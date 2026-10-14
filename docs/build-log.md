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

## 2026-10-09 — first upload to GitHub

- The 26 Sep snapshot (first B1–B4 run) was committed on this Mac on 26 Sep but first uploaded to GitHub on 9 Oct, together with the analysis-programs snapshot. Local commit dates are set by the computer's clock; GitHub's record starts 9 Oct.
- Before the rerun, B1–B4 were repeated from the start (below) to check that the instrument gives the same results twice.

## 2026-10-12 — B1 rerun, I2C connection

- Program: `firmware/i2c_scanner/i2c_scanner.ino` (written by Claude at Rydvan's request; scans addresses 1–126, then reads WHO_AM_I, register 0x75). Uploaded to the Uno; Serial Monitor at 115200 baud.
- Known answer: one device at 0x68; WHO_AM_I = 0x68.
- Attempt 1: **FAIL**. "Devices found: 0", "WHO_AM_I: no reply from 0x68". The Uno printed normally, so USB, board and program were working. Sensor LED lit, so VCC/GND had power. Wiring checked: SDA→A4, SCL→A5, correct.
- Cause found by inspection: the solder on the sensor's SDA pin had lifted off the copper pad (a cold joint, as VCC/GND were on 26 Sep). Re-soldered SDA with the USB unplugged.
- Attempt 2: "Device found at 0x68", "Devices found: 1", "WHO_AM_I = 0x68 (correct: MPU-6050)".
- Result: **PASS** after repair. Lesson: joints can fail after handling; repeat B1 before every field day.

## 2026-10-12 — B2 tools

- `analysis/capture.py` now takes an optional fourth word, a label added to the file name (e.g. `capture.py bench tilt 15 flat` makes `..._bench_tilt_flat.csv`), so the six B2 positions are six separate files. Written by Claude; tested with a simulated Uno (file name, label check, no-label case).
- New `analysis/b2_check.py` (written by Claude): reads the six position files, finds which axis feels gravity in each, checks each reading is within ±800 counts of 1 g or 0, works out each axis's offset and scale, compares the offset with the datasheet (±50 mg X/Y, ±80 mg Z) and adds them to `results/b2_calibration.csv`. Also prints, as information only, the same check after removing each axis's offset.
- Tested on simulated recordings with known faults (offsets +100/−250/−1550, scales 16200/16350/16550): all recovered exactly; missing position and wrong face coverage both reported.
- Expectation written before the rerun: with a Z offset near −1550 counts, the four side positions will read Z ≈ −1550, so the main check will probably FAIL because of the offset alone. Both lines will be reported.

## 2026-10-13 — scouting, span measurements

- Raw readings for four candidate bridges in `data/span_measurements.csv` (every reading kept). Measured outer face to outer face of the support columns with the iPhone Measure app, cross-checked on Apple Maps.
- A, B, C: same 6-lane road, single span, no middle column. A 24.2/24.4 m (walked fast), map 25. B 22.7/23.4 m (phone overheating, app not locking on), map 20: unreliable, to be re-measured; not assumed equal to A or C. C 25.4/25.4 m (walked slowly), map 25.
- D: 8 lanes with a middle column. Whole length 34 m (twice); each span, end column to middle column, 17 m on both sides. The span used is 17 m. Map readings jumped between 30 and 40 m and were not used.
- Lessons: (1) iPhone Measure reads short when walked fast; walk slowly and trace the line. (2) Maps can't show column faces under the walkway and only give whole metres; use as a cross-check, never alone. (3) "Identical" bridges on one road still differed (A 24.3 vs C 25.4), so spans are measured, never assumed. (4) With a middle column the span is end-to-middle, and the sensor goes at the middle of one span, not over the middle column. (5) A 30 m tape would settle doubtful spans to ±0.1 m.
- Still to record for each chosen bridge: road/landmark, column width, underside photo, safe midspan position.

## 2026-10-13/14 — bridge choice, new Mac, recorder changes (before any bridge data)

- Decision (13 Oct, before any bridge recording): **6 bridges**, not 8. Four 6-lane single-span bridges on Charoen Nakhon Road (scouting A, B, C and one more; outer-outer about 24–25 m) and two 8-lane bridges with a middle column on Ratchadaphisek Road (spans about 17 m end-to-middle). Reasons: travel time, an even 4:2 split, and avoiding bridges with large signs (extra mass, and sign panels can sway and add their own peak).
- Consequence, stated before the data: with two span groups the slope test (H3) becomes a comparison of 17 m with 25 m spans, not a fitted slope; the two groups are on different roads, so design differences cannot be separated from length. Main questions unchanged: serviceability, and scatter among nominally identical bridges.
- Spans of B, the fourth Charoen Nakhon bridge and the second Ratchadaphisek bridge are estimated from neighbours for the predictions only; every span is measured on the day before recording, and only measured spans are used in the analysis.
- 14 Oct: project migrated to a new MacBook. `selftest.py` ALL PASS (8 of 8) on the new Mac.
- `capture.py` now finds the Uno's port automatically (`/dev/cu.usbmodem*`), because the port name can change on a new Mac; stops with a clear message if none or several are found. Written by Claude; tested with simulated port lists.
- Field recordings are run as `caffeinate -i python3 analysis/capture.py ...` so the Mac cannot sleep on battery during a 15-minute recording.
- Order of gates today: B1 and B3+B4 before the bridges (new Mac, recent solder repair); B2 and B5 the same evening, with the same sensor, wiring and Mac, unchanged in between.

## 2026-10-14 — B1 on the new Mac

- First compile failed: "avr-g++: bad CPU type in executable" (Rosetta not installed on the new Apple-silicon Mac; same fault as on the old Mac). Fixed with `softwareupdate --install-rosetta --agree-to-license`.
- Scanner (`firmware/i2c_scanner/i2c_scanner.ino`): "Device found at 0x68", "Devices found: 1", "WHO_AM_I = 0x68 (correct: MPU-6050)".
- Result: **PASS**. The SDA joint re-soldered on 12 Oct holds.
- Also this morning: the project's GitHub address had changed to SSH (git@github.com) and asked for an SSH-key passphrase; set back to https with `git remote set-url`, push worked with the token.

## 2026-09-__ — B5, pendulum validation

- String length ____ m, predicted f = ____ Hz from T = 2π√(L/g)
- Measured peak: ____ Hz. Second peak at ____ Hz (expect 2×)
- Result:
