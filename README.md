# Bangkok Footbridge Vibration Study

Ambient vibration measurement of pedestrian overpasses (สะพานลอย) in Bangkok using a
low-cost MEMS accelerometer, to determine fundamental frequency and damping ratio.

**Status:** instrument build and bench qualification. No field data yet.

## What this measures and why

A structure's natural frequency is a property of its own mass and stiffness, not of
whatever is shaking it. Road traffic, wind and footfall supply broadband excitation;
the structure responds preferentially at its own frequencies. Recording the response
and taking an averaged power spectrum therefore recovers those frequencies without
any controlled input. The technique is operational modal analysis.

Two questions:

1. **Vibration serviceability.** Design guidance requires a pedestrian comfort check
   when a footbridge's vertical fundamental frequency falls below 5 Hz; walking excites
   vertically in the 1–3 Hz band. Do any measured overpasses fall in that range?
2. **Period context.** Bangkok's deep soft-clay basin amplifies long-period ground
   motion. Where do these short, stiff structures sit relative to that band?

## Hardware

| Part | Qty | Note |
|---|---|---|
| Arduino Uno R3 | 1 | Any ATmega328P clone |
| GY-521 breakout (MPU-6050) | 1 | Headers soldered by hand |
| Jumper wires, male-to-female | 4 | |

Wiring — four connections, no breadboard:

| GY-521 | Uno |
|---|---|
| VCC | 5V |
| GND | GND |
| SDA | A4 |
| SCL | A5 |

The GY-521 carries its own 3.3 V regulator, so 5 V on VCC is correct.

## Sensor configuration

| Register | Value | Meaning |
|---|---|---|
| `0x6B` PWR_MGMT_1 | `0x01` | Wake; clock from gyro X for stability |
| `0x1A` CONFIG | `0x04` | DLPF 21 Hz — anti-aliasing below the 100 Hz Nyquist |
| `0x1C` ACCEL_CONFIG | `0x00` | ±2 g full scale = 16384 LSB/g = 61 µg per count |
| `0x19` SMPLRT_DIV | `0x04` | 1 kHz / (1+4) = 200 Hz internal sample rate |

## Repository layout

```
firmware/logger/    Arduino sketch: configures the sensor and streams timestamped samples
analysis/           Python: serial capture, timing check, spectra, damping  (added when data exists)
data/raw/           Field recordings, one CSV per run
data/calibration/   Bench recordings for gates B2, B3, B5
docs/               Operating guide, build log, protocol
```

## Reproducing this

1. Wire as above, open `firmware/logger/logger.ino` in the Arduino IDE, upload.
2. Open Serial Monitor at 115200. Confirm `WHO_AM_I ok`.
3. Run the bench gates in `docs/` before any field measurement.
4. Capture to CSV, analyse with the scripts in `analysis/`.

## Data format

See `data/README.md` for the column dictionary and units.

## Licence

Code MIT. Data CC BY 4.0. See LICENSE files when added.
