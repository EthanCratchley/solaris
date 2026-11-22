import math
import sqlite3
from datetime import date, datetime, timedelta, timezone

import pytest

from logger import energy
from logger.power import Power
from logger.store import Store

UTC = timezone.utc
DAY = date(2026, 6, 21)
MIDNIGHT = datetime(2026, 6, 21, tzinfo=UTC).timestamp()
H = 3600.0


def within_1pct(actual, expected):
    assert actual == pytest.approx(expected, rel=0.01)


def constant(watts, start, end, step=1.0):
    n = int(round((end - start) / step))
    return [(start + i * step, watts) for i in range(n + 1)]


def half_sine(peak, start, length, step):
    n = int(round(length / step))
    return [(start + i * step, peak * math.sin(math.pi * i * step / length)) for i in range(n + 1)]


def store_with(curves, volts=10.0):
    s = Store(":memory:")
    for channel, samples in curves.items():
        for ts, watts in samples:
            s.add_power(ts, channel, Power(volts, watts / volts))
    return s


# --- integrate() on plain samples -------------------------------------------------------


def test_constant_power_for_one_hour():
    within_1pct(energy.integrate(constant(10.0, 0, H), 0, H, max_gap=5), 10.0)


def test_half_sine_day_curve():
    # Integral of P sin(pi t / T) over [0, T] is 2 P T / pi.
    samples = half_sine(5.0, 0, 12 * H, step=1.0)
    within_1pct(energy.integrate(samples, 0, 12 * H, max_gap=5), 2 * 5.0 * 12 / math.pi)


def test_ramp_is_exact_with_coarse_samples():
    samples = [(0.0, 0.0), (H, 20.0)]
    assert energy.integrate(samples, 0, H, max_gap=2 * H) == pytest.approx(10.0)


def test_gap_longer_than_max_gap_is_not_bridged():
    samples = constant(10.0, 0, H) + constant(10.0, 2 * H, 3 * H)
    within_1pct(energy.integrate(samples, 0, 3 * H, max_gap=5), 20.0)


def test_gap_equal_to_max_gap_is_bridged():
    samples = [(0.0, 10.0), (5.0, 10.0)]
    assert energy.integrate(samples, 0, 10, max_gap=5) == pytest.approx(50 / H)


def test_window_clips_and_interpolates():
    # Ramp 0 -> 20 W over an hour; the second half holds 3/4 of the energy.
    samples = [(0.0, 0.0), (H, 20.0)]
    assert energy.integrate(samples, H / 2, H, max_gap=2 * H) == pytest.approx(7.5)
    assert energy.integrate(samples, 0, H / 2, max_gap=2 * H) == pytest.approx(2.5)


def test_unsorted_and_duplicate_samples():
    samples = constant(10.0, 0, H)
    shuffled = samples[1::2] + samples[::2] + [samples[10]]
    within_1pct(energy.integrate(shuffled, 0, H, max_gap=5), 10.0)


@pytest.mark.parametrize("samples", [[], [(100.0, 5.0)]])
def test_too_few_samples_is_zero(samples):
    assert energy.integrate(samples, 0, H, max_gap=5) == 0.0


def test_samples_outside_window_are_zero():
    assert energy.integrate(constant(10.0, 2 * H, 3 * H), 0, H, max_gap=5) == 0.0


# --- daily report from the database ------------------------------------------------------


def sunny_day(step=10.0):
    sunrise = MIDNIGHT + 6 * H
    return {
        # Tracker sees more of the sun than the fixed panel.
        "tracker": half_sine(6.0, sunrise, 12 * H, step),
        "fixed": half_sine(4.5, sunrise, 12 * H, step),
        # Servo supply: 0.1 W idle all day plus 2 W while moving, 30 s every 10 min.
        "servo": [
            (MIDNIGHT + t, 2.1 if (t % 600) < 30 else 0.1)
            for t in (i * step for i in range(int(24 * H / step)))  # ends before next midnight
        ],
    }


def test_daily_report_numbers():
    s = store_with(sunny_day())
    r = energy.daily(s.db, DAY, tz=UTC, max_gap=30)
    tracker = 2 * 6.0 * 12 / math.pi
    fixed = 2 * 4.5 * 12 / math.pi
    servo = 0.1 * 24 + 2.0 * 24 * 30 / 600
    within_1pct(r.tracker_wh, tracker)
    within_1pct(r.fixed_wh, fixed)
    within_1pct(r.servo_wh, servo)
    assert r.net_wh == pytest.approx(r.tracker_wh - r.fixed_wh - r.servo_wh)
    within_1pct(r.net_wh, tracker - fixed - servo)
    assert r.day == DAY


def test_net_can_be_negative():
    curves = sunny_day()
    curves["servo"] = constant(1.0, MIDNIGHT, MIDNIGHT + 24 * H, step=10)
    r = energy.daily(store_with(curves).db, DAY, tz=UTC, max_gap=30)
    assert r.net_wh < 0
    within_1pct(r.servo_wh, 24.0)


def test_missing_channel_counts_as_zero():
    curves = sunny_day()
    del curves["servo"]
    r = energy.daily(store_with(curves).db, DAY, tz=UTC, max_gap=30)
    assert r.servo_wh == 0.0
    assert r.net_wh == pytest.approx(r.tracker_wh - r.fixed_wh)


def test_energy_across_midnight_is_split_between_days():
    s = store_with({"servo": constant(6.0, MIDNIGHT - H, MIDNIGHT + H, step=10)})
    before = energy.daily(s.db, DAY - timedelta(days=1), tz=UTC, max_gap=30)
    after = energy.daily(s.db, DAY, tz=UTC, max_gap=30)
    within_1pct(before.servo_wh, 6.0)
    within_1pct(after.servo_wh, 6.0)


def test_timezone_moves_day_boundary():
    s = store_with({"servo": constant(6.0, MIDNIGHT - H, MIDNIGHT + H, step=10)})
    plus_one = timezone(timedelta(hours=1))
    # In UTC+1 the whole 2 h block falls on DAY (local 00:00-02:00).
    within_1pct(energy.daily(s.db, DAY, tz=plus_one, max_gap=30).servo_wh, 12.0)


def test_empty_day():
    r = energy.daily(Store(":memory:").db, DAY, tz=UTC, max_gap=30)
    assert (r.tracker_wh, r.fixed_wh, r.servo_wh, r.net_wh) == (0.0, 0.0, 0.0, 0.0)


def test_all_days_lists_each_day_with_data():
    curves = sunny_day()
    next_day = {k: [(t + 24 * H, w) for t, w in v] for k, v in curves.items()}
    s = store_with({k: curves[k] + next_day[k] for k in curves})
    reports = energy.all_days(s.db, tz=UTC, max_gap=30)
    assert [r.day for r in reports] == [DAY, DAY + timedelta(days=1)]
    within_1pct(reports[1].tracker_wh, 2 * 6.0 * 12 / math.pi)


def test_all_days_empty_db():
    assert energy.all_days(Store(":memory:").db, tz=UTC, max_gap=30) == []


def test_local_time_default_runs():
    s = store_with({"servo": constant(1.0, MIDNIGHT, MIDNIGHT + H, step=10)})
    total = sum(r.servo_wh for r in energy.all_days(s.db, max_gap=30))
    within_1pct(total, 1.0)


def test_cli_prints_csv_report(tmp_path, monkeypatch, capsys):
    path = tmp_path / "solaris.db"
    s = Store(path)
    for t, w in constant(10.0, MIDNIGHT + 12 * H, MIDNIGHT + 13 * H, step=1):
        s.add_power(t, "tracker", Power(10.0, w / 10.0))
    s.close()
    monkeypatch.setattr("sys.argv", ["energy", str(path)])
    energy.main()
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "day,tracker_wh,fixed_wh,servo_wh,net_wh"
    day, tracker, fixed, servo, net = out[1].split(",")
    within_1pct(float(tracker), 10.0)
    assert (float(fixed), float(servo)) == (0.0, 0.0)
    within_1pct(float(net), 10.0)
    assert len(out) == 2


def test_cli_does_not_create_missing_db(tmp_path, monkeypatch):
    path = tmp_path / "missing.db"
    monkeypatch.setattr("sys.argv", ["energy", str(path)])
    with pytest.raises(sqlite3.OperationalError):
        energy.main()
    assert not path.exists()
