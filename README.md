# Bangkok Footbridge Vibration Study

Ambient vibration measurement of pedestrian overpasses (สะพานลอย) in Bangkok using a
low-cost MEMS accelerometer, to determine fundamental frequency and damping ratio.

**Status:** field recordings finished (six footbridges, 20 Oct - 1 Nov 2026) and analysed. Paper in preparation; not yet peer reviewed. See `docs/build-log.md` for the full dated record, including failed attempts.

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
   (Background only: this study measured the bridges, not the basin, so it gives no result
   on this question.)

## Results (six concrete pedestrian overpasses in Bangkok)

Vertical fundamental frequency from ambient vibration (15-minute recordings), with the
95% range of the spectral peak. Span is inner face to inner face, paced with a 30 cm foot
(about +/-0.3 m). Ground ratio = peak power on the bridge divided by power at the same
frequency on a ground control; the rule, fixed on 14 Oct before any data, is at least 10x.

| Bridge | Span (m) | Peak (Hz) | 95% range (Hz) | Ground ratio | Damping (%) |
|---|---|---|---|---|---|
| bridge01 | 17.68 | 5.187 | 5.178-5.201 | 113x | 0.55 and 0.60 (two decays) |
| bridge02 | 16.80 | 4.741 | 4.724-4.761 | 33.2x | 1.20 |
| bridge03 | 24.25 | 3.339 | 3.334-3.350 | **8.1x (below the rule: unconfirmed)** | 0.80 |
| bridge04 | 25.73 | 3.158 | 3.154-3.162 | 32.0x | 0.46 and 0.54 (single drops) |
| bridge05 | 22.80 | 3.315 | 3.306-3.328 | 46.3x | 0.66 and 0.73 (two decays) |
| bridge06 | 25.55 | 2.977 | 2.973-2.987 | 39.7x | not measurable |

Span fit, log f against log L (6 bridges): slope -1.19, 95% range -1.63 to -0.75, R2 0.93.
The sealed predictions (`predictions/predictions_20261014.md`, written before any
recording) assumed depth proportional to span, which gives a slope near -1.

## Limits you should know about

- Damping comes from heel-drop decays and is indicative only: the amplitude check on the sensor
  (gate B5, pendulum) was not passed, so no absolute damping claim is made. Some bridges gave
  one usable drop or none under the pre-set detection rule.
- The drop-detection rule was changed after seeing data (band-passed signal instead of the raw
  signal); this is logged and the old rule's count is printed alongside.
- bridge03 does not meet the 10x ground rule; its peak is reported as unconfirmed.
- Spans were paced, not surveyed. Six bridges in two size groups is a small sample.
- Some files in `data/raw` are failed or mislabelled attempts; they are kept and explained in
  `docs/build-log.md` (for example the 31 Oct files labelled bridge04 were recorded at bridge05).

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
analysis/           Python: serial capture, timing check, spectra, damping, span fit
results/            Output tables written by the analysis programs
figures/            Spectra, decay fits and the span-fit plot
predictions/        Predictions sealed on 14 Oct 2026, before any bridge recording
data/raw/           Field recordings, one CSV per run
data/calibration/   Bench recordings for gates B2, B3, B5
docs/               Operating guide, build log, protocol
```

## Reproducing this

1. Wire as above, open `firmware/logger/logger.ino` in the Arduino IDE, upload.
2. Open Serial Monitor at 115200. Confirm `WHO_AM_I ok`.
3. Run the bench gates in `docs/` before any field measurement.
4. Install the libraries once: `python3 -m pip install -r requirements.txt`.
5. Capture to CSV: `python3 analysis/capture.py SITE RUN SECONDS [LABEL]`.
6. Analyse one bridge: `python3 analysis/analyse_bridge.py bridge05 --axis x`. The program
   picks the newest file of each type by label, so for bridges with several recordings pass the
   file explicitly, e.g. `--ambient data/raw/<file> --decay data/raw/<file>`.
7. Span fit: `python3 analysis/span_fit.py` (reads `data/bridges.csv` and `results/frequencies.csv`).
8. Paper figures: `python3 analysis/paper_figures.py figures/paper`.

Notes for anyone rerunning the analysis:
- bridge01, decay of 20 Oct 15:10: `damping.py` reports 8 detections, 7 usable, mean 0.64 %. The paper
  reports 0.60 % from 5 drops, because two detections (57.3 s and 224.7 s) did not fit the drop record
  from the field (six drops with pauses after drops 1, 2 and 4); see `docs/build-log.md`, 10 Nov.
- `data/sessions.csv` is an unused template: the field notes (conditions, drop schedules, problems)
  were recorded in `docs/build-log.md` instead.

## Data format

See `data/README.md` for the column dictionary and units.

## Licence

Code: MIT (`LICENSE`). Data: CC BY 4.0 (`data/LICENSE`).
