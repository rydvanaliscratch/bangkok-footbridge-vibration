"""Figures 1 and 2 of the paper (no titles; axes in title case with units).
Run from the repo root:  python3 analysis/paper_figures.py OUTDIR
Uses the repo's own analysis functions (common.py, spectrum.py) and results/frequencies.csv,
so the plotted numbers match the official results. Written by Claude (AI assistant), 25 Nov 2026."""
import sys, csv
from pathlib import Path
import numpy as np
from scipy import stats
sys.path.insert(0, "analysis")
import common, spectrum
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "serif", "font.size": 11})
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)   # create the output folder if it does not exist

# Figure 1: bridge05 ambient vs ground control
amb = "data/raw/20261026_0644_bridge05_ambient.csv"
ctl = "data/raw/20261026_0718_bridge05_control.csv"
sig, rate, _ = common.axis_in_g(amb, "x")
f, P = spectrum.pieces(sig, rate); psd = P.mean(axis=0)
csig, crate, _ = common.axis_in_g(ctl, "x")
cf, CP = spectrum.pieces(csig, crate); cpsd = np.interp(f, cf, CP.mean(axis=0))
fp, _ = spectrum.peak(f, psd, 1, 20)
near = np.abs(f - fp) <= (f[1] - f[0])
ratio = psd[near].max() / cpsd[near].max()
print(f"Fig1 check: peak {fp:.3f} Hz (results/ 3.315), ratio {ratio:.1f} (results/ 46.3)")
fig, a = plt.subplots(figsize=(7, 4.2))
a.semilogy(f, psd, color="#1f4e79", lw=1.2, label="Bridge Deck (Midspan)")
a.semilogy(f, cpsd, color="#c55a11", lw=1.2, label="Ground Control (Stair Base)")
a.axvline(fp, color="gray", ls="--", lw=0.9)
a.annotate(f"{fp:.3f} Hz", (fp, psd[near].max()), xytext=(8, 0), textcoords="offset points", fontsize=10)
a.set_xlim(0, 20); a.set_xlabel("Frequency (Hz)"); a.set_ylabel("Power Spectral Density (g$^2$/Hz)")
a.legend(frameon=False); fig.tight_layout()
fig.savefig(out / "Figure1_bridge05_spectrum.jpg", dpi=300, pil_kwargs={"quality": 95}); plt.close(fig)

# Figure 2: span fit with the sealed prediction
spans = {}
with open("data/bridges.csv") as fh:
    for r in csv.DictReader(l for l in fh if not l.startswith("#")):
        if r.get("bridge_id") and r.get("span_m"): spans[r["bridge_id"]] = float(r["span_m"])
freqs = {}
with open("results/frequencies.csv") as fh:
    for r in csv.DictReader(fh):
        if r["run"] == "ambient" and r["site"] in spans: freqs[r["site"]] = float(r["f_peak_hz"])
ids = sorted(set(spans) & set(freqs))
L = np.array([spans[i] for i in ids]); fr = np.array([freqs[i] for i in ids])
x, y = np.log10(L), np.log10(fr); fit = stats.linregress(x, y)
print(f"Fig2 check: slope {fit.slope:.2f}, R2 {fit.rvalue**2:.2f} (results/ -1.19, 0.93); spans {dict(zip(ids, L))}")
fig, a = plt.subplots(figsize=(6.2, 4.6))
Lx = np.linspace(15.5, 28.5, 100)
a.fill_between(Lx, 0.8 * 80 / Lx, 1.25 * 80 / Lx, color="0.88", label="Prediction Range (0.8–1.25 × 80/L)")
a.plot(Lx, 80 / Lx, color="0.4", ls=":", lw=1.3, label="Prediction f = 80/L")
a.plot(Lx, 10 ** (fit.intercept + fit.slope * np.log10(Lx)), color="#1f4e79", lw=1.3,
       label="Least-Squares Fit (Slope " + f"{fit.slope:.2f}".replace("-", "\u2212") + ")")
for i, l, f_ in zip(ids, L, fr):
    unconf = i == "bridge03"
    a.errorbar(l, f_, xerr=0.3, fmt="o", ms=6, color="#c55a11", mfc="white" if unconf else "#c55a11", capsize=2, lw=0.8)
    off = {"bridge06": (6, -14), "bridge03": (-20, 9), "bridge04": (6, 4), "bridge05": (-30, -17), "bridge02": (6, -15)}.get(i, (6, 4))
    a.annotate(i + (" (unconfirmed)" if unconf else ""), (l, f_),
               xytext=off, textcoords="offset points", fontsize=9)
a.set_xscale("log"); a.set_yscale("log")
a.set_xticks([16, 18, 20, 22, 24, 26]); a.set_xticklabels(["16", "18", "20", "22", "24", "26"])
a.set_yticks([2.5, 3, 4, 5, 6]); a.set_yticklabels(["2.5", "3", "4", "5", "6"])
a.minorticks_off()
a.set_xlabel("Clear Span L (m)"); a.set_ylabel("Natural Frequency f (Hz)")
a.legend(frameon=False, fontsize=8.5, loc="upper right"); fig.tight_layout()
fig.savefig(out / "Figure2_span_fit.jpg", dpi=300, pil_kwargs={"quality": 95}); plt.close(fig)
print("saved")
