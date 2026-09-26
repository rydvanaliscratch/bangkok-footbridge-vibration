# Data dictionary

One CSV per recording run. Filenames:

```
YYYYMMDD_HHMM_<site>_<run>.csv

20261005_1430_bridge01_ambient.csv
20261005_1455_bridge01_decay.csv
20261005_1510_bridge01_control.csv
20260928_2100_bench_pendulum.csv
```

`<run>` is one of: `ambient`, `decay`, `control`, `remount`, `pendulum`, `rest`, `tilt`.

## Columns

| Column | Unit | Description |
|---|---|---|
| `t_us` | microseconds | Value of the Arduino's `micros()` counter at the moment the sample was read. Not wall-clock time. Rolls over every ~71 minutes |
| `ax` | counts | Raw X acceleration, signed 16-bit |
| `ay` | counts | Raw Y acceleration, signed 16-bit |
| `az` | counts | Raw Z acceleration, signed 16-bit |

## Converting counts to physical units

At ±2 g full scale the sensor gives **16384 counts per g**, so one count is 61 µg.

```
a [g]     = counts / 16384
a [m/s^2] = counts / 16384 * 9.80665
```

A stationary sensor lying flat reads about +16384 on whichever axis points up.

## Sample rate

The sketch targets 200 Hz, but **use the measured rate, not the nominal one**.
Take the median of `diff(t_us)` and invert it. Using 200 Hz in an FFT when the true
rate was 187 Hz scales every reported frequency by 7%.

## Session metadata

Recorded separately in the field notebook and transcribed into `docs/build-log.md`:
site, span (m), number of intermediate supports, deck material, date, start time,
weather, traffic conditions, sensor position along the span, and the timestamp of
each jump during decay runs.
