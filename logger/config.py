"""Logger settings. Values must match HARDWARE.md / DECISIONS.md."""

# INA219 I2C addresses per channel.
CHANNELS = {"tracker": 0x40, "fixed": 0x41, "servo": 0x44}

# TODO(QUESTIONS.md L1): 0.1 ohm is the usual INA219 breakout shunt; confirm on the boards.
SHUNT_OHMS = 0.1

I2C_BUS = 1  # Raspberry Pi header I2C
BAUD = 115200
POWER_INTERVAL_S = 1.0
DEFAULT_DB = "solaris.db"
# Power samples further apart than this are not bridged when integrating (logger was down).
MAX_GAP_S = 5.0
