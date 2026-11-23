# Questions for Ethan

<!-- Agents add; Ethan answers inline; answers then move to DECISIONS.md. -->

- [ ] <task-id>: <what is needed> — why: <...> — meanwhile: <what the agent did instead>
- [ ] F1: Servo direction on the real mount — why: the library assumes "right LDR brighter → pan angle increases" and "top LDR brighter → tilt angle increases"; if the servos are mounted the other way the tracker runs away from the sun — meanwhile: kept that convention; if it's wrong, swap the pair order in `tracker::step` (or tell me and I'll add an invert flag to the config).
- [ ] F3: Park tilt angle (and the measured east pan angle) — why: DECISIONS.md says park "facing east" with pan TBD, but gives no tilt for parking — meanwhile: `config::PARK = {0, 90}` marked TODO in `include/config.h`; tilt 90° is a guess. A low tilt toward the horizon would catch first light sooner.
- [ ] L1: INA219 shunt resistor value — why: current is computed as shunt voltage / shunt ohms — meanwhile: `logger/config.py` `SHUNT_OHMS = 0.1` (the usual "R100" breakout), marked TODO.
- [ ] L1: Servo-supply current range — why: with a 0.1 Ω shunt and default ±320 mV range the INA219 saturates at 3.2 A; two MG996Rs can stall at ~2.5 A each, so peaks on the servo channel could clip and under-count servo Wh — meanwhile: default range; a lower-ohm shunt on that board would fix it.
- [ ] L1: Please add `SOLARIS_DB` (optional, SQLite path, default `solaris.db`) to `.env.example` — why: agents are denied reading `.env.*`, so I couldn't edit it safely — meanwhile: documented in `logger/app.py`.
