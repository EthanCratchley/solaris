#pragma once

namespace tracker {

struct Limits {
  int min;
  int max;
};

struct Config {
  int deadband;  // ADC counts; a pair must differ by more than this to move
  int step;      // degrees per move
  Limits pan;
  Limits tilt;
};

struct Reading {
  int top;
  int bottom;
  int left;
  int right;
};

struct Position {
  int pan;
  int tilt;
};

int clamp(int value, Limits limits);

Position step(const Reading& reading, Position current, const Config& config);

// One `step` per axis from `current` toward `target` (clamped to the limits), no overshoot.
Position toward(Position current, Position target, const Config& config);

}  // namespace tracker
