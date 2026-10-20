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

## 2026-10-14 — B3 + B4 on the new Mac

- Recording `data/calibration/20261014_1003_bench_rest.csv`: 60 s, sensor flat on its tile, run as `caffeinate -i python3 analysis/capture.py bench rest 60`; port found automatically (/dev/cu.usbmodem21101). 12,026 samples, 60.12 s, 1 non-data line (Uno restart bytes).
- B4: median gap 5000.0 µs, 100.00 % within ±500 µs, smallest/largest 4992/5008 µs, 0 dropped, 200.000 Hz. **PASS**. Histogram `figures/B4_gaps_20261014_1003_bench_rest.png`.
- B3: SD x 16.5, y 16.7, z 26.2 counts (z = 1.60 mg). **PASS** (< 60). 26 Sep: z SD 26.3, so the noise floor repeats.
- Not expected: mean readings flat have changed since 26 Sep: x −159 (was +309), y +103 (was −232), z 16,675 (was 14,969). Either a different board or the 12 Oct re-soldering shifted the offsets (soldering stress can). Does not affect frequency or damping (mean removed in analysis). B2 tonight measures the new offsets; board identity to be confirmed by Rydvan.

## 2026-10-20 — B5 run 1 (FAIL) and the pass rule written before run 2

- Run 1: `data/calibration/20261020_0857_bench_pendulum.csv` (60 s, 12,046 lines). Floss pendulum taped to a pen. Check run with `--length 0.25`, which was the program's default, not a measured length. Peaks 1.88 / 1.88 / 1.85 Hz on x / y / z; theory 0.997 Hz and 1.994 Hz. **RESULT: FAIL.** Kept as recorded; not deleted, not re-analysed to look better.
- What the file shows (diagnostic only, not a result): the sensor was still for 5 s, handled 5–8 s, released with a large kick at 8 s, and was almost still again by about 14 s. The swing lasted only a few seconds, so the 60 s spectrum was mostly silence plus the kick. A weak peak near 1.07 Hz appears at 12–20 s. That window was chosen after seeing the file, so it does not count as a pass.
- Likely cause: something damps the swing (jumper wires dragging, even when slack), plus a hard release. Wires cannot be made longer/lighter without new joints, which are the known weak point.
- **Rule for B5, written before run 2 was analysed or looked at (Rydvan agreed, 20 Oct):**
  - Pass A (strict, unchanged): swing peak within ±0.05 Hz of theory and string-pull peak within ±0.10 Hz of twice that.
  - Pass B (short ringdown): if A fails but the file contains at least 5 consecutive clean, steady swings (each at least 4× the noise, each period within 10 % of the others) and their timed frequency is within ±0.05 Hz of theory, B5 is recorded as "passed on a short ringdown" and the paper states the limitation (see `docs/limitations.md`).
  - Otherwise: FAIL, logged with the cause. The bridge frequencies are then reported as "B5 not validated".
  - Why timing for B: a 5 s window cannot separate frequencies closer than about 0.2 Hz in a spectrum, which is too coarse for ±0.05 Hz. Timing each swing directly is much sharper.
  - Both runs are always reported. Run 1 stays a FAIL whatever run 2 does. The length used is the length measured with a ruler, never the default.
- Code for B (`analysis/pendulum_ringdown.py`, called by `pendulum_check.py` only when A fails) written and tested by Claude at Rydvan's request, on made-up swings with known answers.

### 2026-10-20 — B5 run 2 (FAIL) and the prediction for run 3, written before run 3 was recorded

- Run 2: `data/calibration/20261020_0923_bench_pendulum.csv`, 40 s, 8,029 samples, 200.000 Hz, 0 dropped. Same floss/pen setup, swing pulled about 4-5 cm and released. Checked with `--length 0.24`. Rydvan reports L = 24 cm (he looked at it after the first check; no ruler photo, so L is only as good as that reading).
- Result: pass A not met (peaks x 1.174, y 2.329, z 1.171 Hz; theory 1.018 and 2.035 Hz). Pass B not met (z: 9 clean swings in 7.8 s at 1.158 Hz, 14 % above theory). **FAIL.** Run 1 and run 2 both stay in the repo.
- What is clean about it: the swing lasted about 14 s, the frequency is steady at 1.16-1.18 Hz in every time window whatever the swing size, and early in the run the y axis peaks at exactly twice the x axis (2.328 vs 1.164 Hz). The chain gives a consistent frequency. It is just not the theory frequency.
- 1.17 Hz equals L = 0.181 m, not 0.24 m. Two explanations: (1) L was misjudged; (2) the apparatus adds a restoring force. The sensor with headers, floss and tape weighs only a few grams, and four jumper wires hanging from it behave like weak springs, which raises f and damps the swing. Explanation (2) is a hypothesis, not a finding.
- **Prediction, written before run 3:** if the wires are the cause, hanging a heavier bob (about 30-50 g, e.g. a small stack of coins taped behind the board, clear of the pins) will pull f down toward theory, because gravity then dominates the wires. Rough estimate: the wires add about 13 s^-2 to omega^2, compared with 41 s^-2 from gravity at L = 0.24 m; 30 g or more should bring f to within about 0.02 Hz of 1.018 Hz. If f stays near 1.17 Hz with the heavy bob, the wire explanation is wrong and L or something else must be examined.
- Run 3 procedure: heavy bob taped rigidly so nothing wobbles; L measured with a ruler to the middle of the whole bob, **told to Claude and written here before recording**; wires slack; pull 4-5 cm; `capture.py bench pendulum 40`; then `pendulum_check.py ... --length <that L>`. The pass rule is unchanged (A, then B). Whatever run 3 gives is reported next to runs 1 and 2.
- Honest note for the paper: three runs were needed; the first two used a bob too light for the wires.

- **Run 3 setup, logged before recording (20 Oct, about 09:42):** Rydvan could not attach the extra weight (tape would not hold it), so the heavy-bob test of the wire hypothesis was **not** done. Run 3 is a repeat of the run 2 setup (floss on a pen, no added mass, slack wires). L = **0.24 m**, measured by Rydvan, told to Claude before recording. Pass rule unchanged (A, then B). If run 3 fails, B5 is recorded as not passed, with the wire/light-bob explanation marked as an untested suspicion.

- **Run 3 (FAIL):** `data/calibration/20261020_0943_bench_pendulum.csv`, 40 s, 8,029 samples, 200.000 Hz, 0 dropped. L = 0.24 m, no added mass. Peaks x 1.163, y 1.163, z 1.176 Hz (theory 1.018 Hz). Pass A not met. Pass B not met: x had 8 clean swings in 6.8 s at 1.175 Hz, 15 % above theory. The swing decayed over about 16 s.
- Runs 2 and 3 agree: z peak 1.170 and 1.167 Hz, within 0.3 % of each other. The readout is repeatable; it is the theory value that it does not match.
- **B5 status: NOT PASSED (3 runs, all kept).** The wire/light-bob explanation is an untested suspicion: the weight test could not be done (tape would not hold the weight). No claim is made that B5 validated the readout. Bridge frequencies are reported with this stated (see `docs/limitations.md`). Rydvan's decision, 20 Oct: proceed to the bridges and report B5 as not passed.
- Data-handling fix found while checking run 3: the first lines of a capture can be leftovers from the Uno's previous run (it keeps streaming until the port is reopened and it restarts). In run 3 three such lines sat above the title line and made the loader report a 4,335 s recording with 859,031 dropped samples. The frequency was not affected, but the same would have happened on bridges recorded one after another. `common.load` now reads data only after the `t_us,ax,ay,az` title line and counts anything above it as non-data. Raw files untouched. Old B3/B4 files give identical numbers (Sep 26 and Oct 14: median 5000 us, 4992/5008, 0 dropped); self-test ALL PASS (12 of 12). Run 1 had 16 such lines, run 3 had 3, run 2 none.

- **Supplementary check (not part of the pass rule), prediction written before it is done (20 Oct):** time 10 full swings of the same pendulum by eye with a phone stopwatch, counting back-and-forth swings, repeated 3 times. If the sensor's 1.17 Hz is the real swing rate, 10 swings take about **8.5 s**. If the theory value 1.018 Hz were the real rate, they would take about **9.8 s**. This does not change the B5 status above; it only tests whether the readout or the theory value is the one that is off.

- **Setup caveats (Rydvan, 20 Oct, with four photos):** L is approximate: he only had a 10 cm triangle ruler, so L = 0.24 m is a rough reading (about +/-2 cm; the photos have no scale in the frame and strong perspective, so they cannot give a better number). The floss is not knotted: it is taped to the pen tip and to a small tape tab on the board. From the photos: the four jumper wires run from the Uno on the desk top down to the board and hang in long loops, so their weight and tension act on the board; a loose floss tail and thread ends hang below the board near objects on the floor; the board hangs close to the desk face and objects below. So the "pendulum" is not a single small mass on a single string.
- **Supplementary stopwatch check (prediction was logged first):** 10 full swings took 7.99, 8.31 and 8.55 s (mean 8.28 s, so about 1.21 Hz, uncertainty about +/-0.04 Hz from reaction time and counting). Predicted 8.5 s if the sensor's 1.17 Hz is the real swing rate, 9.8 s if theory's 1.018 Hz were. Result: the sensor's frequency agrees with the independent stopwatch; theory's value is clearly excluded. This does not change the B5 status (NOT PASSED by the rule). It shows the readout agrees with an independent measurement of the same swing, and that the mismatch is with the single-point-mass theory for this apparatus, not with the sensor chain. Untested suspects for why the apparatus swings faster than theory: the weight and tension of the wires (several grams, more than the board), the loose floss ends, and the untied attachment.
- Next time B5 is repeated: knot the floss, tie the wires to the floss so they hang from the same pivot with only a small slack loop near the board, trim the loose floss ends, and use a heavier bob if the tape can hold it.

- **Stopwatch check, all six timings (20 Oct, ~09:55):** 10 swings took 7.99, 8.31, 8.55, then 8.69, 8.62, 8.92 s. Mean 8.51 s, SD 0.33 s, so f = 1.175 Hz, uncertainty about +/-0.02 Hz from the scatter (plus a possible small counting/reaction bias). Sensor 1.17 Hz (8.55 s per 10 swings); theory 1.018 Hz (9.8 s). Every timing is used; none dropped. (A misunderstanding in the chat about which of the timings had been sent was cleared up: the first three sent were the first three taken.) Rydvan noted the swing looks much faster at the very end, when it is tiny; wires dragging is his suspicion, not tested.
- **Run 4, prediction logged before recording (20 Oct, ~09:57):** rig completely unchanged from runs 2 and 3 (floss on pen, same wires, no added mass, L about 0.24 m by rough ruler). Capture 30 s. Prediction: the peak will again be near 1.17 Hz (not 1.018 Hz), so pass A and B will again fail against theory. Purpose: one more repeatability point. Pass rule unchanged. Result will be reported whatever it is.

- **Runs 4 and 5 (FAIL, as predicted):** Rydvan captured twice, 30 s each, rig unchanged, L about 0.24 m. Run 4 `20261020_0957_bench_pendulum.csv` (6,030 samples, 200.000 Hz, 0 dropped): released at the start, very clean ringdown, peaks x 1.164 / y 1.166 / z 1.163 Hz, pass B found 14-15 clean swings at 1.165 Hz. Run 5 `20261020_0958_bench_pendulum.csv` (6,031 samples, 6 stale lines ignored, 0 dropped): peaks 1.161 / 1.160 / 1.169 Hz; pass B 7 swings at 1.163 Hz. Theory 1.018 Hz, so pass A and B fail on both. Rydvan checked only run 5 on his Mac; Claude checked run 4 independently; both are reported.
- **B5 summary, five runs, all kept:** run 1 rough swing (FAIL); runs 2-5 clean swings at z 1.170, 1.167, 1.163, 1.164 Hz (repeatable to about 0.4 %) but 14-15 % above theory, and the stopwatch agrees with the sensor. B5 status stays **NOT PASSED** by the rule written before run 2.

- **Note on `results/frequencies.csv` (append-only, not edited):** the rows analysed before the loader fix show a wrong `dropped_lines` and `n_samples` for run 1 (0857: 2,425,934 "dropped", from leftover lines above the title line) and run 3 (0943: 859,031). Those two numbers are artefacts of the old loader and should be ignored; the peaks in the same rows are unaffected (3 stale samples out of 8,000). Rows for runs 2 and 5 and everything analysed after the fix are correct.
- Snapshot after B5 (this entry's commit): code `analysis/pendulum_ringdown.py` (new), `common.py` loader fix, `pendulum_check.py` pass B, `selftest.py` (12 of 12), `analyse_bridge.py --axis`, `docs/limitations.md`, five pendulum recordings and their figures.

## 2026-09-__ — B5, pendulum validation

- String length ____ m, predicted f = ____ Hz from T = 2π√(L/g)
- Measured peak: ____ Hz. Second peak at ____ Hz (expect 2×)
- Result:
