"""SQLite storage. Timestamps are Unix seconds (UTC) taken on the Pi."""

import sqlite3
from os import PathLike

from logger.power import Power
from logger.stream import Status

SCHEMA = """
CREATE TABLE IF NOT EXISTS status (
    id INTEGER PRIMARY KEY,
    ts REAL NOT NULL,
    millis INTEGER NOT NULL,
    ldr_top INTEGER NOT NULL,
    ldr_bottom INTEGER NOT NULL,
    ldr_left INTEGER NOT NULL,
    ldr_right INTEGER NOT NULL,
    pan INTEGER NOT NULL,
    tilt INTEGER NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('tracking', 'parked'))
);
CREATE TABLE IF NOT EXISTS power (
    id INTEGER PRIMARY KEY,
    ts REAL NOT NULL,
    channel TEXT NOT NULL CHECK (channel IN ('tracker', 'fixed', 'servo')),
    volts REAL NOT NULL,
    amps REAL NOT NULL,
    watts REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS status_ts ON status (ts);
CREATE INDEX IF NOT EXISTS power_channel_ts ON power (channel, ts);
"""


class Store:
    def __init__(self, path: str | PathLike[str]):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA journal_mode=WAL")  # lets the dashboard read while we write
        self.db.executescript(SCHEMA)

    def add_status(self, ts: float, s: Status) -> None:
        with self.db:
            self.db.execute(
                "INSERT INTO status (ts, millis, ldr_top, ldr_bottom, ldr_left, ldr_right,"
                " pan, tilt, state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (ts, s.millis, s.ldr_top, s.ldr_bottom, s.ldr_left, s.ldr_right, s.pan, s.tilt,
                 s.state),
            )

    def add_power(self, ts: float, channel: str, p: Power) -> None:
        with self.db:
            self.db.execute(
                "INSERT INTO power (ts, channel, volts, amps, watts) VALUES (?, ?, ?, ?, ?)",
                (ts, channel, p.volts, p.amps, p.watts),
            )

    def close(self) -> None:
        self.db.close()
