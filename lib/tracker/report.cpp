#include "report.h"

#include <stdio.h>

namespace report {

size_t format(char* buf, size_t size, const Sample& s) {
  if (size == 0) return 0;
  int n = snprintf(buf, size, "%lu,%d,%d,%d,%d,%d,%d,%s", s.millis, s.reading.top,
                   s.reading.bottom, s.reading.left, s.reading.right, s.position.pan,
                   s.position.tilt, s.state == night::State::Parked ? "parked" : "tracking");
  if (n < 0 || static_cast<size_t>(n) >= size) {
    buf[0] = '\0';
    return 0;
  }
  return static_cast<size_t>(n);
}

}  // namespace report
