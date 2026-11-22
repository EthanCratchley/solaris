"""Parse the firmware's CSV status line (docs/serial.md). Input is untrusted."""

from dataclasses import dataclass

MAX_LINE = 64
STATES = ("tracking", "parked")


@dataclass(frozen=True)
class Status:
    millis: int
    ldr_top: int
    ldr_bottom: int
    ldr_left: int
    ldr_right: int
    pan: int
    tilt: int
    state: str


# (max value) for each numeric column; all have min 0 except tilt.
_RANGES = (
    (0, 2**32 - 1),
    (0, 1023),
    (0, 1023),
    (0, 1023),
    (0, 1023),
    (0, 180),
    (15, 165),
)


def parse(raw: bytes) -> Status | None:
    """Return the status for a valid line, else None."""
    text = raw.decode("ascii", errors="replace").strip()
    if not text or len(text) > MAX_LINE:
        return None
    fields = text.split(",")
    if len(fields) != 8 or fields[7] not in STATES:
        return None
    values = []
    for field, (lo, hi) in zip(fields[:7], _RANGES):
        if not (field.isascii() and field.isdigit()):
            return None
        value = int(field)
        if not lo <= value <= hi:
            return None
        values.append(value)
    return Status(*values, fields[7])
