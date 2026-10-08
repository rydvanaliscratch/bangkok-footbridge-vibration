# Build log

Three lines per session. Date, what was done, what happened — including failures.
This is the record that makes the work verifiably yours, and it makes writing the
methods section trivial instead of an act of reconstruction.

---

## 2026-09-__ — headers soldered

- Soldered 8-pin header to GY-521 #1. Pins pointing up so the board sits flat.
- Result:
- Next:

## 2026-09-26 — B1, device responds

- WHO_AM_I returned: 0xFF on the first two boots (no I2C reply). GY-521 power LED was off.
- VCC and GND joints were cold (dull, grainy); reflowed both, LED then steady red. Wire `i2c_scanner` example found the device at 0x68; logger re-uploaded and streams plausible CSV at 115200 (the `WHO_AM_I ok` line itself scrolled off before it was seen).
- Result: **PASS** (device at 0x68). Two failed boots before the fix, so watch for an intermittent SDA/SCL joint or jumper in B3/B4.
- Next: B2.

## 2026-09-26 — B2, gravity calibration

- Read by eye from the Serial Monitor (approximate, values fluctuate). Raw numbers in `data/calibration/20260926_1230_bench_B2_readings.csv`.
- Flat: az ≈ 15000 counts (expect 16384 ± 800), ax ≈ 100, ay ≈ −150
- Upside down: az ≈ −18100, ax ≈ 150, ay ≈ −150
- Pin side down: ax ≈ 16300; opposite edge: ax ≈ −16100
- Left of pins: ay ≈ −16600; right of pins: ay ≈ +16100 (first reported as −16600, a transcription slip, corrected same day)
- Offsets (midpoint of up/down) and scales (half the difference): X ≈ +100 / 16200 (edges tilted ~10° by the pins); Y ≈ −250 / 16350; Z ≈ −1550 (≈ −95 mg) / 16550.
- Result: X PASS, Y PASS (all within ±800 of 0 or ±16384). Z FAIL as written: flat 15000 (1384 low), upside down −18100 (1716 high in magnitude). Datasheet Z zero-g tolerance is ±80 mg, so this module is slightly outside it. Decision pending: record as fail + why it doesn't affect frequency/damping, or compare with the spare board first.

## 2026-09-26 — capture and bench-check scripts

- `analysis/capture.py` (records the Uno's serial output to CSV) and `analysis/bench_checks.py` (gates B3 and B4) written by Claude at Rydvan's request; Rydvan does all real recordings. Line-by-line explanation in the "Recording guide" doc.
- Tested against a simulated Uno (200 lines/s, reset garbage, micros() wraparound, one deliberately dropped line): capture saved every line, refused to overwrite, gave clear port errors; bench_checks found the dropped line and failed B4 as it should.
- B4 "median gap 5000 us" read as 5000 ± 50 us (1%) in the script — an interpretation, stated here so it is not hidden.

## 2026-09-26 — B3, noise floor

- Recording `data/calibration/20260926_2024_bench_rest.csv`: 60 s, board flat, held by thin double-sided tape, pin row over the table edge. 12,032 lines saved.
- SD of az = 26.3 counts = 1.60 mg (pass < 60). SD of ax = 16.8, ay = 16.3 counts. Dossier's datasheet-based estimate was ~30 counts; measured agrees.
- Means: ax 308.5, ay −231.6, az 14,969.4 counts (flat; Z offset as found in B2).
- Result: **PASS**

## 2026-09-26 — B4, sampling steadiness

- Same recording as B3. Median Δt = 5000.0 µs (expect 5000). 100.00% within ±500 µs; smallest/largest gap 4992/5008 µs (micros() resolves 4 µs steps). Dropped lines: 0
- Measured rate = 200.000 Hz
- Histogram: `figures/B4_gaps_20260926_2024_bench_rest.png`
- Result: **PASS**

## 2026-09-27 — analysis programs

- Written and tested by Claude at Rydvan's request: `analysis/common.py` (shared loading), `spectrum.py` (Welch spectrum, peak, bootstrap 95% range, ground comparison), `damping.py` (band-pass, heel-drop detection, logarithmic decrement), `pendulum_check.py` (gate B5), `analyse_bridge.py` (one command per bridge), `span_fit.py` (log f vs log L), `selftest.py`.
- Self-test on synthetic data with known answers: 3.20 Hz found as 3.196 Hz (95% range 3.19–3.20); damping 0.80 % found as 0.79 %; pendulum 0.997 Hz found; span slope −1.60 found as −1.60. ALL PASS (8 of 8).
- Choices that are ours, not from a standard, and must be stated in Methods: 4096-sample pieces; bootstrap over overlapping pieces (range may be slightly narrow); band-pass 0.7–1.3 f; heel-drop = burst > 8× typical level; stop decay at 3× background; proposed ground rule: bridge peak ≥ 10× ground. Decide the ground rule before field day 1.
- Templates added: `data/bridges.csv`, `data/sessions.csv`, `predictions/predictions-template.csv`, `requirements.txt`.

## 2026-09-__ — B5, pendulum validation

- String length ____ m, predicted f = ____ Hz from T = 2π√(L/g)
- Measured peak: ____ Hz. Second peak at ____ Hz (expect 2×)
- Result:
