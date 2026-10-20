# Limitations (kept up to date as they arise)

Each entry: what, why it matters, and what the paper must say. Entries are
added when they are found, not removed when they become inconvenient.

## B5 pendulum check: not passed  (opened 20 Oct 2026)

- **What happened:** five runs (`data/calibration/20261020_0857`, `_0923`, `_0943`,
  `_0957`, `_0958` `_bench_pendulum.csv`). Run 1 was a rough swing and failed.
  Runs 2-5 were clean swings, repeatable to about 0.4 % (z peaks 1.170, 1.167,
  1.163, 1.164 Hz), but 14-15 % above the theory value 1.018 Hz for
  L = 0.24 m (f = 1 / (2 pi sqrt(L / g))). Pass A (spectrum) and pass B (timing
  each swing) both failed on every run. The rule was written before run 2 was
  looked at (`docs/build-log.md`, 20 Oct 2026).
- **Suspected cause (untested):** the sensor with headers, floss and tape
  weighs only a few grams, and the four jumper wires act as weak springs, which
  raises the frequency and damps the swing. The planned test (a heavier bob)
  was not done because the weight would not stay attached.
- **Independent stopwatch check (20 Oct):** 10 swings timed by eye, six times:
  7.99, 8.31, 8.55, 8.69, 8.62, 8.92 s (mean 8.51 s, about 1.175 Hz, +/-0.02 Hz
  from the scatter), against the sensor's 1.17 Hz and theory's 1.018 Hz (which
  would take 9.8 s). The prediction was logged before the timing; all six
  timings are used. So the readout agrees with an independent measurement of
  the same swing; what disagrees is the single-point-mass theory for this
  apparatus. Rough setup: L measured only to about +/-2 cm with a 10 cm ruler,
  the floss was not knotted, the wires hang with weight and tension on the
  board, and loose floss ends hung near objects below.
- **Why it matters:** B5 is the one check where the right frequency is known in
  advance. Not passing it means the frequency readout has not been confirmed
  by an independent known frequency. What does support the readout: the
  sampling rate was measured as 200.000 Hz with no dropped samples (B4); the
  analysis code recovers known frequencies on made-up data (self-test); the
  pendulum frequency is steady and repeatable, with its double appearing on
  another axis, as expected.
- **What the paper must say:** that B5 was run five times and not passed, with
  the numbers above; that the suspected cause was not tested; and that the
  bridge frequencies are therefore reported without a successful pendulum
  validation. Do not write "validated" or "calibrated" for the frequency
  readout.
- **Status:** B5 by its rule is NOT PASSED. The stopwatch check supports the readout
  but is not the pre-agreed gate, so the paper reports both and does not call
  the readout "validated by B5". A repeat with a tidier rig would close it.
