#pragma once

#include <stddef.h>

#include "night.h"
#include "tracker.h"

// One CSV status line per report interval. Format is documented in docs/serial.md.
namespace report {

constexpr size_t LINE_SIZE = 64;  // widest line is 47 chars + NUL

struct Sample {
  unsigned long millis;
  tracker::Reading reading;
  tracker::Position position;
  night::State state;
};

// Writes the line (no newline) into `buf`. Returns its length, or 0 with `buf` emptied
// if it does not fit.
size_t format(char* buf, size_t size, const Sample& sample);

}  // namespace report
