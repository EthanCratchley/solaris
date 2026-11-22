# Hardware and environment facts

<!-- Ethan fills this once. Agents read it; they never guess these values. -->

| Thing | Value |
|---|---|
| Board | Arduino Uno R3 (PlatformIO env `uno`) |
| Servos | 2× MG996R (pan, tilt) on a separate 5–6 V supply |
| LDR pins (top, bottom, left, right) | A0, A1, A2, A3 |
| Servo pins (pan, tilt) | D9, D10 |
| Pan limits (°) | 0–180 |
| Tilt limits (°) | 15–165 |
| Deadband / step / move interval | 30 ADC counts / 1° / 50 ms |
| "East" pan angle for night parking | TBD (measure on the mount) |
| Serial port on Pi / baud | /dev/ttyACM0 / 115200 |
| INA219 channels + I²C addresses | tracker 0x40, fixed 0x41, servo supply 0x44 |
| Panels (model, Voc, Isc) | TBD (two identical) |

Photos of wiring go in `docs/hardware/`.
