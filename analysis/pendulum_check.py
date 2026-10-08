"""
pendulum_check.py - gate B5: does the whole chain find a frequency you
can work out by hand?

    python3 analysis/pendulum_check.py PENDULUM.csv [--length 0.25]

Theory (small swings): T = 2 pi sqrt(L / g), so f = 1 / T.
For L = 0.25 m: T = 1.003 s, f = 0.997 Hz.

It runs the same spectrum as the bridges (spectrum.py) on all three
axes between 0.3 and 5 Hz. The axis across the swing sees the swing
itself at f; the axis along the string sees the string's pull, which
peaks twice per swing, at 2f.

PASS: some axis peaks within +/-0.05 Hz of f, and some axis peaks
within +/-0.10 Hz of 2f.
"""

import argparse
import math

import common
import spectrum

TOL_F = 0.05
TOL_2F = 0.10


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("recording")
    p.add_argument("--length", type=float, default=0.25, help="pivot to sensor centre, metres")
    a = p.parse_args()

    f_theory = 1 / (2 * math.pi * math.sqrt(a.length / 9.81))
    print(f"Theory: L = {a.length} m -> T = {1 / f_theory:.3f} s, f = {f_theory:.3f} Hz, 2f = {2 * f_theory:.3f} Hz\n")
    found = {}
    for axis in ("x", "y", "z"):
        r = spectrum.analyse(a.recording, axis=axis, fmin=0.3, fmax=5.0, quiet=True)
        found[axis] = r
        print(f"  axis {axis}: peak {r['f_peak_hz']:.3f} Hz   95% range "
              f"{r['ci95_low_hz']:.3f}-{r['ci95_high_hz']:.3f} Hz   figure {r['figure']}")
    hit_f = [k for k, r in found.items() if abs(r["f_peak_hz"] - f_theory) <= TOL_F]
    hit_2f = [k for k, r in found.items() if abs(r["f_peak_hz"] - 2 * f_theory) <= TOL_2F]
    ok = bool(hit_f) and bool(hit_2f)
    print(f"\n  swing peak at f within +/-{TOL_F} Hz on axis: {', '.join(hit_f) or 'none'}")
    print(f"  string-pull peak at 2f within +/-{TOL_2F} Hz on axis: {', '.join(hit_2f) or 'none'}")
    print(f"  RESULT: {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  If no axis is near f: was the swing small and steady, and the rate taken from the file?")


if __name__ == "__main__":
    main()
