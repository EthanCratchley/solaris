# Solaris - A Smart Renewable Energy Optimizer

## Project Overview

Solaris is a hardware based system designed to automatically orient a solar panel toward the brightest light source throughout the day. It uses a pan-tilt servo mechanism driven by light sensors (photoresistors) to dynamically adjust the solar panel's position in real time.

This physical system demonstrates how automated solar tracking can improve solar energy efficiency by ensuring optimal alignment with the sun.

## What it Solves

**Problem:**
Traditional fixed solar panels lose efficiency when they are not directly facing the sun, with losses up to 30–40% compared to panels that track the sun.

**Solution:**
This solar tracker autonomously adjusts the solar panel’s orientation in 2 axes (pan and tilt) to face the brightest light source (the sun). It maximizes energy capture without requiring GPS, manual adjustment, or expensive motors.

**Use Cases:**

- Educational tool to demonstrate renewable energy optimization.
- Prototype for low-cost solar tracking solutions in off-grid systems, farms, or small-scale solar installations.
- Expandable into IoT-based energy tracking systems.

## Scope

**Core Scope:**
- 2-axis solar tracking based on real-time light intensity detection.
- Fully physical hardware demonstration using servos and sensors.
- Focus on accurate mechanical motion toward the brightest source.

**Optional Stretch Goals (if time allows):**
- Data logging of servo positions and light intensity to a Raspberry Pi.
- Build a basic web dashboard to display real-time system status and sunlight levels.
- Include energy generation data if a solar panel is hooked up to a meter.

## Tech Stack (Tools, Software, Hardware)

**Hardware:**

- Arduino Uno R3 — Microcontroller for sensor reading and servo control
- Pan-Tilt Bracket Kit (2 DOF) — Holds the panel and servos
- 2x MG996R Servo Motors — High-torque motors for pan and tilt axes
- 4x LDR Photoresistors — Light sensors for detecting sunlight direction
- 4x 10kΩ Resistors — For LDR voltage dividers
- Breadboard, jumper wires, mounting hardware — Wiring and assembly
- Solar Panel or a cardboard dummy pane
- Raspberry Pi for data logging and dashboards

**Software:**
- Arduino IDE (C++): Microcontroller programming
- Python: Rasberry Pi for used logging/dashboard
- Streamlit / Flask: Simple web interface to display data

**Tools:**
- Hot glue, tape, screws, zip ties (for mechanical assembly)

## System Pipeline

![pipeline](/assets/pipeline.png)

## Step by Step

1. Mechanical Build: Assemble the pan-tilt mount, attach panel and LDRs
2. Circuit Wiring: Connect LDR sensors to Arduino analog pins and servos to PWM pins
3. Microcontroller Programming: Write and deploy Arduino code for reading LDRs and controlling servos
4. Testing: Check servo movement; adjust sensitivity and limits
5. Data Logging and Web UI: Send data from Arduino to Raspberry Pi for tracking and analysis
6. Final Demo Prep: Record video, create presentation, submit to Devpost
