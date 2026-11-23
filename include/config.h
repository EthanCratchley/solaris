#pragma once

#include "tracker.h"

// The one place firmware settings live. Values must match HARDWARE.md (checked by
// test/native/test_config). Pins are plain Uno numbers so this builds natively;
// main.cpp static_asserts them against A0..A3.
namespace config {

constexpr int LDR_TOP = 14;     // A0
constexpr int LDR_BOTTOM = 15;  // A1
constexpr int LDR_LEFT = 16;    // A2
constexpr int LDR_RIGHT = 17;   // A3

constexpr int SERVO_PAN = 9;
constexpr int SERVO_TILT = 10;

constexpr tracker::Config TRACKER = {
    30,         // deadband, ADC counts
    1,          // step, degrees
    {0, 180},   // pan limits
    {15, 165},  // tilt limits
};

constexpr unsigned long MOVE_INTERVAL_MS = 50;
// Servos stay attached this long after a write, then detach. Shorter than the move
// interval so they are always detached between moves.
constexpr unsigned long SETTLE_MS = 40;
// From an unknown power-on angle the first move can be up to 180°.
constexpr unsigned long BOOT_SETTLE_MS = 1000;

constexpr tracker::Position START = {90, 90};

}  // namespace config
