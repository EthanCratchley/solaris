import logging
import sqlite3
from pathlib import Path

import pytest

from logger import app
from logger.power import FakeSensor, Power
from logger.store import Store

STREAM = Path(__file__).parent / "fixtures" / "serial_stream.bin"


def lines():
    return STREAM.read_bytes().split(b"\n")


def clock(start=1_700_000_000.0, step=0.5):
    t = start
    while True:
        yield t
        t += step


def sensors(n=20):
    return {
        "tracker": FakeSensor([Power(18.0 + i * 0.01, 0.30) for i in range(n)]),
        "fixed": FakeSensor([Power(17.5, 0.20 + i * 0.001) for i in range(n)]),
        "servo": FakeSensor([Power(5.0, 0.05) for _ in range(n)]),
    }


@pytest.fixture
def store():
    s = Store(":memory:")
    yield s
    s.close()


def test_replay_stores_only_valid_status_lines(store):
    log = app.Logger(store, sensors(), power_interval=1.0)
    app.replay(lines(), clock().__next__, log)
    rows = store.db.execute(
        "SELECT ts, millis, ldr_top, ldr_bottom, ldr_left, ldr_right, pan, tilt, state"
        " FROM status ORDER BY id"
    ).fetchall()
    t0 = 1_700_000_000.0
    assert rows == [
        (t0 + 0.5, 1000, 512, 498, 601, 587, 93, 120, "tracking"),
        (t0 + 1.5, 2000, 520, 500, 590, 600, 93, 120, "tracking"),
        (t0 + 3.5, 6000, 40, 30, 20, 10, 0, 90, "parked"),
        (t0 + 5.0, 4294967295, 1023, 0, 1023, 0, 180, 165, "tracking"),
    ]
    assert log.rejected == 8  # empty line is not counted


def test_replay_samples_every_channel_at_the_power_interval(store):
    log = app.Logger(store, sensors(), power_interval=1.0)
    app.replay(lines(), clock().__next__, log)
    rows = store.db.execute(
        "SELECT ts, channel, volts, amps, watts FROM power ORDER BY id"
    ).fetchall()
    # 13 lines at 0.5 s -> t = 0 .. 6.0; samples at t = 0, 1, ..., 6.
    t0 = 1_700_000_000.0
    times = sorted({r[0] for r in rows})
    assert times == [t0 + i for i in range(7)]
    for t in times:
        assert sorted(r[1] for r in rows if r[0] == t) == ["fixed", "servo", "tracker"]
    first = {r[1]: r[2:] for r in rows if r[0] == t0}
    assert first["tracker"] == pytest.approx((18.0, 0.30, 5.4))
    assert first["fixed"] == pytest.approx((17.5, 0.20, 3.5))
    assert first["servo"] == pytest.approx((5.0, 0.05, 0.25))
    last_tracker = [r for r in rows if r[1] == "tracker"][-1]
    assert last_tracker[2] == pytest.approx(18.06)


def test_failed_sensor_read_skips_that_channel_and_warns(store, caplog):
    flaky = sensors()
    flaky["servo"] = FakeSensor([OSError("i2c nack"), Power(5.0, 0.05)])
    log = app.Logger(store, flaky, power_interval=1.0)
    with caplog.at_level(logging.WARNING):
        log.sample(100.0)
        log.sample(101.0)
    rows = store.db.execute("SELECT ts, channel FROM power ORDER BY id").fetchall()
    assert rows == [
        (100.0, "tracker"),
        (100.0, "fixed"),
        (101.0, "tracker"),
        (101.0, "fixed"),
        (101.0, "servo"),
    ]
    assert "servo" in caplog.text and "i2c nack" in caplog.text


def test_sample_waits_for_interval(store):
    log = app.Logger(store, sensors(), power_interval=1.0)
    for t in (10.0, 10.4, 10.99, 11.0, 11.5, 12.2):
        log.sample(t)
    times = [r[0] for r in store.db.execute("SELECT DISTINCT ts FROM power ORDER BY ts")]
    assert times == [10.0, 11.0, 12.2]


def test_rejected_line_is_logged_without_raw_bytes_flooding(store, caplog):
    log = app.Logger(store, {}, power_interval=1.0)
    with caplog.at_level(logging.WARNING):
        assert log.line(b"x" * 500, 1.0) is False
    assert log.rejected == 1
    assert len(caplog.text) < 300


def test_schema_rejects_bad_channel_and_state(store):
    with pytest.raises(sqlite3.IntegrityError):
        store.db.execute(
            "INSERT INTO power (ts, channel, volts, amps, watts) VALUES (1, 'solar', 1, 1, 1)"
        )
    with pytest.raises(sqlite3.IntegrityError):
        store.db.execute(
            "INSERT INTO status (ts, millis, ldr_top, ldr_bottom, ldr_left, ldr_right,"
            " pan, tilt, state) VALUES (1, 1, 1, 1, 1, 1, 1, 60, 'asleep')"
        )


def test_store_persists_to_file(tmp_path):
    path = tmp_path / "solaris.db"
    s = Store(path)
    app.Logger(s, sensors(), power_interval=1.0).line(b"1,2,3,4,5,6,60,tracking", 1.0)
    s.close()
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT millis FROM status").fetchall() == [(1,)]
        assert db.execute("PRAGMA journal_mode").fetchone() == ("wal",)


def test_main_requires_serial_port_env(monkeypatch):
    monkeypatch.delenv("SOLARIS_SERIAL_PORT", raising=False)
    with pytest.raises(SystemExit, match="SOLARIS_SERIAL_PORT"):
        app.main()
