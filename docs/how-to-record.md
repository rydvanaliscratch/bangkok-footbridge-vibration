# How to record (quick card)

## Before
- Board fixed so it can't rock. Uno plugged in by USB; sensor LED on.
- Arduino IDE Serial Monitor **closed**.

## Record
```
cd ~/Desktop/bangkok-footbridge-vibration
python3 analysis/capture.py SITE RUN SECONDS
```
- SITE: `bench` at home, or the bridge ID from `data/bridges.csv` (`bridge01` ...)
- RUN: `rest` (still, B3/B4) · `tilt` (B2) · `pendulum` (B5) · `ambient` (midspan, 900 s) · `decay` (heel-drops, 300 s) · `control` (pavement, 300 s) · `remount`
- Files are named automatically `YYYYMMDD_HHMM_SITE_RUN.csv`: bench -> `data/calibration/`, bridges -> `data/raw/`. **Never rename or edit them.**

## Check a bench `rest` recording (B3 + B4)
```
python3 analysis/bench_checks.py data/calibration/<file>.csv
```

## After every session
1. Three lines in `docs/build-log.md` (date, files, what happened).
2. Save:
```
git add .
git commit -m "what happened"
git push
```

Keys: Up arrow = previous command · Tab = complete a file name · Control+C = stop recording early (keeps what was saved).
