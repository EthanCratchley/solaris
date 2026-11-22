"""Read the tracker's serial stream and the INA219s into SQLite.

Run on the Pi: SOLARIS_SERIAL_PORT=/dev/ttyACM0 python -m logger.app
"""

import logging
import os
import time
from collections.abc import Callable, Iterable, Mapping

from logger import config
from logger.power import Ina219, PowerSensor
from logger.store import Store
from logger.stream import parse

log = logging.getLogger("solaris.logger")


class Logger:
    def __init__(self, store: Store, sensors: Mapping[str, PowerSensor], power_interval: float):
        self.store = store
        self.sensors = sensors
        self.power_interval = power_interval
        self.sampled_at: float | None = None
        self.rejected = 0

    def line(self, raw: bytes, now: float) -> bool:
        """Store one serial line if valid. Blank lines are ignored without counting."""
        if not raw.strip():
            return False
        status = parse(raw)
        if status is None:
            self.rejected += 1
            log.warning("rejected serial line (%d bytes): %r", len(raw), raw[:40])
            return False
        self.store.add_status(now, status)
        return True

    def sample(self, now: float) -> None:
        """Read every power channel if the interval has elapsed."""
        if self.sampled_at is not None and now - self.sampled_at < self.power_interval:
            return
        self.sampled_at = now
        for channel, sensor in self.sensors.items():
            try:
                reading = sensor.read()
            except OSError as e:  # transient I2C errors: skip this sample, keep logging
                log.warning("power read failed on %s: %s", channel, e)
                continue
            self.store.add_power(now, channel, reading)


def replay(lines: Iterable[bytes], clock: Callable[[], float], logger: Logger) -> None:
    for raw in lines:
        now = clock()
        logger.line(raw, now)
        logger.sample(now)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    port = os.environ.get("SOLARIS_SERIAL_PORT")
    if not port:
        raise SystemExit("SOLARIS_SERIAL_PORT is not set (e.g. /dev/ttyACM0)")
    # Hardware libraries are only needed on the Pi.
    import serial
    import smbus2

    db = os.environ.get("SOLARIS_DB", config.DEFAULT_DB)
    store = Store(db)
    bus = smbus2.SMBus(config.I2C_BUS)
    sensors = {name: Ina219(bus, addr, config.SHUNT_OHMS) for name, addr in config.CHANNELS.items()}
    logger = Logger(store, sensors, config.POWER_INTERVAL_S)
    # timeout=1 makes readline return b"" each second, so power sampling continues even
    # when the board is silent.
    with serial.Serial(port, config.BAUD, timeout=1) as stream:
        log.info("logging %s to %s", port, db)
        replay(iter(stream.readline, None), time.time, logger)


if __name__ == "__main__":
    main()
