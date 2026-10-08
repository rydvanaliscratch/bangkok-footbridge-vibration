"""
span_fit.py - the physics test: how does frequency change with span?

    python3 analysis/span_fit.py

Reads the span of every bridge from data/bridges.csv and its measured
frequency (newest ambient result) from results/frequencies.csv, then
fits a straight line to log10(f) against log10(L).

Ideal simply-supported beams follow f proportional to 1/L^2, a slope of
-2. The fit reports the slope with its 95% range (t-distribution on the
standard error), draws the points, the fitted line and a -2 reference
line, and adds the result to results/span_fit.csv.
"""

import csv
from pathlib import Path

import numpy as np
from scipy import stats

import common


def main():
    spans = {}
    with open("data/bridges.csv") as f:
        for row in csv.DictReader(r for r in f if not r.startswith("#")):
            if row.get("bridge_id") and row.get("span_m"):
                spans[row["bridge_id"]] = float(row["span_m"])
    freqs = {}
    with open("results/frequencies.csv") as f:
        for row in csv.DictReader(f):
            if row["run"] == "ambient" and row["site"] in spans:
                freqs[row["site"]] = float(row["f_peak_hz"])   # later rows overwrite: newest wins
    ids = sorted(set(spans) & set(freqs))
    if len(ids) < 3:
        raise SystemExit(f"Need at least 3 bridges with both a span and a frequency; have {len(ids)}.")
    L = np.array([spans[i] for i in ids])
    fr = np.array([freqs[i] for i in ids])
    x, y = np.log10(L), np.log10(fr)
    fit = stats.linregress(x, y)
    tcrit = stats.t.ppf(0.975, len(ids) - 2)
    lo, hi = fit.slope - tcrit * fit.stderr, fit.slope + tcrit * fit.stderr
    print(f"Bridges used: {len(ids)}  ({', '.join(ids)})")
    for i in ids:
        print(f"  {i}: span {spans[i]:.1f} m   f {freqs[i]:.3f} Hz")
    print(f"\nSlope {fit.slope:.2f}   95% range {lo:.2f} to {hi:.2f}   R2 {fit.rvalue ** 2:.3f}")
    if hi < -2:
        verdict = "steeper than -2"
    elif lo > -2:
        verdict = "shallower than -2 (H3 as currently worded would be supported)"
    else:
        verdict = "cannot be told apart from -2 (ideal beams) with these bridges"
    print(f"  -> {verdict}")
    common.append_result("results/span_fit.csv", {"n_bridges": len(ids), "bridges": " ".join(ids),
                         "slope": round(fit.slope, 3), "ci95_low": round(lo, 3), "ci95_high": round(hi, 3),
                         "r2": round(fit.rvalue ** 2, 4)})
    plt = common.plt_or_none()
    if plt:
        fig, a = plt.subplots(figsize=(6, 4.5))
        a.loglog(L, fr, "o")
        for i, l, f_ in zip(ids, L, fr):
            a.annotate(i, (l, f_), textcoords="offset points", xytext=(4, 4), fontsize=7)
        xx = np.linspace(x.min() - 0.05, x.max() + 0.05, 50)
        a.loglog(10 ** xx, 10 ** (fit.intercept + fit.slope * xx), "-", label=f"fit: slope {fit.slope:.2f}")
        a.loglog(10 ** xx, 10 ** (y.mean() - 2 * (xx - x.mean())), ":", label="ideal beam: slope -2")
        a.set_xlabel("span L (m)")
        a.set_ylabel("natural frequency f (Hz)")
        a.legend(fontsize=8)
        fig.tight_layout()
        Path("figures").mkdir(exist_ok=True)
        fig.savefig("figures/span_fit.png", dpi=150)
        print("  figure: figures/span_fit.png")


if __name__ == "__main__":
    main()
