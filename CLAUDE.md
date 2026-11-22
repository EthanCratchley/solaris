# solaris — rules for coding agents

Goal: firmware for a two-axis LDR solar tracker (Arduino Uno, PlatformIO) and a
Raspberry Pi logger that records tracker, fixed-panel and servo-supply power into
SQLite, so we can measure whether a small tracker is net positive. Finished means F1–F4
and L1–L3 in `BRIEF.md` are ticked with tests passing in `./check.sh`. This repo is
**public**.

Read this file, then `BRIEF.md`, `PROGRESS.md`, `DECISIONS.md` and `HARDWARE.md` before
doing anything.

## How you work

1. Take the first unchecked task in `BRIEF.md`.
2. Create a branch `loop/<task-id>-<short-name>` from the latest `main`.
3. Make the change. Keep the diff small; don't reformat code you aren't changing.
4. Run `./check.sh` until it passes. Done means it passes, not that it looks right.
5. Update `PROGRESS.md` (what changed, what's next, anything surprising), tick the task in
   `BRIEF.md`, commit, push the branch, open a PR titled `<task-id>: <summary>`.
6. Continue with the next task. There is no task cap.
7. **Milestone check-in.** A milestone is something big: a finished feature (the milestones
   listed in `BRIEF.md`), a major change or fix, or a major blocker (nothing left you can
   move forward on). Small gaps are not milestones: log them in `QUESTIONS.md` and keep
   going. At a milestone, add a `## Milestone check-in — <what>` entry to `PROGRESS.md`
   (what works now, PRs to review, open questions, what's next), then stop until Ethan says
   continue. Also stop when every task is ticked.

## If you are missing something

Never stop and wait. Write it to `QUESTIONS.md` (task id, what you need, why, what you did
instead), then do the next task or stub the missing piece behind a clear TODO.

## These rules win

Where this file conflicts with Ethan's global `~/.claude/CLAUDE.md`, follow this file. In
particular, in this repo:
- Don't stop to confirm understanding or ask before acting. Follow the loop; put questions
  in `QUESTIONS.md`.
- Fakes, stubs and recorded responses are the intended way to test hardware and external
  APIs. The global "avoid mocks" rule doesn't apply.
- No coverage target. The done checks in `BRIEF.md` define enough testing.

## Never

- Commit to `main`, force-push, or merge your own PR.
- Print, log, or commit secrets, or put them in PR text. You may read `.env` and
  `.env.example` to use configuration, but never echo the values. Keys live in `.env`
  (gitignored) or the macOS Keychain; `.env.example` lists names only.
- Commit real personal data. Fixtures are synthetic or scrubbed. This repo is public:
  no hostnames, IPs, home location or names in committed files.
- Weaken or delete a test or check to make `./check.sh` pass.
- Exceed the limits in `HARDWARE.md`, or flash firmware onto a commercial device.
- Run `pio run -t upload` or talk to a real serial port. Ethan uploads.
- Leave servos attached and powered while idle, or command an angle outside the configured limits.

## Commands

- Check: `./check.sh`
- Build: `pio run`
- Firmware tests: `pio test -e native`
- Logger tests: `.venv/bin/python -m pytest -q logger/tests`
