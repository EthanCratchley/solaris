import pytest

from logger import config
from logger.power import CONFIG_DEFAULT, FakeSensor, Ina219, Power


class FakeBus:
    """In-memory INA219 register file, keyed by (address, register)."""

    def __init__(self, registers):
        self.registers = dict(registers)
        self.writes = []

    def read_i2c_block_data(self, addr, reg, length):
        assert length == 2
        return list(self.registers[(addr, reg)])

    def write_i2c_block_data(self, addr, reg, data):
        self.writes.append((addr, reg, list(data)))


def ina(addr, bus_raw, shunt_raw):
    return {(addr, 0x02): bus_raw, (addr, 0x01): shunt_raw}


def test_config_matches_decisions():
    assert config.CHANNELS == {"tracker": 0x40, "fixed": 0x41, "servo": 0x44}


def test_writes_default_config_on_init():
    bus = FakeBus({})
    Ina219(bus, 0x41, 0.1)
    assert bus.writes == [(0x41, 0x00, [CONFIG_DEFAULT >> 8, CONFIG_DEFAULT & 0xFF])]


def test_converts_bus_and_shunt_registers():
    # 12.000 V -> (12000 mV / 4) << 3 = 0x5DC0; 50 mV shunt -> 5000 * 10 uV = 0x1388.
    bus = FakeBus(ina(0x40, [0x5D, 0xC0], [0x13, 0x88]))
    p = Ina219(bus, 0x40, 0.1).read()
    assert p.volts == pytest.approx(12.0)
    assert p.amps == pytest.approx(0.5)
    assert p.watts == pytest.approx(6.0)


def test_status_bits_in_bus_register_are_ignored():
    bus = FakeBus(ina(0x40, [0x5D, 0xC3], [0x00, 0x00]))  # CNVR and OVF set
    assert Ina219(bus, 0x40, 0.1).read().volts == pytest.approx(12.0)


def test_negative_shunt_is_twos_complement():
    # -10 mV -> -1000 -> 0xFC18
    bus = FakeBus(ina(0x44, [0x00, 0x00], [0xFC, 0x18]))
    assert Ina219(bus, 0x44, 0.1).read().amps == pytest.approx(-0.1)


def test_full_scale_values():
    # Bus max 0xFFF8 -> 8191 * 4 mV = 32.764 V; shunt +320 mV max (32000 = 0x7D00).
    bus = FakeBus(ina(0x40, [0xFF, 0xF8], [0x7D, 0x00]))
    p = Ina219(bus, 0x40, 0.1).read()
    assert p.volts == pytest.approx(32.764)
    assert p.amps == pytest.approx(3.2)


def test_uses_shunt_resistance():
    bus = FakeBus(ina(0x40, [0x5D, 0xC0], [0x13, 0x88]))
    assert Ina219(bus, 0x40, 0.05).read().amps == pytest.approx(1.0)


def test_reads_only_its_own_address():
    bus = FakeBus(ina(0x41, [0x5D, 0xC0], [0x13, 0x88]))
    with pytest.raises(KeyError):
        Ina219(bus, 0x40, 0.1).read()


@pytest.mark.parametrize("ohms", [0, -0.1])
def test_rejects_nonpositive_shunt(ohms):
    with pytest.raises(ValueError):
        Ina219(FakeBus({}), 0x40, ohms)


def test_fake_sensor_replays_then_raises():
    s = FakeSensor([Power(5.0, 0.2), Power(5.1, 0.3)])
    assert s.read() == Power(5.0, 0.2)
    assert s.read().watts == pytest.approx(1.53)
    with pytest.raises(OSError):
        s.read()


def test_fake_sensor_can_inject_errors():
    s = FakeSensor([OSError("i2c nack"), Power(5.0, 0.2)])
    with pytest.raises(OSError, match="nack"):
        s.read()
    assert s.read() == Power(5.0, 0.2)
