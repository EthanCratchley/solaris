#include "night.h"

namespace night {

Night update(Night night, const tracker::Reading& r, unsigned long now, const Config& config) {
  if (night.state == State::Parked) {
    if (r.top > config.light || r.bottom > config.light || r.left > config.light ||
        r.right > config.light) {
      night.state = State::Tracking;
      night.dark = false;
    }
    return night;
  }

  if (r.top >= config.dark || r.bottom >= config.dark || r.left >= config.dark ||
      r.right >= config.dark) {
    night.dark = false;
    return night;
  }
  if (!night.dark) {
    night.dark = true;
    night.dark_since = now;
  }
  if (now - night.dark_since >= config.dark_ms) night.state = State::Parked;
  return night;
}

}  // namespace night
