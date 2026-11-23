#include <unity.h>

#include "tracker.h"

using tracker::Config;
using tracker::Position;
using tracker::Reading;

static const Config cfg = {30, 1, {0, 180}, {15, 165}};
static const Position mid = {90, 90};

void setUp() {}
void tearDown() {}

static Position run(Reading r, Position p = mid, const Config& c = cfg) {
  return tracker::step(r, p, c);
}

void test_equal_light_holds() {
  Position p = run({500, 500, 500, 500});
  TEST_ASSERT_EQUAL(90, p.pan);
  TEST_ASSERT_EQUAL(90, p.tilt);
}

void test_left_brighter_pans_down() {
  Position p = run({500, 500, 600, 500});
  TEST_ASSERT_EQUAL(89, p.pan);
  TEST_ASSERT_EQUAL(90, p.tilt);
}

void test_right_brighter_pans_up() {
  Position p = run({500, 500, 500, 600});
  TEST_ASSERT_EQUAL(91, p.pan);
  TEST_ASSERT_EQUAL(90, p.tilt);
}

void test_top_brighter_tilts_up() {
  Position p = run({600, 500, 500, 500});
  TEST_ASSERT_EQUAL(90, p.pan);
  TEST_ASSERT_EQUAL(91, p.tilt);
}

void test_bottom_brighter_tilts_down() {
  Position p = run({500, 600, 500, 500});
  TEST_ASSERT_EQUAL(90, p.pan);
  TEST_ASSERT_EQUAL(89, p.tilt);
}

void test_both_axes_move_together() {
  Position p = run({600, 500, 500, 600});
  TEST_ASSERT_EQUAL(91, p.pan);
  TEST_ASSERT_EQUAL(91, p.tilt);
}

void test_difference_at_deadband_holds() {
  Position p = run({530, 500, 530, 500});
  TEST_ASSERT_EQUAL(90, p.pan);
  TEST_ASSERT_EQUAL(90, p.tilt);
}

void test_difference_just_over_deadband_moves() {
  Position p = run({531, 500, 500, 531});
  TEST_ASSERT_EQUAL(91, p.pan);
  TEST_ASSERT_EQUAL(91, p.tilt);
}

void test_deadband_is_symmetric() {
  Position p = run({500, 530, 530, 500});
  TEST_ASSERT_EQUAL(90, p.pan);
  TEST_ASSERT_EQUAL(90, p.tilt);
  p = run({500, 531, 531, 500});
  TEST_ASSERT_EQUAL(89, p.pan);
  TEST_ASSERT_EQUAL(89, p.tilt);
}

void test_step_size_is_used() {
  Config c = cfg;
  c.step = 5;
  Position p = run({600, 500, 500, 600}, mid, c);
  TEST_ASSERT_EQUAL(95, p.pan);
  TEST_ASSERT_EQUAL(95, p.tilt);
}

void test_clamps_at_upper_limits() {
  Position p = run({600, 500, 500, 600}, {180, 165});
  TEST_ASSERT_EQUAL(180, p.pan);
  TEST_ASSERT_EQUAL(165, p.tilt);
}

void test_clamps_at_lower_limits() {
  Position p = run({500, 600, 600, 500}, {0, 15});
  TEST_ASSERT_EQUAL(0, p.pan);
  TEST_ASSERT_EQUAL(15, p.tilt);
}

void test_large_step_does_not_overshoot_limits() {
  Config c = cfg;
  c.step = 10;
  Position p = run({600, 500, 500, 600}, {175, 160}, c);
  TEST_ASSERT_EQUAL(180, p.pan);
  TEST_ASSERT_EQUAL(165, p.tilt);
  p = run({500, 600, 600, 500}, {5, 20}, c);
  TEST_ASSERT_EQUAL(0, p.pan);
  TEST_ASSERT_EQUAL(15, p.tilt);
}

void test_out_of_range_start_is_clamped_even_when_holding() {
  Position p = run({500, 500, 500, 500}, {200, 0});
  TEST_ASSERT_EQUAL(180, p.pan);
  TEST_ASSERT_EQUAL(15, p.tilt);
  p = run({500, 500, 500, 500}, {-10, 170});
  TEST_ASSERT_EQUAL(0, p.pan);
  TEST_ASSERT_EQUAL(165, p.tilt);
}

void test_clamp_helper() {
  tracker::Limits l = {15, 165};
  TEST_ASSERT_EQUAL(15, tracker::clamp(-1, l));
  TEST_ASSERT_EQUAL(15, tracker::clamp(15, l));
  TEST_ASSERT_EQUAL(100, tracker::clamp(100, l));
  TEST_ASSERT_EQUAL(165, tracker::clamp(165, l));
  TEST_ASSERT_EQUAL(165, tracker::clamp(1000, l));
}

void test_extreme_adc_values() {
  Position p = run({1023, 0, 0, 1023});
  TEST_ASSERT_EQUAL(91, p.pan);
  TEST_ASSERT_EQUAL(91, p.tilt);
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_equal_light_holds);
  RUN_TEST(test_left_brighter_pans_down);
  RUN_TEST(test_right_brighter_pans_up);
  RUN_TEST(test_top_brighter_tilts_up);
  RUN_TEST(test_bottom_brighter_tilts_down);
  RUN_TEST(test_both_axes_move_together);
  RUN_TEST(test_difference_at_deadband_holds);
  RUN_TEST(test_difference_just_over_deadband_moves);
  RUN_TEST(test_deadband_is_symmetric);
  RUN_TEST(test_step_size_is_used);
  RUN_TEST(test_clamps_at_upper_limits);
  RUN_TEST(test_clamps_at_lower_limits);
  RUN_TEST(test_large_step_does_not_overshoot_limits);
  RUN_TEST(test_out_of_range_start_is_clamped_even_when_holding);
  RUN_TEST(test_clamp_helper);
  RUN_TEST(test_extreme_adc_values);
  return UNITY_END();
}
