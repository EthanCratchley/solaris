# Progress

<!-- Agents append one entry per task, newest first. -->

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
