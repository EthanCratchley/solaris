#pragma once

#include "tracker.h"

namespace night {

enum class State { Tracking, Parked };

struct Config {
  int dark;               // all LDRs strictly below this count as dark
  int light;              // any LDR strictly above this ends the night
  unsigned long dark_ms;  // continuous darkness needed before parking
};

struct Night {
  State state = State::Tracking;
  bool dark = false;
  unsigned long dark_since = 0;
};

// `now` is millis(); differences are taken unsigned so wraparound is safe.
Night update(Night night, const tracker::Reading& reading, unsigned long now,
             const Config& config);

}  // namespace night
