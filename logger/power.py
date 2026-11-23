"""INA219 power readings behind a small interface, with a fake for tests."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

REG_CONFIG = 0x00
REG_SHUNT = 0x01
REG_BUS = 0x02
# Power-on default: 32 V range, PGA /8 (+/-320 mV shunt), 12-bit, continuous shunt + bus.
CONFIG_DEFAULT = 0x399F


@dataclass(frozen=True)
class Power:
    volts: float
    amps: float

    @property
    def watts(self) -> float:
        return self.volts * self.amps


class PowerSensor(Protocol):
    def read(self) -> Power: ...


class I2CBus(Protocol):
    """The subset of smbus2.SMBus used here."""

    def read_i2c_block_data(self, addr: int, reg: int, length: int) -> list[int]: ...

    def write_i2c_block_data(self, addr: int, reg: int, data: list[int]) -> None: ...


class Ina219:
    """Reads bus voltage and shunt voltage directly; current = shunt V / shunt ohms.

    Avoids the calibration register so the result depends only on the shunt value.
    """

    def __init__(self, bus: I2CBus, address: int, shunt_ohms: float):
        if shunt_ohms <= 0:
            raise ValueError("shunt_ohms must be positive")
        self.bus = bus
        self.address = address
        self.shunt_ohms = shunt_ohms
        bus.write_i2c_block_data(address, REG_CONFIG, [CONFIG_DEFAULT >> 8, CONFIG_DEFAULT & 0xFF])

    def _register(self, reg: int) -> int:
        msb, lsb = self.bus.read_i2c_block_data(self.address, reg, 2)
        return (msb << 8) | lsb

    def read(self) -> Power:
        bus_mv = (self._register(REG_BUS) >> 3) * 4  # low 3 bits are status flags
        shunt = self._register(REG_SHUNT)
        if shunt & 0x8000:
            shunt -= 1 << 16
        shunt_v = shunt * 10e-6
        return Power(bus_mv / 1000, shunt_v / self.shunt_ohms)


class FakeSensor:
    """Returns scripted readings in order; an exception in the script is raised instead."""

    def __init__(self, script: Iterable[Power | Exception]):
        self._script = iter(script)

    def read(self) -> Power:
        item = next(self._script, None)
        if item is None:
            raise OSError("fake sensor: script exhausted")
        if isinstance(item, Exception):
            raise item
        return item
