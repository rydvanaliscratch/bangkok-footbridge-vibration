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

## 2026-10-20 — B1 on site (via the logger banner) and orientation of the mounted sensor

- Plan change, Claude's suggestion (Rydvan agreed by doing it): instead of uploading the scanner at the bridge and then re-uploading the logger, B1 was checked by the logger's own start-up test, which reads WHO_AM_I and prints `# WHO_AM_I ok (0x68)` at the top of every recording (`firmware/logger/logger.ino`). Same check, same wires and chip, and done after the transport and taping.
- `data/raw/20261020_1435_bridge01_tilt_orient.csv`, 10 s, sensor taped in place at bridge01 (no flat surface, so mounted on its edge). Banner: `WHO_AM_I ok (0x68)`. B1: **PASS**.
- File check: 2,032 samples, 200.000 Hz, 0 dropped, largest gap 5,008 us, 0 stale lines. Means: x -16,579 counts (-1.012 g), y +319 (+0.019 g), z +760 (+0.046 g); total 1.013 g. So **the X axis points straight down/up (vertical)**; the board is within about 3 degrees of square. Noise SD x 17.7, y 16.0, z 27.6 counts, the same as on the bench (16.5 / 16.7 / 26.2): the mounting is quiet.
- **Analysis for this mounting: `--axis x`** for ambient, decay and control. Same orientation to be used for the pavement control and at every bridge; if any bridge differs, it is logged.

## 2026-10-20 — bridge01 ambient (first field recording)

- Rydvan's field notes, 14:38-14:53: **bridge01 = the first Ratchadaphisek bridge**, span 17 m (his reading; to be confirmed with two slow measurements, end column to middle column). Clear weather, very strong wind (his umbrella was blown about), heavy car and truck traffic on the road below ("too many to count"), 8 pedestrians counted. Board mounted on its edge on the concrete at the deck side, X axis pointing down, laptop on the deck beside the sensor under an umbrella. Order differs from the written plan (Charoen Nakhon first): Ratchadaphisek was done first.
- Photo notes: a blade of grass lay across the board's header pins (blown by the wind) and had to be removed; the wind can also move the cable and umbrella, so the wind is a noted source of extra noise.
- `data/raw/20261020_1437_bridge01_ambient.csv`: 179,864 samples, 899.3 s, 200.000 Hz, 0 dropped, largest gap 5,008 us, 9 non-data lines (restart bytes). RMS x 1.37 mg (sensor noise alone about 1.08 mg), so the bridge signal is small and relies on the 15-minute averaging.
- Claude's preview of the spectrum (default settings, `--axis x`, 1-20 Hz, run in a scratch folder, nothing added to the repo): one peak at 5.187 Hz (95 % range 5.178-5.201 Hz), inside the sealed prediction for 17 m spans (3.76-5.875 Hz). **Not yet a finding:** it counts only if it is at least 10x stronger than on the ground control (rule fixed before data) and Rydvan runs the analysis himself for the record.

- **bridge01 first decay recording, 15:02:** `data/raw/20261020_1502_bridge01_decay.csv`, 299.9 s, 200.000 Hz, 0 dropped. Five heel-drops at about 4, 46, 87, 129 and 171 s (40 s apart, as planned). Rydvan's notes: a man walked onto the bridge right after drop 1; for drops 2 and 4 a person reached the 10 m zone near the end of the 20 s; the data also show raised activity at about 110-128 s and 150-165 s.
- **Stray file:** `data/raw/20261020_1501_bridge01_ambient.csv`, only 3.5 s (697 samples), started 15:01:59 asking for 900 s and stopped at once: the wrong command was started before the decay command. Kept, not deleted, not renamed; not to be used as an ambient recording.
- Claude's preview of `damping.py` on the decay file (`--f 5.187`, axis x, not saved): the program found **1 of the 5 drops** (87.8 s): 23 peaks, ring 5.13 Hz, zeta 0.57 %, fit R2 0.92; no spread possible from one drop. Diagnosis: in the band around 5.19 Hz all five drops are 16-20x the typical in-band level (strong ringing), but `find_drops` tests the unfiltered signal against 8x its typical level, about 9 mg here, and Rydvan's drops peak at about 7-9 mg unfiltered, so only the hardest passed. This is a property of the detection rule and the strength of the drops, not a missing signal.
- Decision to be made openly: (a) redo the decay with harder drops at midspan so the unchanged rule finds them, and keep this file; or (b) change the detection rule to use the band-passed signal, which would be an analysis change made after seeing the data and must be logged and applied to every bridge. Claude recommends (a) first.

- **bridge01 second decay recording, 15:10:** `data/raw/20261020_1510_bridge01_decay.csv`, 299.8 s, 200.000 Hz, 0 dropped, 18 non-data lines (restart bytes). Rydvan did the drops harder and nearer the sensor, and waited for walkers to leave the 10 m zone after drops 1, 2 and 4 (his notes). In-band (3.6-6.7 Hz) bursts at about 1.4, 41.8, 111.8, 153.6, 210.4 and 264.7 s, i.e. six drops, 40-70 s apart because of the waiting.
- Claude's preview with the unchanged `damping.py` rule (`--f 5.187`, axis x, not saved): the unfiltered 8x threshold was 11.8 mg (background higher than in the first file, wind and traffic), the drops peaked at about 7.5-11.7 mg in band, and the rule found only one burst (212.9 s), which was **not usable** (fewer than 5 clear peaks). Harder drops did not lift the unfiltered bursts above the rule: the bridge is stiff and the heel-drops are light.
- Conclusion for the log: redoing again would not help; the detection rule in `find_drops` (8x the typical level of the unfiltered signal, designed on 50 mg synthetic drops) does not suit this bridge. Both decay files are kept. Decision postponed to tonight at home and to be made in the open: change `find_drops` to look at the band-passed signal (the one the damping fit uses) with the same factor 8, as an analysis change made after seeing data, applied to every bridge, with the old rule's result also reported. Damping is a secondary result; frequency does not depend on it.

## 2026-09-__ — B5, pendulum validation

- String length ____ m, predicted f = ____ Hz from T = 2π√(L/g)
- Measured peak: ____ Hz. Second peak at ____ Hz (expect 2×)
- Result:

### 20 Oct, 15:45 — bridge01 control + span
- Control recorded 15:38 at the base of the stairs (board on its edge, X vertical, same as deck), 300 s, 200.000 Hz, 0 dropped. Chosen because the stair base exists on every bridge and sits on the ground; it is still attached to the structure, so any bridge vibration it picks up makes the 10x ground test harder to pass (conservative). Limitation to state in the paper.
- People on the stairs during the control: ~75 s (1 person up, another 10-15 s later), ~230 s (2 down), ~280 s (2 up).
- Preview (analyse_bridge.py bridge01 --axis x, ambient 1437): peak 5.187 Hz, 95% range 5.178-5.201 Hz, 113x the ground (rule >= 10x). Inside sealed prediction for a 17 m span (3.76-5.875 Hz).
- Span: full bridge ~34 m with a middle column, so two spans of ~17 m (Captain's reading, not yet tape-measured twice). Which span the sensor was on: to confirm.

## 2026-10-20 — bridge02 (second Ratchadaphisek bridge): orientation, ambient, decay

- Rydvan's description: second Ratchadaphisek bridge, 34 m long with one middle column, so two spans of about 17 m (his reading, not yet confirmed by slow measurements). Sensor mounted at the middle of one 17 m span (about 8.5 m from the middle column and from the end column), board on its edge, X axis pointing down, as at bridge01. Wind, traffic and pedestrian counts for bridge02: **not yet given, to be added from Rydvan's notes.**
- Recordings (all kept, nothing edited or deleted):
  - `data/raw/20261020_1602_bridge02_tilt_orient.csv`, 10 s. Banner `WHO_AM_I ok (0x68)`. 2,034 samples, 200.000 Hz, 0 dropped, largest gap 5,008 us. Means x -16,602 (-1.013 g), y -654 (-0.040 g), z -460 (-0.028 g): **X is vertical, so `--axis x`** as at bridge01. Noise SD x 17.8 / y 16.7 / z 28.5 counts, like the bench.
  - `data/raw/20261020_1603_bridge02_ambient.csv`, 900 s requested. 179,869 samples, 899.3 s, 200.000 Hz, 0 dropped, largest gap 5,008 us, 5 non-data lines (restart bytes), no clipping. RMS x 1.50 mg.
  - `data/raw/20261020_1619_bridge02_decay.csv`, 300 s. 59,980 samples, 299.9 s, 200.000 Hz, 0 dropped, largest gap 5,008 us, 8 non-data lines, no clipping.
- Checks by Claude on Rydvan's Mac, nothing written to the repo: all three files pass the basic checks (rate, dropped samples, gaps, clipping).
- **Z-axis drift in the ambient file:** the z mean rose from about -275 counts (first minute) to about 1,015 counts after roughly 5-12 minutes, then stayed flat. X moved only about 40 counts (-16,604 to -16,561). At bridge01 z moved from 765 to 797. Cause unknown (tape or board settling, or sensor warm-up are the candidates, not tested). Not a reason to rerun: the analysis axis is x and a slow drift is removed by the analysis. To be reported as it is.
- **Disturbed drop (Rydvan's field note):** someone walked by at the second drop. By time that is the drop at about 45 s. Claude's preview shows nothing unusual in the accelerometer at that drop (fit R2 0.986), but the accelerometer may not show a walker. Decision: the drop is kept and reported, flagged as "walker nearby", not removed. (Same rule as all drops: no result-tuning.)
- Rydvan's observation, untested: bridge01 carried far more mass than bridge02 (boards and plants on the deck). Recorded as a field observation only. Not used as an explanation for any difference in frequency until it is measured or looked up.
- **Claude's previews (scratch folder, not saved to results/, not findings):** ambient peak near 4.74 Hz, inside the sealed 17 m range (3.76-5.875 Hz). The unchanged `damping.py` rule (`--f 4.74 --axis x`) found 6 drops (at 3.7, 45.1, 87.4, 128.0, 205.6, 247.8 s), all usable, fit R2 0.93-0.99, zeta mean 1.20 %, SD 0.12 %. At bridge01 the same rule found only 1 of 5, so the detection-rule decision is still open and is not made by this file. Bridge01 5.19 Hz versus bridge02 4.74 Hz, both nominally 17 m: about 9 % apart, to be looked at with Rydvan's own results. Nothing counts until the ground control (at least 10x weaker) and Rydvan's own analysis runs.
- Next: bridge02 control at the base of the stairs (300 s, board on its edge, X vertical), then Claude checks the file.
- **bridge02 conditions (Rydvan's field notes, 20 Oct, said at 16:34):** 7-8 people on the bridge, meagre (light) wind, traffic on the road below about the same as at bridge01 ("give or take", i.e. heavy). Which recording the 7-8 people count covers (ambient, decay or both) is to be confirmed. Bridge01 had very strong wind, so wind is a difference between the two bridges.

### 20 Oct, 16:40 — bridge02 control, and Claude's preview analysis of bridge02

- Rydvan's notes: control recorded at the base of the stairs at 16:34, **nobody walked** during it. Done with two bridges for the day; the rest is on following days. Git commit to be done at home.
- `data/raw/20261020_1634_bridge02_control.csv`: 299.9 s, 59,980 samples, 200.000 Hz, 0 dropped, largest gap 5,008 us, 5 non-data lines. Means x -16,451 / y -257 / z -2,554 counts, so X is still the vertical axis but this board is tilted about 9 degrees more than at the deck (z -2,554 vs about +1,000); noise SD 16.9 / 17.1 / 26.8, the same as on the bench. Analysis uses `--axis x` for the control as well.
- **Claude's preview** (`analyse_bridge.py bridge02 --axis x`, run in a scratch copy, nothing added to results/ or figures/; **not the record**, Rydvan runs it himself at home):
  - Peak **4.741 Hz**, 95 % range 4.724-4.761 Hz, period 0.211 s.
  - Ground check: bridge is **33.2x** stronger than the ground at that frequency (rule: at least 10x) -> passes. (bridge01's recorded ratio in results/frequencies.csv: 113x.)
  - Damping from 6 drops: zeta 1.20 %, SD 0.12 %, fit R2 0.93-0.99, with the unchanged `find_drops` rule. Includes the drop at 45.1 s that Rydvan flagged (walker nearby).
  - Falls inside the sealed 17 m prediction (3.76-5.875 Hz). 95 % range overlaps twice walking pace (3.2-4.8 Hz). Below 5 Hz, so the European comfort check applies.
- Open point, not resolved: bridge01 5.187 Hz vs bridge02 4.741 Hz is a difference of about 9 %, far bigger than either 95 % range. Both spans are nominal 17 m from Rydvan's reading and neither has been confirmed by slow measurements yet, and conditions differed (wind, deck mass). No explanation is claimed.

## 2026-10-21 — bridge03 (first Charoen Nakhon bridge, about 25 m single span): orientation, ambient, decay, control

- Rydvan's description: first Charoen Nakhon bridge, about 25 m, single span (his estimate; **span not yet measured support to support**, so it is not yet usable in the span fit). Sensor at midspan, board on its edge, X down (same mounting as bridge01 and bridge02).
- Conditions (his notes, 21 Oct): ambient started 06:45 in morning sun, one person, moderate cars. Decay: people walking by were controlled so there was no real interference; car flow the same. Control (finished by about 07:38): people stepped on the base step at about 60 s, 75 s and 260 s.
- Recordings:
  - `20261021_0643_bridge03_tilt_orient.csv`, 10 s: WHO_AM_I ok (0x68); 2,035 samples, 200.000 Hz, 0 dropped; x -16,602 (-1.013 g), so **X vertical**, `--axis x`.
  - `20261021_0644_bridge03_ambient.csv`: 179,881 samples, 899.4 s, 200.000 Hz, 0 dropped, max gap 5,008 us, no clipping. Board did not move (Rydvan's worry): biggest 5 s-to-5 s step in mean x 3.7 counts, y 4.0, z 7.7; largest sample deviation 84 counts; total gravity 1.010-1.020 g throughout; x noise SD 18.7 (first 30 s) vs 16.8 (last 30 s). Z crept 93 counts (about 0.3 degrees) over 15 min. X RMS about 1.06 mg, i.e. the sensor noise floor: the bridge signal shows only in the 15-min averaged spectrum.
  - `20261021_0707_bridge03_decay.csv`: 59,983 samples, 299.9 s, 200.000 Hz, 0 dropped, 10 non-data lines, no clipping.
  - **Five control files, all kept:** `0716` (100 bytes, no data lines: the recorder started and stopped at once), `0722` (222 s of a 300 s request, large disturbances in the last minutes), `0726` (23 s), `0730` (72 s, board apparently moved: x mean -14,380, SD 4,319), `0732` (full 299.9 s, 200.000 Hz, 0 dropped, 5 non-data lines). Why the first four were stopped: **to be added from Rydvan.** The analysis program takes the newest control file by default, which is `0732`; that is the control used below.
  - In `0732`, three bursts match Rydvan's step times: x noise SD per 10 s jumps from 16-17 counts to 239 / 341 counts at about 60-80 s and to 709 counts at about 250-260 s; the other 10 s blocks are at the sensor noise (16-20 counts).
- **Claude's preview** (`analyse_bridge.py bridge03 --axis x` in a scratch copy, nothing written to results/ or figures/; not the record, Rydvan runs it himself):
  - Ambient peak **3.339 Hz** (95 % range 3.334-3.350 Hz), period 0.299 s. Inside the sealed 25 m prediction (2.56-4.0 Hz). The decay file's own spectrum peaks at the same place (3.32 Hz).
  - **GROUND CHECK, rule as fixed before data: bridge is 1.6x stronger than the ground at this frequency. That is below the 10x rule, so by the rule written in advance the peak is NOT confirmed as the bridge's.** Result stays as it is.
  - Why, from Claude's exploratory checks (post hoc, not the rule, shown only to understand it): the footsteps on the step inflate the control. With the step windows removed from the control (50-90 s and 245-275 s) the ratio is 7.3; with wider removal 6.5; using only the quiet 100-240 s 6.8. All still under 10. In the quiet part of the control the power near 3.34 Hz is only about 1.5x the sensor's flat noise floor, and the ambient peak is only about 10x that floor. So with this weak excitation a 10x ratio is out of reach even with a perfect control: the rule is limited by the sensor noise floor, not only by the control.
  - Damping with the unchanged `find_drops` rule: **0 of the drops found.** Band-passed (2.34-4.34 Hz) bursts exist at about 2, 43, 85, 127, 168 and 226 s (12-18x the typical in-band level, 3.1-4.5 mg), i.e. 6 drops. Same pattern as bridge01: the unfiltered rule (8x typical, about 6 mg here) misses drops that are clear in the band. Bridge02 needed no change. This is evidence for the pending decision on the detection rule (not decided here).
- Open: how to report the bridge03 ground check. The honest default is to report it as it came out (rule failed, exploratory ~7x), not to change the rule. A fresh control with nobody on the steps would be a new recording, decided in the open and logged. Not decided.

- **Why the first four bridge03 control files were stopped (Rydvan, 21 Oct 07:42):** `0716` had no signal at all (nothing recorded). In the next three (`0722`, `0726`, `0730`) the module came unstuck from the slab. The stair base at this bridge seems to be disconnected from the actual stair and the floor, so it is shaky, and any step on it shows up extremely strongly. This is his field observation (not measured): it fits the data, where `0732` is quiet (noise-floor level) except for the three step bursts at about 60-80 s and 250-260 s.
- **Decision announced before recording (Rydvan, 21 Oct 07:42):** after school he will record a second control on the base step on the **other side** of bridge03. Logged here in advance, so the choice is visible. Rules for it: `0732` stays in the record and is reported next to the new one (not replaced); the 10x rule is not changed; the new file is judged by the same rule; the result is reported whichever way it comes out; its date, time, who walked and the reason for the new placement go in the log.

## 2026-10-23 — bridge03 second control (other side's base step)

- Rydvan, 10:36: ran another control; he did not think the module was holding on right. (Placement details, who walked, and whether the step was pressed first: **to be added from Rydvan.**)
- `data/raw/20261023_1030_bridge03_control.csv`, started 10:31:00: 59,966 samples, 299.8 s, 200.000 Hz, 0 dropped, largest gap 5,008 us, 0 non-data lines, no clipping. Checked by Claude from a staged copy (the Mac shell was unavailable); file not changed.
- **Board was creeping, as Rydvan suspected.** Gravity direction rotated slowly through the whole file: y mean from about +243 to +1,261 counts (range of 5 s block means 1,034), z from about -508 to -320, x from -16,560 to -16,499; largest single 5 s step 85.6 counts (y, about 180 s). So no fall and no sudden jump, but a steady tilt of roughly 3-4 degrees: the mount was not rigid. Total gravity 0.998-1.018 g. X noise SD per 10 s is 16-18 counts throughout (no step bursts, nobody stepped on it, or nothing registered).
- **Ground check, rule as fixed before data (bridge peak 3.320 Hz in the 21 Oct ambient file vs this control): bridge is 6.6x stronger than the ground. Below the 10x rule, so the rule is still not met.** The earlier control `20261021_0732` gave 1.4x on the same calculation (1.6x in the program's own run at 3.339 Hz); with its step windows removed, about 7x (exploratory). The new control's power near the peak is about 1.6x the sensor's noise floor, consistent with the earlier quiet part. If the loosely attached board under-recorded the ground, the true ground power was higher and the true ratio lower, so the loose mount cannot explain a failure to reach 10x; it could only flatter this number.
- Reading, not a claim: the ratio is limited by the sensor's own noise floor (ambient peak is only about 10x the floor), so with this weak shaking 10x may not be reachable with any control. The rule is not changed. Both controls are reported side by side. The 3.32 Hz peak also appears in the bridge03 decay recording, which supports it as the bridge's but does not replace the rule.

- **Decision announced before recording (Rydvan, 23 Oct 10:42):** a third bridge03 control will be recorded, because the 23 Oct control's board was not held rigidly (it crept about 3-4 degrees). Claude had suggested not repeating it (risk of looking like a search for a pass); Rydvan decided to repeat it, so the reason is logged first. Rules: both earlier controls (`20261021_0732`, `20261023_1030`) stay in the record and are reported next to the new one; the 10x rule is not changed; the new file is judged by the same rule; the result is reported whichever way it comes out; no further repeats are planned (if the third also fails, bridge03 is reported as not meeting the ground rule). Placement, mount check, time and who walked to be logged with the recording.

- **Control attempts on 23 Oct after 10:42 did not succeed (Rydvan, written 23 Oct 11:58):** he tried again but "it was too hot" (his words; what the heat did to the tape/board is to be added). Two files, both kept, neither usable as a control:
  - `data/raw/20261023_1040_bridge03_control.csv`: stopped after 2.4 s (480 samples), 12 non-data lines. Nothing to analyse.
  - `data/raw/20261023_1043_bridge03_control.csv`: 52.7 s (10,540 samples, 200.000 Hz, 0 dropped) of 300 s requested. The board moved a lot during it: y mean went from about -58 to +11,197 counts and z from about -428 to -10,114 counts, i.e. it turned through a large angle (probably came off the surface). Checked by Claude from a staged copy.
- **Commit and teaching request (Rydvan, 23 Oct 11:58):** commit what exists now. Rydvan wants this research to be mainly his own: to be taught what each document is for, what the research is about, which values to look for and what they mean, what the code does, and to be sure no API keys/secrets are in the repo before it goes public. Secret scan by Claude (working-tree text files, `.git/config`): no keys, tokens or passwords found; the remote URL holds only the username. **Git history scan still to do.**

## 2026-10-24 — bridge03 control, further attempts (morning, before 08:00)

- Rydvan's notes, 24 Oct: did the bridge03 control again; the board "came off in about 255 s" and he re-stuck it; a person walked up at about 275 s. Third day on this and the board "keeps unsticking". (He had asked beforehand whether he could hold the module by hand; Claude advised against it, because the hand's own tremor and body sway fall in the 1-12 Hz range and would be recorded; he did not hold it.)
- Two files, both kept, checked by Claude from staged copies, files not changed:
  - `data/raw/20261024_0738_bridge03_control.csv`: 201.3 s of 300 s requested (200.000 Hz, 0 dropped). Quiet (x noise 15-17 counts) for about 180 s with a slow tilt creep (y +145 to +555 counts in 180 s), then the board came off at about 185-190 s (y jumps to +11,677). Not usable as a 300 s control; stopped.
  - `data/raw/20261024_0744_bridge03_control.csv`: 299.9 s, 59,982 samples, 200.000 Hz, 0 dropped, largest gap 5,008 us, 7 non-data lines, no clipping. X noise 16-17 counts (the sensor noise floor) for the whole file except one event: x was more than 200 counts off baseline between **237.2 s and 249.3 s** (10 s noise block 240-250 s: SD 846), after which the readings returned to the original orientation (y -173 at start, +257 at end). That event is the board coming loose and being re-stuck. His times (255 s, 275 s) are about 10-15 s later than the event in the data; the likely reason is that his count started a few seconds after the recorder started (not tested). **The person walking up at about 275 s left no visible trace** (x noise 16-17 counts in all blocks after 250 s). Before the event the board crept slowly (y -168 to +252 over about 220 s, roughly 1.5 degrees).
- **Ground check, rule as fixed before data (bridge peak 3.320 Hz, 21 Oct ambient file, vs this whole file): 0.7x.** The event dominates the whole-file spectrum, so the rule as written fails badly on this file. This is the number for the rule.
- Exploratory only (post hoc, to understand it, not the rule): with the event removed the ratio is about 8x (8.1 with 225-255 s removed; 7.9 with 220-260 s removed; 7.8 using only the first 220 s). The control's power near 3.32 Hz is about 1.3x the sensor's noise floor in the quiet part, and the ambient peak is only about 10x that floor, so a ratio of 10x is at the edge of what any control could show here.
- bridge03 controls so far: `0732` (steps) 1.4-1.6x; `23 Oct 1030` (creeping board) 6.6x; `24 Oct 0744` (board came loose once) 0.7x on the whole file, about 8x with the event removed. None meets the 10x rule as written. The rule is unchanged. All files kept. Failed short attempts: `0716`, `0722`, `0726`, `0730`, `23 Oct 1040`, `23 Oct 1043`, `24 Oct 0738`.
- **Mounting (Rydvan's account, 24 Oct):** at bridge01, bridge02 and the bridge03 ambient run the board was held with "one strip, flat under" (exact meaning to be confirmed: one strip of masking tape, laid flat), in shade (umbrella at the two Ratchadaphisek bridges; the bridge03 ambient started about 06:40, already cool). The failed bridge03 controls were in sun, on a rough, dusty concrete step, with several strips taped around the board's edges (photo, 24 Oct 08:25). Hypothesis, not tested: heat and sun softened the tape glue and/or the dusty rough surface gave poor adhesion. Claude's advice: shade, clean the spot, press-test, tape the cable behind the board, record early.

## 2026-10-24 — spans, and plan to remeasure (Rydvan, 11:43)

- Saved readings (`data/span_measurements.csv`, 13 Oct, outer face of one support column to outer face of the other): candidate A 24.2, 24.4 (iPhone Measure, walked fast), 25 (Apple Maps); C 25.4, 25.4 (iPhone, slow), 25 (Maps); B 22.7, 23.4 (iPhone, phone overheating) and 20 (Maps), marked unreliable; D (with middle column) 17 and 17 end-to-middle, 34 whole. Rydvan's working values: about 24 m (6-lane single spans) and 17 m. The "24 m" is not itself in the saved file; where it comes from is to be added.
- Online search (24 Oct) found no published length for any of these footbridges, only general road pages; the spans rest on Rydvan's own measurements.
- **Decision announced before measuring:** Rydvan will remeasure the 25/24 m bridges to confirm, with the iPhone Measure app, walking slowly and carefully, early morning (no heat), and uses "outer face to outer face" of the support columns. Rules: all new readings are added as new rows (nothing overwritten); each span measured at least twice; the spread is reported as the uncertainty. Caveat for the paper: the textbook formula uses the distance between the supports, which is usually a little shorter than outer-face-to-outer-face (by about a column width), so L is a slight overestimate; with f proportional to 1/L^2, a 1 m error on a 17 m span changes the expected frequency by about 12 %, as large as the 9 % gap between bridge01 (5.187 Hz) and bridge02 (4.741 Hz), so the spans must be known to better than about 0.3 m before that gap is interpreted.
- `data/bridges.csv` and `data/sessions.csv` currently contain only their column headings (no bridge IDs or spans); to be filled once the spans are confirmed.
- **bridge04 files exist, not yet checked or logged** (seen in the folder on 24 Oct 11:43): `20261024_0809_bridge04_tilt_orient.csv`, `20261024_0810_bridge04_ambient.csv`, `20261024_0824_bridge04_ambient.csv`. Rydvan's notes for them (which bridge, span, weather, people, why two ambient files, and decay/control) to be added.
- **Git history secret scan done (Claude, 24 Oct 11:50):** all 8 commits, all files, searched for GitHub/OpenAI/AWS/Google/Slack key patterns, private keys, and `password`/`secret`/`api_key` assignments. No secrets found. The only pattern hit is the sentence in `docs/independence-guide.md` that says GitHub asks for a personal access token (instructions, no token). No `.env`, key or credential files were ever committed. The only commit author is the GitHub no-reply address (`...@users.noreply.github.com`), not a personal email. `.git` is 1.9 MB; raw data is 44 MB, within GitHub's limits. Still to repeat right before the repo is made public (new commits since).

## 2026-10-25 — bridges 04-06 session, start (Rydvan, 06:24)

- **Mounting change from this session on:** Rydvan added tape to hold the cable (wires) to the surface behind the board, so the cable's weight and movement no longer pull on the board. Seems to be holding (his words, 06:24). This is a change from bridge01-03 and the 23-24 Oct controls, so it is logged as the point from which the cable is strain-relieved.
- Conditions at start: 06:24, light traffic. Bridge numbers for today: bridge04 to bridge06 (the 24 Oct bridge04 files `0809` tilt_orient, `0810` ambient, `0824` ambient are still unchecked; whether today redoes bridge04 or adds to it is to be confirmed).
- **bridge04 recordings, 25 Oct (checked by Claude at 06:47; files not changed):**
  - `20261025_0624_bridge04_tilt_orient.csv`: 2,035 samples, 200.000 Hz, 0 dropped; x -16,596 counts (-1.013 g), so **X vertical, `--axis x`**; noise SD 17.0 / 16.6 / 31.8.
  - `20261025_0625_bridge04_ambient.csv` (started 06:25:14): 179,880 samples, 899.4 s, 200.000 Hz, 0 dropped, largest gap 5,008 us, 11 non-data lines (restart bytes), no clipping. Board stable: range of 5 s block means 19 counts on x, 114 on y, 336 on z (about 1 degree of z creep); x noise 17-19 counts every minute. Rough spectrum (not the analysis): strongest peak near 3.17 Hz, inside the sealed 25 m prediction (2.56-4.0 Hz); its power is about 32x the sensor's noise floor (bridge03 was about 10x). Conditions per Rydvan: 06:24-06:25, light traffic, cable now taped behind the board.
  - `20261025_0641_bridge04_decay.csv` (started 06:41:23): 59,984 samples, 299.9 s, 200.000 Hz, 0 dropped, no clipping. Band-pass bursts at about 2, 44, 85, 126 and 169 s, i.e. 5 heel-drops about 41 s apart, then quiet to the end. The file's own spectrum peaks at 3.17 Hz, the same as the ambient. The unchanged `find_drops` rule was not run here.
  - Control not yet recorded at the time of this entry. Span of this bridge to be added from Rydvan's measurement.
- **Claude's preview analysis of bridge04** (`analyse_bridge.py bridge04 --axis x`, scratch copy, nothing written to results/ or figures/; not the record, Rydvan runs it himself; 25 Oct 06:50): ambient peak **3.158 Hz**, 95 % range 3.154-3.162 Hz, period 0.317 s, inside the sealed 25 m prediction (2.56-4.0 Hz). **No control yet, so the 10x ground check cannot be done.** Damping with the unchanged `find_drops` rule: **0 drops found**, although 5 drops are visible in the band-passed signal (about 2, 44, 85, 126, 169 s). The 95 % range sits just below twice walking pace (3.2-4.8 Hz) as the program defines it (3.158 vs 3.2 Hz): near the edge, to be stated carefully. Detection-rule tally so far: bridge02 6 of 6 found; bridge01 1 of 5 and 0 of 6 usable; bridge03 0 of 6; bridge04 0 of 5. Decision on `find_drops` still open.
- **Decision announced before recording (Rydvan, 25 Oct 06:55):** he will try another bridge03 control (a fourth full-length attempt after `0732`, `23 Oct 1030`, `24 Oct 0744`), with the cable now taped, the spot cleaned, in shade and early morning. Claude's earlier advice was not to repeat it: the ratio is probably limited by the sensor noise floor (bridge03 ambient peak only about 10x the floor), so even a perfect control may not reach 10x, and repeated tries can look like a search for a pass. Rydvan decided to repeat it. Rules, stated in advance: all earlier controls stay in the record and are reported next to the new one; the 10x rule is not changed; the new file is judged by the same rule on the whole file (events inside it are not cut out for the rule); the result is reported whichever way it comes out; **if this one is also below 10x, bridge03 is reported as not meeting the ground rule and no further bridge03 controls are recorded.** Placement, time, shade, tape and who walked to be logged with the recording.
- **bridge04 control recordings, 25 Oct (checked by Claude at 07:32; files not changed):** three files, all kept.
  - `20261025_0703_bridge04_control.csv`: 273.8 s of 300 s requested, 200.000 Hz, 0 dropped. Quiet (x noise 16-17 counts) until about 260 s, then x noise 51-62 counts and a z shift in the last 10-15 s (z block means 576 to -402 over the file): something disturbed it at the end. Port was `/dev/cu.usbmodem1101` (a different USB socket than the others).
  - `20261025_0713_bridge04_control.csv`: 158.0 s of 300 s requested, 200.000 Hz, 0 dropped. The board moved in the first 10 s (y -2,599 to about -2,590 after a 298-count step), then stayed stable, x noise 16-17 counts.
  - `20261025_0725_bridge04_control.csv`: **299.9 s, 59,983 samples, 200.000 Hz, 0 dropped, no clipping**; x range of 5 s block means 7 counts, y 49, z 53; x noise 16-17 counts in every 10 s block (the sensor noise floor): a clean, firm control.
  - **Ground check, rule as fixed before data (bridge04 ambient peak 3.158 Hz, `analyse_bridge.py` in a scratch copy): bridge is 32.0x stronger than the ground with `0725` (the newest, full-length file), 24.6x with `0703` and 27.3x with `0713`. All three are above the 10x rule: the 3.158 Hz peak is confirmed as the bridge's.** Control power near the peak is only about 1.2-1.9x the noise floor in each file, so the ratio here is limited by the ambient peak (about 34x the floor), not by the control. Reasons the first two files were stopped, spot, tape, shade and who walked: to be added from Rydvan's notes.
- **Why `0703` and `0713` were stopped (Rydvan, 25 Oct 07:33):** the mounting did not hold in those two, so he stopped them; at the third attempt (`0725`) it "finally" held properly. This agrees with the data (disturbance at the end of `0703`, board shift at the start of `0713`, nothing in `0725`). Which change made it hold (spot, tape, cable, shade) is to be added. The ground-check ratios of all three files (24.6x, 27.3x, 32.0x) are reported; the full-length `0725` is the one used by default.

## 2026-10-25 — comparison with the sealed predictions (Claude's previews; Rydvan has to run the real analysis for the record)

- Peaks (ambient, `--axis x`): bridge01 5.187 Hz (95 % 5.178-5.201), bridge02 4.741 Hz (4.724-4.761), bridge03 3.339 Hz (3.334-3.350), bridge04 3.158 Hz (3.154-3.162). Only bridge01 is in `results/frequencies.csv` and `results/damping.csv` so far; bridges 02-04 are previews run in scratch copies until Rydvan runs `analyse_bridge.py` himself (`--axis x`; for bridge01 use `--ambient` 20261020_1437 because a 3.5 s stray ambient file is the newest).
- Against `predictions/predictions_20261014.md` (17 m: 4.71 Hz, range 3.76-5.875; 25 m: 3.2 Hz, range 2.56-4.0): bridge01 +10 %, bridge02 +0.6 %, bridge03 +4 %, bridge04 -1.3 %. All four are inside their ranges. The range (x0.8 to x1.25) is wide, so being inside it is a weak test. The point predictions are close.
- H1 (all between 2 and 6 Hz): holds for 4 of 6 bridges so far. H2 (not wrong unless all six are above 5 Hz or any is inside 1.6-2.4 Hz): not wrong so far (3 of 4 are under 5 Hz, none inside 1.6-2.4 Hz). H3 (f(17 m) / f(25 m) about 1.5, predicted 1.46): group means 4.964 and 3.249 Hz give 1.53; pairs 4.741/3.158 = 1.50 and 5.187/3.339 = 1.55. Consistent with the prediction, not confirmation (two bridges per group, spans still being remeasured, bridge03 ground check below 10x).
- Pairs: bridge01 vs bridge02 differ by 9.4 %, bridge03 vs bridge04 by 5.7 %. Each peak is known to about 0.3 %, so the gaps are real differences between structures. For an ideal beam (f proportional to 1/L^2) they equal span differences of about 0.8 m (of 17 m) and 0.7 m (of 25 m). So the spans must be known to better than about 0.3 m before the gaps are interpreted. Rydvan's note: bridge01 carried far more mass (boards, plants) yet has the higher frequency; more mass alone would lower it, so stiffness or support conditions may matter (not tested).
- Ground check so far: bridge01 113x; bridge02 33x; bridge03 below 10x on all full-length controls (1.4-1.6x with steps; 6.6x; 0.7x whole-file / about 8x with the loose-board event removed, post hoc); bridge04 32.0x / 27.3x / 24.6x (all pass). Bridge03's peak is only about 10x the sensor noise floor, bridge04's about 34x.
- Wording agreed for the paper (Claude's advice, Rydvan's to accept): "low-cost sensor" is a design constraint to state with its measured limit (noise floor about 1 mg, frequency precision about 0.02 Hz, timebase agrees with a stopwatch to about 0.5 %), not an excuse for failed checks or unexplained differences; claims worded "consistent with", not "confirms"; amplitude and damping are not validated. JHSS: about 20 % acceptance, 2-5 review rounds, closest accepted paper found is the badminton string vibration study (accelerometer, FFT, mean +/- SD, Kruskal-Wallis); no JHSS bridge or footbridge paper was found (not proof none exists).

## Still open (as of 25 Oct 18:20)

- Detection rule in `find_drops` (miss rate: bridge02 0 of 6 missed; bridge01, bridge03, bridge04 almost all missed). Decision not made.
- Spans: remeasure the 25/24 m bridges (iPhone Measure, slowly, early morning, at least twice); `data/bridges.csv` and `data/sessions.csv` are still only headers.
- From Rydvan: what "one strip, flat under" means exactly; what finally made the bridge04 control hold; what the 7-8 people count at bridge02 covered; where "24 m" comes from; bridge04's span, wind, people; why bridge04 has two ambient files on 24 Oct (`0810`, `0824`, with `0809` tilt_orient: unchecked).
- B2 (six-position gate): no completed B2 decision was found in the log entries checked on 25 Oct.
- bridge03 control: fourth attempt planned (stop rule written 25 Oct 06:55); bridges 05 and 06 not yet recorded.
- Teaching guide for Rydvan (what each document and program is for, which values matter) not yet written; secret scan to repeat before the repo goes public.

## 2026-10-25 18:25 — Rydvan's answers, and a labelling question about "bridge04"

- **Git:** Rydvan ran `git add .` himself at 18:21; the staged list (36 items: 2 modified code files, 28 raw recordings, `build-log.md`, `frequencies.csv`, `damping.csv`, 1 figure) was as expected. The build-log was edited again after that, so it must be staged again before the commit.
- **Rydvan's answers (25 Oct):**
  - Bridge04 control: he "started to add another strip of tape to hold the wires"; **why it finally held: because it was early morning and no heat** (his view).
  - The 7-8 people at bridge02 "were probably the ambient" (not confirmed).
  - 24 m "is likely the length of the bridges" (the 6-lane single-span ones). After the measurements he will do one final check of the lengths with the iPhone Measure app, twice, walking carefully.
  - Bridge04 (25 Oct) is "the same as the other Charoen Nakhon bridges, 25 m", as approximated from earlier measurements (not measured separately yet). Conditions on 25 Oct: low wind, barely any people (early morning).
- **Claude's check of all bridge04 ambient files (25 Oct 18:30; files not changed)**, refined peaks by the program's own method (`--axis x`):

  | File | Started | Length | Peak | Board |
  |---|---|---|---|---|
  | `20261021_0644_bridge03_ambient` | 21 Oct 06:44 | 899.4 s | 3.339 Hz | steady |
  | `20261024_0810_bridge04_ambient` | 24 Oct 08:10 | 787.6 s of 900 requested | **3.281 Hz** | quiet for about 600 s, then moved (x noise up to 171 counts, y +754 at about 660-720 s); z mean 1,035 |
  | `20261024_0824_bridge04_ambient` | 24 Oct 08:24 | 899.4 s | **3.277 Hz** | noisy first minute (x SD 48), then steady (x noise 17-19), y creeps -65 to +225 |
  | `20261025_0625_bridge04_ambient` | 25 Oct 06:25 | 899.4 s | **3.158 Hz** | steady |

  All files: 200.000 Hz, 0 dropped samples. The two 24 Oct files agree with each other (3.281 and 3.277 Hz), so they look like one structure. **They are not bridge03's recording**: the 24 Oct files start at 08:10 and 08:24 on a different day, and their peak (about 3.28 Hz) is about 1.8 % below bridge03's 3.339 Hz, much more than the roughly 0.3 % uncertainty of a peak (a temperature or traffic shift of this size on one bridge is possible but not shown). They also do not match the 25 Oct file labelled bridge04 (3.158 Hz, 3.8 % lower). So the 24 Oct and 25 Oct files labelled "bridge04" do not look like the same bridge.
- **Open question for Rydvan (not decided):** which physical bridge was recorded in each of (a) bridge03 (21-24 Oct), (b) the 24 Oct files labelled `bridge04`, (c) the 25 Oct files labelled `bridge04`? One possibility, not tested: the 25 Oct set was recorded at another bridge using the `bridge04` commands, so there may be three different 25 m bridges (3.339, about 3.28 and 3.158 Hz) under only two labels. Raw files are **not renamed** (rule). The mapping goes into `data/bridges.csv` / `data/sessions.csv` and this log. Until it is settled the analysis program must not combine the 24 Oct ambient files with the 25 Oct decay and control: it takes the newest file of each type by label. The 25 Oct control (`0725`, 32.0x) was recorded together with the 25 Oct ambient; its ground check does not apply to the 24 Oct ambient files unless they are the same bridge.
- **24 Oct timeline, rebuilt from the files (Claude, 25 Oct 18:45; there are no other 24 Oct logs, notes or files in the project folder):**
  - 07:38:30 `bridge03_control` (stopped at 201 s: board came off), 07:44:52 `bridge03_control` (full 300 s, event at 237-249 s). These are the bridge03 controls Rydvan reported at 07:50.
  - 08:09:37 `bridge04_tilt_orient`, 08:10:02 `bridge04_ambient` (stopped at 787.6 s), 08:24:26 `bridge04_ambient` (899.4 s, ended about 08:39). About 19 minutes after the last bridge03 file ended, with a label typed as `bridge04`. No decay and no control were recorded for this bridge. At 08:25-08:27 he sent a photo of the edge-taped board and said he had used that taping only "for this bridge so far".
  - Rydvan's recollection (25 Oct 18:42, uncertain, "or wait... no I don't recall"): the 24 Oct recording may have been **bridge05**; he first thought he had been doing the bridge03 control that day (he did, in the morning: `0738` and `0744`), then stopped the ambient "because it wasn't holding right"/too hot. Not confirmed.
  - Not settled by the data: the 24 Oct ambient peak (about 3.28 Hz) matches neither bridge03 (3.339) nor the 25 Oct `bridge04` (3.158). The photo sent on 24 Oct has no time or GPS in it (stripped on upload); the two scouting photos in the folder are undersides only. Next step: Rydvan checks his iPhone Photos (time and map location of the 24 Oct 08:25 photo, and any other photos from 08:00-08:40) to name the bridge. Until then the 24 Oct files keep their label and are not combined with the 25 Oct decay or control.
- **Rydvan's explanation (25 Oct 18:47):** on 24 Oct he tried recording at a bridge (label `bridge04`) but the board "wasn't holding right as it was too hot" and "wasn't held onto the wall right", so he quit it. He considers the 24 Oct `bridge04` files **failed attempts**. On 25 Oct he redid "bridge04" but **actually used a different bridge**. So the files labelled `bridge04` on 24 Oct (`0809` tilt_orient, `0810` ambient, `0824` ambient) and on 25 Oct (`0624`, `0625`, `0641`, `0703`, `0713`, `0725`) are two different physical bridges. Which bridge number the 24 Oct site really is (earlier recollection: possibly bridge05) is still to be named from his phone photos.
- **Claude's note on "failed":** the files are kept as recorded and not renamed or deleted. Data check: `0810` is usable for about the first 600 s only (board moved later); `0824` is steady after its first minute (peak about 3.277 Hz, 26x the noise floor, 899.4 s), so it may be a usable ambient recording of that other bridge. Without a decay, a control and a measured span at that bridge it is not used for any result yet. Whether to revisit that bridge (decay, control, span) is Rydvan's decision. Frequencies by site so far: bridge03 3.339 Hz, 25 Oct `bridge04` 3.158 Hz, 24 Oct (other bridge) about 3.28 Hz.
