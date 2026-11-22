#include <Arduino.h>
#include <Servo.h>

#include "config.h"
#include "night.h"
#include "report.h"
#include "tracker.h"

static_assert(config::LDR_TOP == A0, "LDR top must be A0 (HARDWARE.md)");
static_assert(config::LDR_BOTTOM == A1, "LDR bottom must be A1 (HARDWARE.md)");
static_assert(config::LDR_LEFT == A2, "LDR left must be A2 (HARDWARE.md)");
static_assert(config::LDR_RIGHT == A3, "LDR right must be A3 (HARDWARE.md)");

static Servo pan;
static Servo tilt;
static tracker::Position position = config::START;
static unsigned long moved_at = 0;
static bool attached = false;
static night::Night sky;
static unsigned long reported_at = 0;

static void command(tracker::Position target) {
  position = {tracker::clamp(target.pan, config::TRACKER.pan),
              tracker::clamp(target.tilt, config::TRACKER.tilt)};
  // Write before attach so the first pulse is the target, not the library's 90° default.
  pan.write(position.pan);
  tilt.write(position.tilt);
  if (!attached) {
    pan.attach(config::SERVO_PAN);
    tilt.attach(config::SERVO_TILT);
    attached = true;
  }
  moved_at = millis();
}

static void detach() {
  pan.detach();
  tilt.detach();
  attached = false;
}

void setup() {
  Serial.begin(config::BAUD);
  command(config::START);
  delay(config::BOOT_SETTLE_MS);
  detach();
}

void loop() {
  unsigned long now = millis();
  if (attached && now - moved_at >= config::SETTLE_MS) detach();

  tracker::Reading reading = {analogRead(config::LDR_TOP), analogRead(config::LDR_BOTTOM),
                              analogRead(config::LDR_LEFT), analogRead(config::LDR_RIGHT)};
  sky = night::update(sky, reading, now, config::NIGHT);

  if (now - reported_at >= config::REPORT_INTERVAL_MS) {
    reported_at = now;
    char line[report::LINE_SIZE];
    if (report::format(line, sizeof(line), {now, reading, position, sky.state})) Serial.println(line);
  }

  if (now - moved_at < config::MOVE_INTERVAL_MS) return;
  tracker::Position next = sky.state == night::State::Parked
                               ? tracker::toward(position, config::PARK, config::TRACKER)
                               : tracker::step(reading, position, config::TRACKER);
  if (next.pan == position.pan && next.tilt == position.tilt) return;
  command(next);
}
