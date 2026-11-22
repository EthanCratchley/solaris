# Decisions

<!-- Every answer Ethan gives goes here so no agent asks twice. -->

- 2026-11-21: PlatformIO Core is installed on the Mac (Homebrew). `check.sh` builds firmware and runs `pio test -e native` once `test/native` exists.
- 2026-11-21: Logger tests run in the repo `.venv` with pytest.
- 2026-11-21: CI: GitHub Actions runs `./check.sh` on every PR (PlatformIO installed via pip in CI).
- 2026-11-21: Pins: LDR A0 top, A1 bottom, A2 left, A3 right; servo pan D9, tilt D10.
- 2026-11-21: Limits: pan 0–180°, tilt 15–165°, deadband 30 ADC counts, 1° steps, one move every 50 ms. Servos detached between moves.
- 2026-11-21: Night: all LDRs < 50 for 10 min → park facing east; resume when any LDR > 100 (hysteresis). East pan angle is TBD (Ethan measures); use 0° as a placeholder constant marked TODO.
- 2026-11-21: Serial: 115200 baud, one CSV line per second, format documented in `docs/serial.md`.
- 2026-11-21: Power: **3× INA219** — tracker panel 0x40, fixed panel 0x41, servo supply 0x44.
- 2026-11-21: Logger runs on the Pi in Docker; serial port `/dev/ttyACM0` (from env `SOLARIS_SERIAL_PORT`).
- 2026-11-21: Licence: MIT (add `LICENSE` in the first PR that needs it; copyright "Ethan Cratchley").
- 2026-11-21: Panel model and servo supply are TBD (Ethan buys parts); code takes them from config.
