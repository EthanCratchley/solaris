import time
from datetime import date, datetime, time as clock, timedelta
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from logger import energy
from logger.power import Power
from logger.store import Store
from logger.stream import Status

PAGE = str(Path(__file__).resolve().parents[1] / "dashboard.py")
TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)


def at_local(day, hour):
    return datetime.combine(day, clock(hour)).timestamp()


def add_constant(store, channel, watts, start, hours, step=5.0, volts=10.0):
    for i in range(int(hours * 3600 / step) + 1):
        store.add_power(start + i * step, channel, Power(volts, watts / volts))


@pytest.fixture
def fixture_db(tmp_path):
    """Synthetic DB: two days of power and a few recent status lines."""
    path = tmp_path / "solaris.db"
    store = Store(path)
    # Yesterday: tracker 2 h at 10 W, fixed at 9 W, servo 0.5 W -> net 1 Wh.
    # Today:     tracker 2 h at 10 W, fixed at 8 W, servo 0.5 W -> net 3 Wh.
    for day, fixed in ((YESTERDAY, 9.0), (TODAY, 8.0)):
        start = at_local(day, 8)
        add_constant(store, "tracker", 10.0, start, 2)
        add_constant(store, "fixed", fixed, start, 2)
        add_constant(store, "servo", 0.5, start, 2)
    now = time.time()
    for i, (pan, tilt) in enumerate([(80, 60), (81, 61), (82, 62)]):
        store.add_status(now - 30 + i * 10, Status(1000 * i, 500, 480, 470, 520, pan, tilt,
                                                   "tracking"))
    store.close()
    return path


def run(monkeypatch, path):
    monkeypatch.setenv("SOLARIS_DB", str(path))
    at = AppTest.from_file(PAGE, default_timeout=30)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def metrics(at):
    return {m.label: m.value for m in at.metric}


def test_renders_live_angles_today_and_days(monkeypatch, fixture_db):
    at = run(monkeypatch, fixture_db)
    m = metrics(at)
    assert m["Pan"] == "82°"
    assert m["Tilt"] == "62°"
    assert m["State"] == "tracking"
    assert m["Tracker"] == "20.00 Wh"
    assert m["Fixed"] == "16.00 Wh"
    assert m["Servo"] == "1.00 Wh"
    assert m["Net gain"] == "3.00 Wh"
    assert not at.error and not at.info

    table = at.dataframe[0].value
    assert list(table.day) == [YESTERDAY.isoformat(), TODAY.isoformat()]
    assert list(table.net_wh) == pytest.approx([1.0, 3.0], rel=0.01)


def test_today_matches_energy_report(monkeypatch, fixture_db):
    import sqlite3

    with sqlite3.connect(fixture_db) as db:
        report = energy.daily(db, TODAY)
    m = metrics(run(monkeypatch, fixture_db))
    assert m["Net gain"] == f"{report.net_wh:.2f} Wh"


def test_shows_parked_state(monkeypatch, fixture_db):
    store = Store(fixture_db)
    store.add_status(time.time(), Status(5000, 10, 10, 10, 10, 0, 90, "parked"))
    store.close()
    m = metrics(run(monkeypatch, fixture_db))
    assert (m["Pan"], m["Tilt"], m["State"]) == ("0°", "90°", "parked")


def test_empty_db_shows_placeholders(monkeypatch, tmp_path):
    path = tmp_path / "empty.db"
    Store(path).close()
    at = run(monkeypatch, path)
    assert [i.value for i in at.info] == ["No tracker status yet.", "No power samples yet."]
    m = metrics(at)
    assert "Pan" not in m
    assert m["Net gain"] == "0.00 Wh"


def test_missing_db_shows_error_without_creating_file(monkeypatch, tmp_path):
    path = tmp_path / "missing.db"
    at = run(monkeypatch, path)
    assert len(at.error) == 1
    assert not at.metric
    assert not path.exists()


def test_db_path_with_uri_characters_is_opened_as_a_file(monkeypatch, tmp_path, fixture_db):
    odd = tmp_path / "a?mode=rwc#x.db"
    fixture_db.rename(odd)
    assert metrics(run(monkeypatch, odd))["Net gain"] == "3.00 Wh"


def test_page_does_not_write_to_db(monkeypatch, fixture_db):
    before = fixture_db.read_bytes()
    run(monkeypatch, fixture_db)
    assert fixture_db.read_bytes() == before
