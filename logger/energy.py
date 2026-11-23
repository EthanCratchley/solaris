"""Daily energy per channel and the tracker's net gain.

net = tracker Wh - fixed Wh - servo Wh. Days are local calendar days (the Pi's timezone
unless `tz` is given). Usage: python -m logger.energy [path/to/solaris.db]
"""

import sqlite3
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, tzinfo

from logger import config


@dataclass(frozen=True)
class Report:
    day: date
    tracker_wh: float
    fixed_wh: float
    servo_wh: float

    @property
    def net_wh(self) -> float:
        return self.tracker_wh - self.fixed_wh - self.servo_wh


def integrate(samples: Iterable[tuple[float, float]], start: float, end: float,
              max_gap: float) -> float:
    """Wh in [start, end) from (unix seconds, watts) samples, trapezoidal.

    Segments longer than `max_gap` are skipped rather than interpolated; segments that
    cross the window edge are cut at the edge by linear interpolation.
    """
    points = sorted(samples)
    joules = 0.0
    for (t0, w0), (t1, w1) in zip(points, points[1:]):
        if t1 <= t0 or t1 - t0 > max_gap:
            continue
        a, b = max(t0, start), min(t1, end)
        if b <= a:
            continue
        slope = (w1 - w0) / (t1 - t0)
        joules += (w0 + slope * (a - t0) + w0 + slope * (b - t0)) / 2 * (b - a)
    return joules / 3600


def _bounds(day: date, tz: tzinfo | None) -> tuple[float, float]:
    # A naive datetime's timestamp() uses local time, DST included.
    start = datetime.combine(day, time(), tzinfo=tz)
    end = datetime.combine(day + timedelta(days=1), time(), tzinfo=tz)
    return start.timestamp(), end.timestamp()


def _channel_wh(db: sqlite3.Connection, channel: str, start: float, end: float,
                max_gap: float) -> float:
    rows = db.execute(
        "SELECT ts, watts FROM power WHERE channel = ? AND ts >= ? AND ts <= ? ORDER BY ts",
        (channel, start - max_gap, end + max_gap),
    ).fetchall()
    return integrate(rows, start, end, max_gap)


def daily(db: sqlite3.Connection, day: date, tz: tzinfo | None = None,
          max_gap: float = config.MAX_GAP_S) -> Report:
    start, end = _bounds(day, tz)
    wh = {c: _channel_wh(db, c, start, end, max_gap) for c in config.CHANNELS}
    return Report(day, wh["tracker"], wh["fixed"], wh["servo"])


def all_days(db: sqlite3.Connection, tz: tzinfo | None = None,
             max_gap: float = config.MAX_GAP_S) -> list[Report]:
    """One report per calendar day from the first to the last power sample."""
    first, last = db.execute("SELECT MIN(ts), MAX(ts) FROM power").fetchone()
    if first is None:
        return []
    day = datetime.fromtimestamp(first, tz).date()
    end = datetime.fromtimestamp(last, tz).date()
    reports = []
    while day <= end:
        reports.append(daily(db, day, tz, max_gap))
        day += timedelta(days=1)
    return reports


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else config.DEFAULT_DB
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
        print("day,tracker_wh,fixed_wh,servo_wh,net_wh")
        for r in all_days(db):
            print(f"{r.day},{r.tracker_wh:.3f},{r.fixed_wh:.3f},{r.servo_wh:.3f},{r.net_wh:.3f}")


if __name__ == "__main__":
    main()
