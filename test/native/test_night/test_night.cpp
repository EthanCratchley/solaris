#include <limits.h>
#include <unity.h>

#include "config.h"
#include "night.h"
#include "tracker.h"

using night::State;

static const night::Config cfg = {50, 100, 600000UL};
static const unsigned long MIN = 60000UL;
static const tracker::Reading DAY = {600, 600, 600, 600};
static const tracker::Reading DARK = {10, 20, 30, 49};

void setUp() {}
void tearDown() {}

static night::Night fresh() { return night::Night(); }

void test_starts_tracking() { TEST_ASSERT_EQUAL(State::Tracking, fresh().state); }

void test_daylight_keeps_tracking() {
  night::Night n = fresh();
  for (unsigned long t = 0; t <= 30 * MIN; t += MIN) n = night::update(n, DAY, t, cfg);
  TEST_ASSERT_EQUAL(State::Tracking, n.state);
}

void test_parks_after_ten_dark_minutes_not_before() {
  night::Night n = night::update(fresh(), DAY, 0, cfg);
  n = night::update(n, DARK, 1000, cfg);
  n = night::update(n, DARK, 1000 + 10 * MIN - 1, cfg);
  TEST_ASSERT_EQUAL(State::Tracking, n.state);
  n = night::update(n, DARK, 1000 + 10 * MIN, cfg);
  TEST_ASSERT_EQUAL(State::Parked, n.state);
}

void test_reading_at_dark_threshold_is_not_dark() {
  night::Night n = fresh();
  tracker::Reading edge = {10, 10, 10, 50};
  for (unsigned long t = 0; t <= 20 * MIN; t += MIN) n = night::update(n, edge, t, cfg);
  TEST_ASSERT_EQUAL(State::Tracking, n.state);
}

void test_any_single_ldr_above_dark_counts_as_light() {
  const tracker::Reading one_lit[] = {
      {50, 0, 0, 0}, {0, 50, 0, 0}, {0, 0, 50, 0}, {0, 0, 0, 50}};
  for (const tracker::Reading& r : one_lit) {
    night::Night n = fresh();
    for (unsigned long t = 0; t <= 20 * MIN; t += MIN) n = night::update(n, r, t, cfg);
    TEST_ASSERT_EQUAL(State::Tracking, n.state);
  }
}

void test_brief_light_restarts_dark_timer() {
  night::Night n = night::update(fresh(), DARK, 0, cfg);
  n = night::update(n, DARK, 9 * MIN, cfg);
  n = night::update(n, {10, 10, 10, 60}, 9 * MIN + 1, cfg);
  n = night::update(n, DARK, 9 * MIN + 2, cfg);
  n = night::update(n, DARK, 10 * MIN + 5, cfg);
  TEST_ASSERT_EQUAL(State::Tracking, n.state);
  n = night::update(n, DARK, 19 * MIN + 1, cfg);
  TEST_ASSERT_EQUAL(State::Tracking, n.state);
  n = night::update(n, DARK, 19 * MIN + 2, cfg);
  TEST_ASSERT_EQUAL(State::Parked, n.state);
}

static night::Night parked() {
  night::Night n = night::update(fresh(), DARK, 0, cfg);
  n = night::update(n, DARK, 10 * MIN, cfg);
  TEST_ASSERT_EQUAL(State::Parked, n.state);
  return n;
}

void test_hysteresis_band_stays_parked() {
  night::Night n = parked();
  n = night::update(n, {60, 60, 60, 60}, 11 * MIN, cfg);
  TEST_ASSERT_EQUAL(State::Parked, n.state);
  n = night::update(n, {100, 100, 100, 100}, 12 * MIN, cfg);
  TEST_ASSERT_EQUAL(State::Parked, n.state);
}

void test_resumes_when_any_ldr_above_light_threshold() {
  const tracker::Reading dawn[] = {
      {101, 0, 0, 0}, {0, 101, 0, 0}, {0, 0, 101, 0}, {0, 0, 0, 101}};
  for (const tracker::Reading& r : dawn) {
    night::Night n = night::update(parked(), r, 11 * MIN, cfg);
    TEST_ASSERT_EQUAL(State::Tracking, n.state);
  }
}

void test_after_resume_needs_a_fresh_dark_period() {
  night::Night n = night::update(parked(), {200, 200, 200, 200}, 11 * MIN, cfg);
  n = night::update(n, DARK, 11 * MIN + 1, cfg);
  n = night::update(n, DARK, 20 * MIN, cfg);
  TEST_ASSERT_EQUAL(State::Tracking, n.state);
  n = night::update(n, DARK, 21 * MIN + 1, cfg);
  TEST_ASSERT_EQUAL(State::Parked, n.state);
}

void test_dark_timer_survives_millis_wraparound() {
  unsigned long start = ULONG_MAX - 5 * MIN;
  night::Night n = night::update(fresh(), DARK, start, cfg);
  n = night::update(n, DARK, start + 9 * MIN, cfg);  // wrapped past zero
  TEST_ASSERT_EQUAL(State::Tracking, n.state);
  n = night::update(n, DARK, start + 10 * MIN, cfg);
  TEST_ASSERT_EQUAL(State::Parked, n.state);
}

void test_toward_steps_and_stops_at_target() {
  tracker::Position p = tracker::toward({90, 90}, {0, 100}, config::TRACKER);
  TEST_ASSERT_EQUAL(89, p.pan);
  TEST_ASSERT_EQUAL(91, p.tilt);
  p = tracker::toward({0, 100}, {0, 100}, config::TRACKER);
  TEST_ASSERT_EQUAL(0, p.pan);
  TEST_ASSERT_EQUAL(100, p.tilt);
}

void test_toward_does_not_overshoot_with_large_step() {
  tracker::Config c = config::TRACKER;
  c.step = 10;
  tracker::Position p = tracker::toward({5, 95}, {0, 100}, c);
  TEST_ASSERT_EQUAL(0, p.pan);
  TEST_ASSERT_EQUAL(100, p.tilt);
}

void test_toward_clamps_target_outside_limits() {
  tracker::Position p = {20, 20};
  for (int i = 0; i < 400; i++) p = tracker::toward(p, {-50, 0}, config::TRACKER);
  TEST_ASSERT_EQUAL(0, p.pan);
  TEST_ASSERT_EQUAL(15, p.tilt);
}

void test_park_position_within_limits() {
  TEST_ASSERT_EQUAL(config::PARK.pan, tracker::clamp(config::PARK.pan, config::TRACKER.pan));
  TEST_ASSERT_EQUAL(config::PARK.tilt, tracker::clamp(config::PARK.tilt, config::TRACKER.tilt));
}

void test_config_matches_decisions() {
  TEST_ASSERT_EQUAL(50, config::NIGHT.dark);
  TEST_ASSERT_EQUAL(100, config::NIGHT.light);
  TEST_ASSERT_EQUAL(600000UL, config::NIGHT.dark_ms);
}

// Mirrors one firmware loop tick: night state picks between tracking and parking.
static tracker::Position tick(night::Night& n, tracker::Position p, tracker::Reading r,
                              unsigned long t) {
  n = night::update(n, r, t, config::NIGHT);
  if (n.state == State::Parked) return tracker::toward(p, config::PARK, config::TRACKER);
  return tracker::step(r, p, config::TRACKER);
}

void test_dusk_night_dawn_simulation() {
  night::Night n = fresh();
  tracker::Position p = {150, 120};
  unsigned long t = 0;
  const unsigned long dt = config::MOVE_INTERVAL_MS;

  // Dusk: sun low in the west (right side brighter), fading out.
  for (int level = 400; level >= 0; level -= 2, t += dt)
    p = tick(n, p, {level, level, level / 2, level}, t);
  TEST_ASSERT_EQUAL(State::Tracking, n.state);

  // Night: dark for an hour. Must park and arrive at the park position.
  for (unsigned long end = t + 60 * MIN; t < end; t += dt) p = tick(n, p, DARK, t);
  TEST_ASSERT_EQUAL(State::Parked, n.state);
  TEST_ASSERT_EQUAL(config::PARK.pan, p.pan);
  TEST_ASSERT_EQUAL(config::PARK.tilt, p.tilt);

  // Pre-dawn glow inside the hysteresis band: stays parked, does not move.
  for (unsigned long end = t + 5 * MIN; t < end; t += dt) p = tick(n, p, {80, 70, 90, 60}, t);
  TEST_ASSERT_EQUAL(State::Parked, n.state);
  TEST_ASSERT_EQUAL(config::PARK.pan, p.pan);

  // Dawn: east side (left) brightens past the light threshold — tracking resumes.
  p = tick(n, p, {300, 300, 400, 150}, t);
  TEST_ASSERT_EQUAL(State::Tracking, n.state);
  tracker::Position before = p;
  p = tick(n, p, {400, 300, 300, 300}, t += dt);
  TEST_ASSERT_EQUAL(before.tilt + 1, p.tilt);
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_starts_tracking);
  RUN_TEST(test_daylight_keeps_tracking);
  RUN_TEST(test_parks_after_ten_dark_minutes_not_before);
  RUN_TEST(test_reading_at_dark_threshold_is_not_dark);
  RUN_TEST(test_any_single_ldr_above_dark_counts_as_light);
  RUN_TEST(test_brief_light_restarts_dark_timer);
  RUN_TEST(test_hysteresis_band_stays_parked);
  RUN_TEST(test_resumes_when_any_ldr_above_light_threshold);
  RUN_TEST(test_after_resume_needs_a_fresh_dark_period);
  RUN_TEST(test_dark_timer_survives_millis_wraparound);
  RUN_TEST(test_toward_steps_and_stops_at_target);
  RUN_TEST(test_toward_does_not_overshoot_with_large_step);
  RUN_TEST(test_toward_clamps_target_outside_limits);
  RUN_TEST(test_park_position_within_limits);
  RUN_TEST(test_config_matches_decisions);
  RUN_TEST(test_dusk_night_dawn_simulation);
  return UNITY_END();
}
