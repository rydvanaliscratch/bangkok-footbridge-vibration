# How to record and analyse (quick card)

Full explanations: "The Complete Study Guide" (Claude doc).

## Once only
```
cd ~/Desktop/bangkok-footbridge-vibration
python3 -m pip install -r requirements.txt
python3 analysis/selftest.py          # must say ALL PASS
```

## Before every recording
- Board fixed so it can't rock. Uno plugged in by USB; sensor LED on.
- Arduino IDE Serial Monitor **closed**. Laptop lid open (closing it stops the recording).
- On battery a Mac can fall asleep by itself after a few idle minutes, which would cut a 15-minute recording short. Put `caffeinate -i` in front of every field recording, e.g. `caffeinate -i python3 analysis/capture.py bridge01 ambient 900`. (`caffeinate` keeps the Mac awake only while that command runs.)

## Record
```
cd ~/Desktop/bangkok-footbridge-vibration
python3 analysis/capture.py SITE RUN SECONDS
```
- SITE: `bench` at home, or the bridge ID from `data/bridges.csv` (`bridge01` ...)
- RUN: `rest` (B3/B4) · `tilt` (B2) · `pendulum` (B5) · `ambient` (900) · `decay` (300) · `control` (300) · `remount`
- Files name themselves `YYYYMMDD_HHMM_SITE_RUN.csv`. **Never rename or edit them.**

## Analyse
| What | Command |
| --- | --- |
| B3 + B4 (bench rest) | `python3 analysis/bench_checks.py data/calibration/<file>.csv` |
| B5 (pendulum) | `python3 analysis/pendulum_check.py data/calibration/<file>.csv` |
| One bridge, everything | `python3 analysis/analyse_bridge.py bridge01` |
| Just a spectrum | `python3 analysis/spectrum.py <file>.csv --control <ground>.csv` |
| Just damping | `python3 analysis/damping.py <decay>.csv --f 3.2` |
| Span test (3+ bridges) | `python3 analysis/span_fit.py` |

Results are added automatically to `results/*.csv`; pictures go to `figures/`.

## After every session
1. `data/sessions.csv`: one row per recording (field days).
2. `docs/build-log.md`: three lines (date, files, what happened and the key numbers).
3. Save:
```
git add .
git commit -m "what happened"
git push
```

Keys: Up arrow = previous command · Tab = complete a file name · Control+C = stop early (keeps what was saved).

## Measuring a span (scouting)
- Span = distance between two supports. Count the columns first: with a middle column, each span is end column to middle column.
- iPhone Measure app, **walk slowly**, trace the line, phone not overheating. Outer face to outer face of the columns (end-to-middle for multi-span). Twice.
- Measure one column's width too, so centre-to-centre = outer-outer − one width.
- Cross-check on a map (only roughly ±1 m). If methods disagree by more than about 1 m, re-measure (30 m tape best). Never assume a span from a "similar" bridge.
- Write every reading in `data/span_measurements.csv`, including bad ones, with a note.
- On a two-span bridge, put the sensor at the middle of **one span**, never above the middle column.
