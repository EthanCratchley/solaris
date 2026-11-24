"""Streamlit page: live angles, today's Wh per channel, net gain over days.

Run on the Pi from the repo root: python -m streamlit run logger/dashboard.py
Reads SOLARIS_DB (default solaris.db) read-only, so it can run beside the logger.
"""

import os
import sqlite3
import time
from contextlib import closing
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from logger import config, energy

REFRESH_S = 5
HISTORY_S = 3600


def connect(path: Path) -> sqlite3.Connection:
    # as_uri() percent-escapes the path, so "?" or "#" in it can't inject URI options.
    return sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)


def wh(x: float) -> str:
    return f"{x:.2f} Wh"


@st.fragment(run_every=REFRESH_S)
def live(path: Path) -> None:
    with closing(connect(path)) as db:
        latest = db.execute(
            "SELECT ts, pan, tilt, state FROM status ORDER BY ts DESC LIMIT 1").fetchone()
        history = db.execute(
            "SELECT ts, pan, tilt FROM status WHERE ts >= ? ORDER BY ts",
            (time.time() - HISTORY_S,)).fetchall()
        today = energy.daily(db, date.today())

    st.subheader("Live")
    if latest is None:
        st.info("No tracker status yet.")
    else:
        ts, pan, tilt, state = latest
        cols = st.columns(4)
        cols[0].metric("Pan", f"{pan}°")
        cols[1].metric("Tilt", f"{tilt}°")
        cols[2].metric("State", state)
        cols[3].metric("Last update", f"{max(0.0, time.time() - ts):.0f} s ago")
    if history:
        frame = pd.DataFrame(history, columns=["ts", "pan", "tilt"])
        frame["time"] = [datetime.fromtimestamp(t) for t in frame.ts]
        st.line_chart(frame, x="time", y=["pan", "tilt"])

    st.subheader(f"Today ({today.day})")
    cols = st.columns(4)
    cols[0].metric("Tracker", wh(today.tracker_wh))
    cols[1].metric("Fixed", wh(today.fixed_wh))
    cols[2].metric("Servo", wh(today.servo_wh))
    cols[3].metric("Net gain", wh(today.net_wh))


def days(path: Path) -> None:
    with closing(connect(path)) as db:
        reports = energy.all_days(db)

    st.subheader("Net gain over days")
    if not reports:
        st.info("No power samples yet.")
        return
    frame = pd.DataFrame(
        [(r.day.isoformat(), r.tracker_wh, r.fixed_wh, r.servo_wh, r.net_wh) for r in reports],
        columns=["day", "tracker_wh", "fixed_wh", "servo_wh", "net_wh"])
    st.bar_chart(frame, x="day", y="net_wh")
    st.dataframe(frame, hide_index=True)


st.set_page_config(page_title="solaris", layout="wide")
st.title("solaris tracker")
db = Path(os.environ.get("SOLARIS_DB", config.DEFAULT_DB))
if not db.is_file():
    st.error("No database found. Set SOLARIS_DB to the logger's SQLite file.")
    st.stop()
live(db)
days(db)
