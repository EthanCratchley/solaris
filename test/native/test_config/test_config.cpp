#include <unity.h>

#include "config.h"
#include "tracker.h"

// Values copied from HARDWARE.md on purpose: if config.h drifts from it, these fail.
static const int PAN_MIN = 0, PAN_MAX = 180, TILT_MIN = 15, TILT_MAX = 165;

void setUp() {}
void tearDown() {}

void test_config_matches_hardware_md() {
  TEST_ASSERT_EQUAL(14, config::LDR_TOP);  // A0 on the Uno
  TEST_ASSERT_EQUAL(15, config::LDR_BOTTOM);
  TEST_ASSERT_EQUAL(16, config::LDR_LEFT);
  TEST_ASSERT_EQUAL(17, config::LDR_RIGHT);
  TEST_ASSERT_EQUAL(9, config::SERVO_PAN);
  TEST_ASSERT_EQUAL(10, config::SERVO_TILT);
  TEST_ASSERT_EQUAL(PAN_MIN, config::TRACKER.pan.min);
  TEST_ASSERT_EQUAL(PAN_MAX, config::TRACKER.pan.max);
  TEST_ASSERT_EQUAL(TILT_MIN, config::TRACKER.tilt.min);
  TEST_ASSERT_EQUAL(TILT_MAX, config::TRACKER.tilt.max);
  TEST_ASSERT_EQUAL(30, config::TRACKER.deadband);
  TEST_ASSERT_EQUAL(1, config::TRACKER.step);
  TEST_ASSERT_EQUAL(50, config::MOVE_INTERVAL_MS);
}

void test_servos_detach_before_next_move() {
  TEST_ASSERT_TRUE(config::SETTLE_MS < config::MOVE_INTERVAL_MS);
}

void test_start_position_is_within_limits() {
  TEST_ASSERT_TRUE(config::START.pan >= PAN_MIN && config::START.pan <= PAN_MAX);
  TEST_ASSERT_TRUE(config::START.tilt >= TILT_MIN && config::START.tilt <= TILT_MAX);
}

static void assert_within_limits(tracker::Position p) {
  TEST_ASSERT_TRUE(p.pan >= PAN_MIN && p.pan <= PAN_MAX);
  TEST_ASSERT_TRUE(p.tilt >= TILT_MIN && p.tilt <= TILT_MAX);
}

// Every reading pattern (min, deadband edges, max on each LDR) from every start angle,
// including starts outside the limits, must produce a command inside the limits.
void test_no_command_outside_limits() {
  const int levels[] = {0, 1, 30, 31, 500, 992, 993, 1023};
  const int n = sizeof(levels) / sizeof(levels[0]);
  for (int start_pan = -20; start_pan <= 200; start_pan += 5) {
    for (int start_tilt = -20; start_tilt <= 200; start_tilt += 5) {
      for (int t = 0; t < n; t++)
        for (int b = 0; b < n; b++)
          for (int l = 0; l < n; l++)
            for (int r = 0; r < n; r++) {
              tracker::Reading reading = {levels[t], levels[b], levels[l], levels[r]};
              assert_within_limits(
                  tracker::step(reading, {start_pan, start_tilt}, config::TRACKER));
            }
    }
  }
}

// Driving one direction for longer than the full range must stop at the limit.
void test_sustained_drive_stops_at_limits() {
  tracker::Position p = config::START;
  for (int i = 0; i < 400; i++) p = tracker::step({1023, 0, 0, 1023}, p, config::TRACKER);
  TEST_ASSERT_EQUAL(PAN_MAX, p.pan);
  TEST_ASSERT_EQUAL(TILT_MAX, p.tilt);
  for (int i = 0; i < 400; i++) p = tracker::step({0, 1023, 1023, 0}, p, config::TRACKER);
  TEST_ASSERT_EQUAL(PAN_MIN, p.pan);
  TEST_ASSERT_EQUAL(TILT_MIN, p.tilt);
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_config_matches_hardware_md);
  RUN_TEST(test_servos_detach_before_next_move);
  RUN_TEST(test_start_position_is_within_limits);
  RUN_TEST(test_no_command_outside_limits);
  RUN_TEST(test_sustained_drive_stops_at_limits);
  return UNITY_END();
}
