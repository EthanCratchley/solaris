# Serial output

The firmware prints one CSV line per second on the Uno's USB serial port at **115200**
baud, 8N1. Lines end with `\r\n` (`Serial.println`). No header is sent; the column order
is fixed:

```
millis,ldr_top,ldr_bottom,ldr_left,ldr_right,pan,tilt,state
```

| Column | Type | Range | Meaning |
|---|---|---|---|
| `millis` | unsigned integer | 0–4294967295 | `millis()` at the time of the line; wraps after ~49.7 days and resets on reboot |
| `ldr_top` | integer | 0–1023 | raw ADC reading, A0 |
| `ldr_bottom` | integer | 0–1023 | raw ADC reading, A1 |
| `ldr_left` | integer | 0–1023 | raw ADC reading, A2 |
| `ldr_right` | integer | 0–1023 | raw ADC reading, A3 |
| `pan` | integer | 0–180 | last commanded pan angle, degrees |
| `tilt` | integer | 15–165 | last commanded tilt angle, degrees |
| `state` | text | `tracking` / `parked` | night state (see DECISIONS.md, night parking) |

Example line:

```
3600000,512,498,601,587,93,120,tracking
```

Fields contain no spaces or quotes. The widest possible line is 47 characters. Anything
that does not have exactly 8 fields is not a status line and should be ignored (e.g. a
partial line after the board resets).

Source of truth: `lib/tracker/report.cpp`; `test/native/test_report` checks this file's
header and example lines against the formatter.
