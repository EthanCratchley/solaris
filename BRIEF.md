# solaris — brief

## Goal
A two-axis solar tracker (Arduino Uno, 4 LDRs, 2 MG996R servos) plus a Raspberry Pi
logger that measures a tracking panel against an identical fixed panel and the servo
supply, to answer with real data: **is a small tracker net positive?** The answer is a
daily energy number: tracker panel Wh − fixed panel Wh − servo Wh.

## Out of scope (for now)
- Uploading firmware to the board or anything that needs the hardware wired (Ethan does that).
- GPS / sun-position tracking, wireless links, cloud dashboards.

## Milestones
Big checkpoints only (see CLAUDE.md step 7). Also check in early on a major change, a
major fix, or a major blocker.

- M1: F1–F4 — firmware builds and passes native tests.
- M2: L1–L3 — Pi logger, energy report and dashboard.

## Tasks
Each task: id, what to do, done check. Agents take them in order.

- [x] F1: Tracking logic as a pure C++ library (`lib/tracker/`): LDR pairs → pan/tilt step with deadband, angle limits, step size.
      Done when: `pio test -e native` passes tests for each direction, the deadband, and clamping at both limits.
- [x] F2: `src/main.cpp`: read 4 LDRs, apply F1, drive servos, detach servos between moves; pins and limits from one config header that matches HARDWARE.md.
      Done when: `pio run` builds for `uno`; a native test checks that no command outside the HARDWARE.md limits can be produced.
- [ ] F3: Night parking: when all LDRs are below the dark threshold for N minutes, park facing east; resume at dawn.
      Done when: native tests simulate dusk → night → dawn and check parking and resuming (with hysteresis).
- [ ] F4: Serial output: one CSV line per interval (documented in `docs/serial.md`): millis, 4 LDR values, pan, tilt, state.
      Done when: native test checks line format; the format doc matches the test.
- [ ] L1: Pi logger (`logger/`): read the serial stream and INA219 readings into SQLite; INA219 behind an interface with a fake for tests.
      Done when: `logger/tests` replay a recorded/simulated serial stream and fake INA219 data and check the SQLite rows.
- [ ] L2: Daily energy report: integrate power to Wh per channel and compute net gain.
      Done when: tests with synthetic power curves check the Wh numbers to within 1%.
- [ ] L3: Streamlit page: live angles, today's Wh per channel, net gain over days.
      Done when: the page imports and renders against a fixture DB in a smoke test.

Hardware to buy is in agent-hq HUMAN-TASKS.md.
