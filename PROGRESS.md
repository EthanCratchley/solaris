# Progress

<!-- Agents append one entry per task, newest first. -->

## Milestone check-in — M2 (L1–L3: Pi logger, energy report, dashboard)
- Works now: every task in BRIEF.md is ticked. Firmware (F1–F4) builds for `uno` and passes
  45 native tests; the logger records serial status + 3× INA219 into SQLite, `logger.energy`
  reports daily Wh and net gain, and `logger/dashboard.py` shows it live. `./check.sh`: 74
  pytest + 45 native tests pass.
- PRs to review: L3 (this one). Earlier PRs #2, #4–#7, #10 are merged.
- Open questions (QUESTIONS.md): servo direction on the mount (F1), park tilt + measured east
  pan angle (F3), INA219 shunt value (L1), servo-channel current range (L1), `SOLARIS_DB` in
  `.env.example` (L1).
- Next: nothing left in BRIEF.md. Likely follow-ups once hardware is wired: a Dockerfile /
  compose for the Pi (logger + dashboard), real calibration values, a first field run.

## 2026-11-23 — L3
- Changed: `logger/dashboard.py` Streamlit page (`python -m streamlit run logger/dashboard.py`
  from the repo root; DB from `SOLARIS_DB`, opened read-only via a percent-escaped
  `file:` URI). Live section (latest pan/tilt/state/age, last-hour angle chart, today's Wh
  per channel and net) refreshes every 5 s as an `st.fragment`; net gain over days is a bar
  chart + table from `energy.all_days`. Missing DB → error, no file created; empty DB →
  placeholders. `test_dashboard.py` (7 tests, `streamlit.testing.v1.AppTest`) renders it
  against a synthetic fixture DB and checks metric values, the days table, parked state,
  empty/missing DB, URI characters in the path, and that the page never writes the DB.
- Next: milestone M2 — all tasks ticked.
- Surprises / notes: `smbus2==0.5.1` (pinned in L1) doesn't exist on PyPI — the pin was never
  installed anywhere. Fixed to `0.5.0`. CI now installs `logger/requirements.txt` (streamlit
  1.66.1 pinned); `pip-audit` reports no known vulnerabilities.

## 2026-11-21 — L2
- Changed: `logger/energy.py`: `integrate` (trapezoidal Wh over a window; segments longer
  than `MAX_GAP_S` = 5 s are not bridged; segments crossing midnight are cut by linear
  interpolation), `daily(db, day)` → `Report(tracker_wh, fixed_wh, servo_wh, net_wh)` with
  net = tracker − fixed − servo, `all_days(db)`, and a read-only CLI
  `python -m logger.energy [db]` printing CSV. Days are the Pi's local calendar days
  (DST-aware) unless a `tz` is passed — no timezone committed. 21 tests with synthetic
  curves (constant, half-sine day, ramps, servo duty cycle, gaps, midnight split, timezone
  shift, negative net, missing channel, CLI) check Wh to within 1%.
- Next: L3 — Streamlit page (live angles, today's Wh, net gain over days).
- Surprises / notes: `all_days` lists every calendar day from first to last sample, so a
  lone sample at 00:00:00 creates a (near-zero) day — my first fixture tripped on this.
  Negative INA219 noise at night is integrated as-is (≈ 0 net). Stacked on L1.

## 2026-11-21 — L1
- Changed: `logger/` package. `stream.parse` validates each serial line strictly (8 fields,
  ASCII digits only, ranges from docs/serial.md/HARDWARE.md, ≤ 64 chars) → `Status` or None.
  `power.py`: `PowerSensor` protocol, `Ina219` (reads bus 0x02 / shunt 0x01 registers via an
  injected smbus2-style bus, writes the default config on init, current = shunt V / ohms),
  `FakeSensor` (scripted readings/exceptions). `store.py`: SQLite `status` and `power` tables
  (CHECK constraints, WAL, parameterised inserts, `ts` = Pi Unix seconds). `app.py`:
  `Logger.line` / `Logger.sample` (1 s interval, an `OSError` on one channel is warned and
  skipped), `replay`, and `main()` (env `SOLARIS_SERIAL_PORT`, optional `SOLARIS_DB`; pyserial
  and smbus2 imported lazily, pinned in `logger/requirements.txt`). 46 pytest tests replay a
  synthetic CRLF stream with garbage/partial/out-of-range lines and fake INA219s, and check
  the SQLite rows.
- Next: L2 — daily Wh per channel + net gain from the `power` table.
- Surprises / notes: no Dockerfile yet (not in L1's done check). `.env.example` is
  read-denied to agents, so `SOLARIS_DB` isn't listed there (QUESTIONS.md). Fixture is
  binary (`.gitattributes -text`) to keep CRLF and invalid bytes intact. Stacked on F4.

## 2026-11-21 — F4
- Changed: `lib/tracker/report.{h,cpp}`: `report::format` writes one CSV line
  `millis,ldr_top,ldr_bottom,ldr_left,ldr_right,pan,tilt,state` with `snprintf` (no
  `String`), returns 0 and empties the buffer if it does not fit. `docs/serial.md` documents
  columns, ranges, 115200 baud, `\r\n` endings. `main.cpp` now reads LDRs every loop and
  prints a line every 1000 ms (`config::BAUD`, `config::REPORT_INTERVAL_MS`).
  `test_report` (8 tests) checks exact lines, widest line, truncation/exact-fit, and reads
  `docs/serial.md` to confirm its header and example lines match the formatter.
- Next: L1 — Pi logger parsing this format.
- Surprises / notes: `LINE_MAX` collides with a POSIX `<limits.h>` macro → named
  `LINE_SIZE`. Native env gets `-D PROJECT_DIR` so the test can open the doc. RAM went
  66 → 296 B (Serial buffers). Stacked on `loop/F3-night-parking`.

## 2026-11-21 — F3
- Changed: `lib/tracker/night.{h,cpp}`: pure `night::update` state machine (Tracking/Parked).
  Parks after all LDRs < 50 continuously for 10 min (any LDR ≥ 50 restarts the timer);
  resumes when any LDR > 100, stays parked in the 50–100 band. Unsigned millis maths, so
  wraparound is safe. `tracker::toward` moves one step per interval toward a target (clamped,
  no overshoot) so parking is a gentle sweep, not a 180° jump. `config::NIGHT`, `config::PARK`
  added; `main.cpp` picks `toward(PARK)` vs `step` from the night state. `test_night`: 16 tests
  incl. thresholds, hysteresis, timer reset, wraparound and a dusk → night → dawn simulation.
- Next: F4 — serial CSV output + `docs/serial.md` (state column can use `night::State`).
- Surprises / notes: park pan 0° and park tilt 90° are TODO placeholders (east not measured;
  tilt not specified) — in QUESTIONS.md. Stacked on `loop/F2-firmware-main`.

## 2026-11-21 — F2
- Changed: `include/config.h` holds all firmware settings (pins, limits, deadband, step,
  50 ms move interval, 40 ms settle, start 90/90). `src/main.cpp` reads the 4 LDRs, applies
  `tracker::step` at most every 50 ms, clamps again before `Servo::write`, writes *before*
  attach (avoids the library's 90° jump), detaches 40 ms after each write, so servos are
  always detached between moves and while idle. `arduino-libraries/Servo@1.2.2` pinned for
  `uno`. `test/native/test_config`: config equals HARDWARE.md values, settle < interval, and
  an exhaustive sweep (start angles −20..200, LDR levels incl. deadband edges) never yields a
  command outside 0–180 / 15–165.
- Next: F3 — night parking.
- Surprises / notes: Servo is not bundled with the PlatformIO AVR framework. Branch is
  stacked on `loop/F1-tracking-lib` (needs `lib/tracker`, F1 not merged yet); PR targets that
  branch and GitHub retargets to `main` when #2 merges. Startup does one blocking 1 s settle
  to move from an unknown power-on angle to 90/90.

## 2026-11-21 — F1
- Changed: `lib/tracker/` pure C++ tracking step (`tracker::step`, `tracker::clamp`): compares
  top/bottom and right/left LDR pairs, moves one `step` per axis when the difference exceeds
  `deadband` (strictly greater), clamps to pan/tilt limits (also clamps an out-of-range start).
  Added `[env:native]` (Unity, `-Werror`) with `test/native/test_tracker` (16 tests);
  `default_envs = uno` so `pio run` still only builds firmware.
- Next: F2 — `src/main.cpp` + config header from HARDWARE.md.
- Surprises / notes: direction convention is an assumption (right brighter → pan angle up,
  top brighter → tilt angle up); logged in QUESTIONS.md since it depends on the mount.

## <date> — <task-id>
- Changed:
- Next:
- Surprises / notes:
