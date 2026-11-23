# Progress

<!-- Agents append one entry per task, newest first. -->

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
