# Questions for Ethan

<!-- Agents add; Ethan answers inline; answers then move to DECISIONS.md. -->

- [ ] <task-id>: <what is needed> — why: <...> — meanwhile: <what the agent did instead>
- [ ] F1: Servo direction on the real mount — why: the library assumes "right LDR brighter → pan angle increases" and "top LDR brighter → tilt angle increases"; if the servos are mounted the other way the tracker runs away from the sun — meanwhile: kept that convention; if it's wrong, swap the pair order in `tracker::step` (or tell me and I'll add an invert flag to the config).
