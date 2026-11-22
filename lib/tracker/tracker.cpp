#include "tracker.h"

namespace tracker {

int clamp(int value, Limits limits) {
  if (value < limits.min) return limits.min;
  if (value > limits.max) return limits.max;
  return value;
}

// +1 when `up` exceeds `down` by more than the deadband, -1 for the reverse, else 0.
static int direction(int up, int down, int deadband) {
  int diff = up - down;
  if (diff > deadband) return 1;
  if (diff < -deadband) return -1;
  return 0;
}

Position step(const Reading& reading, Position current, const Config& config) {
  int pan = current.pan + direction(reading.right, reading.left, config.deadband) * config.step;
  int tilt = current.tilt + direction(reading.top, reading.bottom, config.deadband) * config.step;
  return {clamp(pan, config.pan), clamp(tilt, config.tilt)};
}

}  // namespace tracker
