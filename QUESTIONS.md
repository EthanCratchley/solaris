# Questions for Ethan

<!-- Agents add; Ethan answers inline; answers then move to DECISIONS.md. -->

- [ ] <task-id>: <what is needed> — why: <...> — meanwhile: <what the agent did instead>
- [ ] F1: Servo direction on the real mount — why: the library assumes "right LDR brighter → pan angle increases" and "top LDR brighter → tilt angle increases"; if the servos are mounted the other way the tracker runs away from the sun — meanwhile: kept that convention; if it's wrong, swap the pair order in `tracker::step` (or tell me and I'll add an invert flag to the config).
- [ ] F3: Park tilt angle (and the measured east pan angle) — why: DECISIONS.md says park "facing east" with pan TBD, but gives no tilt for parking — meanwhile: `config::PARK = {0, 90}` marked TODO in `include/config.h`; tilt 90° is a guess. A low tilt toward the horizon would catch first light sooner.
