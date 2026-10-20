"""
pendulum_ringdown.py - gate B5, pass B: time the swings one by one.

    python3 analysis/pendulum_ringdown.py PENDULUM.csv --length 0.25

Used when the strict spectrum check (pass A in pendulum_check.py) is not
met because the swing was short. Rule, fixed before run 2 was looked at
(docs/build-log.md, 20 Oct 2026):

  PASS-B if some axis has at least 5 consecutive clean swings
  (each at least 4x the sensor noise, each period within 10 % of the
  run's median period) AND their timed frequency is within +/-0.05 Hz
  of theory, f = 1 / (2 pi sqrt(L / g)).

How it works, in plain words:
  1. Remove everything slower than 0.4 Hz and faster than 3 Hz.
  2. Find the moments the signal crosses zero going up. The time between
     two such moments is one swing (one period).
  3. Find the longest stretch of swings that are big enough and all about
     the same length.
  4. Frequency = number of swings / time they took.
A spectrum over 5 s cannot tell 0.95 Hz from 1.05 Hz; counting swings can.
"""

import argparse
import math

import numpy as np

import common

TOL_F = 0.05          # Hz, allowed distance from theory
MIN_CYCLES = 5        # swings in a row
AMP_FACTOR = 4.0      # each swing must reach this many times the noise
PERIOD_TOL = 0.10     # each period within 10 % of the run's median
BAND = (0.4, 3.0)     # Hz


def bandpass(x, rate, lo, hi):
    """Zero-phase band-pass with the FFT (no phase shift, so crossing times are true)."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / rate)
    spec[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(spec, len(x))


def noise_level(sig, rate):
    """Typical quiet level: the 25th percentile of one-second standard deviations."""
    w = int(rate)
    sds = [sig[k:k + w].std() for k in range(0, len(sig) - w + 1, w)]
    return float(np.percentile(sds, 25)) if sds else float(sig.std())


def best_run(sig, rate, noise_sd):
    """Longest run of clean, steady swings. Returns a dict or None."""
    idx = np.where((sig[:-1] < 0) & (sig[1:] >= 0))[0]
    if len(idx) < 2:
        return None
    t = (idx + (-sig[idx]) / (sig[idx + 1] - sig[idx])) / rate   # interpolated crossing times, s
    per = np.diff(t)
    amp = np.array([np.abs(sig[idx[i]:idx[i + 1] + 1]).max() for i in range(len(per))])
    big = amp >= AMP_FACTOR * noise_sd
    best = (0, 0)                                               # (start, count)
    n = len(per)
    for i in range(n):
        if not big[i]:
            continue
        j = i
        while j < n and big[j]:
            seg = per[i:j + 1]
            med = np.median(seg)
            if np.any(np.abs(seg / med - 1) > PERIOD_TOL):
                break
            j += 1
        if j - i > best[1]:
            best = (i, j - i)
    s, c = best
    if c == 0:
        return None
    seg = per[s:s + c]
    secs = t[s + c] - t[s]
    return {"cycles": c, "f_hz": c / secs, "seconds": secs, "start_s": float(t[s]),
            "spread": float(seg.std() / seg.mean()), "amp_g": float(amp[s:s + c].min())}


def analyse(path, length, quiet=False):
    f_theory = 1 / (2 * math.pi * math.sqrt(length / common.G))
    out = {"f_theory": f_theory, "axes": {}, "passed": False, "best_axis": None}
    for axis in ("x", "y", "z"):
        sig, rate, _ = common.axis_in_g(path, axis)
        sig = bandpass(sig, rate, *BAND)
        noise = noise_level(sig, rate)
        out["axes"][axis] = dict(best_run(sig, rate, noise) or {"cycles": 0}, noise_g=noise)
    cands = [k for k, r in out["axes"].items()
             if r["cycles"] >= MIN_CYCLES and abs(r["f_hz"] - f_theory) <= TOL_F]
    if cands:
        out["best_axis"] = max(cands, key=lambda k: out["axes"][k]["cycles"])
        out["passed"] = True
    if not quiet:
        print(f"  Pass B (timing each swing): theory f = {f_theory:.3f} Hz, "
              f"need >= {MIN_CYCLES} clean swings within +/-{TOL_F} Hz")
        for axis, r in out["axes"].items():
            if r["cycles"] == 0:
                print(f"    axis {axis}: no clean run (noise {r['noise_g'] * 1000:.2f} mg in band)")
            else:
                near = abs(r["f_hz"] - f_theory) <= TOL_F
                print(f"    axis {axis}: {r['cycles']} swings in {r['seconds']:.1f} s from "
                      f"t = {r['start_s']:.1f} s, f = {r['f_hz']:.3f} Hz "
                      f"(period spread {100 * r['spread']:.1f} %), "
                      f"{'near theory' if near else 'NOT at theory frequency'}")
        if out["passed"]:
            a = out["axes"][out["best_axis"]]
            print(f"    -> {a['cycles']} swings on axis {out['best_axis']}, {a['f_hz']:.3f} Hz "
                  f"vs {f_theory:.3f} Hz. The swing lasted {a['seconds']:.1f} s: state this limitation.")
        else:
            print("    -> pass B not met.")
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("recording")
    p.add_argument("--length", type=float, required=True,
                   help="pivot to sensor centre in metres, measured with a ruler")
    a = p.parse_args()
    r = analyse(a.recording, a.length)
    print(f"  RESULT: {'PASS (B, short ringdown)' if r['passed'] else 'FAIL'}")


if __name__ == "__main__":
    main()
