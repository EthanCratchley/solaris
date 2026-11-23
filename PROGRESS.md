# Progress

<!-- Agents append one entry per task, newest first. -->

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
