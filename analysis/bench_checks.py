"""
bench_checks.py - gates B3 (noise) and B4 (timing) from one resting recording.

    python3 analysis/bench_checks.py data/calibration/<file>_bench_rest.csv

The board must have been still on a solid surface for the whole recording.
Pass marks come from the study dossier (Bench qualification table).
"""

import sys
from pathlib import Path

import numpy as np

COUNTS_PER_G = 16384        # +/-2 g full scale (AFS_SEL = 0)
TARGET_GAP_US = 5000        # 200 Hz -> one sample every 5000 microseconds

B3_MAX_SD_COUNTS = 60       # B3: standard deviation of Z below 60 counts
B4_WINDOW_US = 500          # B4: 99% of gaps within +/-500 us of 5000
B4_MIN_FRACTION = 0.99
B4_MEDIAN_TOL_US = 50       # B4 says "median gap 5000 us"; +/-50 us (1%) is our reading of that


def load(path):
    """Return t_us, ax, ay, az as numpy arrays, plus how many lines were not data."""
    rows = []
    not_data = 0
    with open(path, encoding="ascii", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#") or line.startswith("t_us"):
                continue                        # comments and the column-name line
            parts = line.split(",")
            try:
                if len(parts) != 4:
                    raise ValueError
                rows.append([int(p) for p in parts])
            except ValueError:
                not_data += 1                   # e.g. garbage bytes while the Uno reset
    data = np.array(rows, dtype=np.int64)
    return data[:, 0], data[:, 1], data[:, 2], data[:, 3], not_data


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    path = Path(sys.argv[1])
    t, ax, ay, az, not_data = load(path)

    print(f"File: {path}")
    print(f"Samples: {len(t)}   non-data lines skipped: {not_data}")

    # ---------- B4: timing ----------
    gaps = np.diff(t)
    gaps[gaps < 0] += 2**32                     # micros() wraps around every ~71.6 min
    duration_s = gaps.sum() / 1e6               # sum of gaps survives the wraparound
    print(f"Duration covered by timestamps: {duration_s:.2f} s")
    median_gap = float(np.median(gaps))
    within = np.abs(gaps - TARGET_GAP_US) <= B4_WINDOW_US
    fraction_within = within.mean()
    # a gap of about 2x the median means one line went missing, 3x means two, ...
    missing = np.round(gaps / median_gap).astype(int) - 1
    dropped = int(missing[missing > 0].sum())
    rate_hz = 1e6 / median_gap

    b4_pass = (abs(median_gap - TARGET_GAP_US) <= B4_MEDIAN_TOL_US
               and fraction_within >= B4_MIN_FRACTION
               and dropped == 0)

    print("\nB4 - timing")
    print(f"  median gap        {median_gap:.1f} us   (target {TARGET_GAP_US})")
    print(f"  measured rate     {rate_hz:.3f} Hz")
    print(f"  gaps within +/-{B4_WINDOW_US} us  {100*fraction_within:.2f} %   (need >= {100*B4_MIN_FRACTION:.0f} %)")
    print(f"  smallest / largest gap  {gaps.min()} / {gaps.max()} us")
    print(f"  dropped lines     {dropped}")
    print(f"  RESULT: {'PASS' if b4_pass else 'FAIL'}")

    # ---------- B3: noise ----------
    sd = {name: float(np.std(v, ddof=1)) for name, v in (("x", ax), ("y", ay), ("z", az))}
    mean = {name: float(np.mean(v)) for name, v in (("x", ax), ("y", ay), ("z", az))}
    b3_pass = sd["z"] < B3_MAX_SD_COUNTS

    print("\nB3 - noise at rest")
    for name in ("x", "y", "z"):
        mg = 1000 * sd[name] / COUNTS_PER_G
        print(f"  {name}: mean {mean[name]:9.1f} counts   SD {sd[name]:6.1f} counts ({mg:.2f} mg)")
    print(f"  RESULT: {'PASS' if b3_pass else 'FAIL'}   (Z SD must be < {B3_MAX_SD_COUNTS} counts)")

    # ---------- histogram of the gaps (B4 picture) ----------
    try:
        import matplotlib
        matplotlib.use("Agg")                   # draw to a file, no window needed
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib not installed - skipping the histogram)")
        return
    out = Path("figures") / f"B4_gaps_{path.stem}.png"
    out.parent.mkdir(exist_ok=True)
    fig, axis = plt.subplots(figsize=(7, 4))
    axis.hist(gaps, bins=100)
    axis.axvline(TARGET_GAP_US, linestyle="--")
    axis.set_yscale("log")
    axis.set_xlabel("gap between consecutive samples (us)")
    axis.set_ylabel("number of gaps (log scale)")
    axis.set_title(f"B4 timing - {path.name}")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"\nHistogram saved to {out}")


if __name__ == "__main__":
    main()
