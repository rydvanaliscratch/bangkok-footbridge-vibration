"""
damping.py - measure damping from a heel-drop ("decay") recording.

    python3 analysis/damping.py DECAY.csv --f 3.2 [--axis z]

--f is the bridge's natural frequency, taken from spectrum.py.

What it does, in order:
 1. Loads the vertical axis in g, mean removed, true sample rate.
 2. Band-pass filter from 0.7f to 1.3f (4th-order Butterworth, run
    forwards and backwards so it adds no delay). This keeps the bridge's
    own bounce and removes footsteps, traffic rumble and sensor hiss.
 3. Finds each heel-drop: a burst in the BAND-PASSED signal more than 8x
    its typical level, at least 10 s after the previous one.
    (Changed 26 Oct 2026, after seeing the data: the first version looked
    for the burst in the raw signal, where walking, traffic and board
    drift hid most drops. The factor 8 and all other constants are
    unchanged. The old rule's drop count is still printed for comparison.
    See docs/build-log.md.)
 4. For each drop, starts 0.5 s after the burst (the drop itself is
    over by then) and collects the successive positive peaks of the
    ringing, stopping when they sink into the background (3x its level)
    or the next drop begins.
 5. Logarithmic decrement: fits a straight line to ln(peak height)
    against peak number. The slope is -delta; damping ratio
    zeta = delta / sqrt(4 pi^2 + delta^2)  (about delta / 2 pi).
 6. Reports each drop and the mean and spread, saves a figure of one
    decay with its fitted envelope, and adds a row per drop to
    results/damping.csv.
"""

import argparse
from pathlib import Path

import numpy as np
from scipy import signal

import common

EVENT_FACTOR = 8        # a heel-drop is a burst this many times the typical level
MIN_GAP_S = 10          # heel-drops at least this far apart
SKIP_S = 0.5            # ignore this long after the burst (the forced part)
FLOOR_FACTOR = 3        # stop when peaks fall below this many times the background
MIN_PEAKS = 5           # fewer usable peaks than this -> drop is not analysed


def bandpass(sig, rate, f):
    sos = signal.butter(4, [0.7 * f, 1.3 * f], btype="bandpass", fs=rate, output="sos")
    return signal.sosfiltfilt(sos, sig)


def find_drops(sig, rate):
    """Sample indices of heel-drop bursts in the given signal.

    Current rule: pass the band-passed signal. The original (raw-signal)
    rule is the same function called with the raw signal.
    """
    level = np.median(np.abs(sig)) / 0.6745          # robust typical level
    loud = np.where(np.abs(sig) > EVENT_FACTOR * level)[0]
    drops, last = [], -np.inf
    for i in loud:
        if i - last > MIN_GAP_S * rate:
            drops.append(int(i))
            last = i
    return drops


def one_decay(bp, rate, f, start, stop, background):
    seg = bp[start:stop]
    pk, _ = signal.find_peaks(seg, distance=max(1, int(0.7 * rate / f)))
    heights = seg[pk]
    keep = []
    for k, h in zip(pk, heights):
        if h < FLOOR_FACTOR * background:
            break
        keep.append((k, h))
    if len(keep) < MIN_PEAKS:
        return None
    idx = np.array([k for k, _ in keep])
    amp = np.array([h for _, h in keep])
    n = np.arange(len(amp))
    slope, intercept = np.polyfit(n, np.log(amp), 1)
    fit = intercept + slope * n
    ss_res = float(((np.log(amp) - fit) ** 2).sum())
    ss_tot = float(((np.log(amp) - np.log(amp).mean()) ** 2).sum())
    delta = -slope
    zeta = delta / np.sqrt(4 * np.pi ** 2 + delta ** 2)
    f_ring = rate / float(np.median(np.diff(idx)))
    return {"start": start, "peak_idx": idx + start, "amp": amp, "intercept": intercept,
            "slope": slope, "delta": delta, "zeta": zeta, "r2": 1 - ss_res / ss_tot if ss_tot else 1.0,
            "n_peaks": len(amp), "f_ring": f_ring}


def analyse(path, f, axis="z", save=True, quiet=False):
    raw, rate, info = common.axis_in_g(path, axis)
    bp = bandpass(raw, rate, f)
    drops = find_drops(bp, rate)            # current rule (band-passed)
    old_drops = find_drops(raw, rate)       # original rule, for comparison only
    results = []
    for j, d in enumerate(drops):
        start = d + int(SKIP_S * rate)
        stop = drops[j + 1] - int(0.5 * rate) if j + 1 < len(drops) else len(bp)
        pre = bp[max(0, d - int(3 * rate)):max(1, d - int(0.2 * rate))]
        background = float(np.sqrt(np.mean(pre ** 2))) if len(pre) > 10 else float(np.std(bp))
        r = one_decay(bp, rate, f, start, stop, background)
        results.append((d, r))

    good = [r for _, r in results if r is not None]
    if not quiet:
        print(f"File: {info['file']}   axis {axis}   measured rate {rate:.3f} Hz   "
              f"band-pass {0.7 * f:.2f}-{1.3 * f:.2f} Hz")
        print(f"Heel-drops found: {len(drops)}   usable: {len(good)}   "
              f"(original raw-signal rule would find {len(old_drops)})")
        for k, (d, r) in enumerate(results, 1):
            t = d / rate
            if r is None:
                print(f"  drop {k:2d} at {t:6.1f} s   not usable (fewer than {MIN_PEAKS} clear peaks)")
            else:
                print(f"  drop {k:2d} at {t:6.1f} s   {r['n_peaks']:3d} peaks   ring {r['f_ring']:.2f} Hz   "
                      f"delta {r['delta']:.4f}   zeta {100 * r['zeta']:.2f} %   fit R2 {r['r2']:.3f}")
    summary = None
    if good:
        z = np.array([r["zeta"] for r in good])
        summary = {"n": len(good), "zeta_mean": float(z.mean()),
                   "zeta_sd": float(z.std(ddof=1)) if len(z) > 1 else float("nan")}
        if not quiet:
            print(f"  DAMPING  zeta = {100 * summary['zeta_mean']:.2f} % (mean of {len(good)} drops), "
                  f"spread (SD) {100 * summary['zeta_sd']:.2f} %")

    if save:
        for k, (d, r) in enumerate(results, 1):
            common.append_result("results/damping.csv", {
                "file": info["file"], **common.parse_name(path), "axis": axis,
                "f_used_hz": f, "drop": k, "time_s": round(d / rate, 1),
                "usable": r is not None,
                "n_peaks": r["n_peaks"] if r else "", "f_ring_hz": round(r["f_ring"], 3) if r else "",
                "log_decrement": round(r["delta"], 5) if r else "",
                "zeta_percent": round(100 * r["zeta"], 3) if r else "",
                "fit_r2": round(r["r2"], 4) if r else ""})
        plt = common.plt_or_none()
        if plt and good:
            r = max(good, key=lambda x: x["n_peaks"])
            t0 = r["start"] / rate
            span = slice(r["start"], int(r["peak_idx"][-1] + rate))
            tt = np.arange(span.start, span.stop) / rate - t0
            fig, a = plt.subplots(figsize=(8, 4.5))
            a.plot(tt, 1000 * bp[span], linewidth=0.8, label="band-passed signal")
            a.plot(r["peak_idx"] / rate - t0, 1000 * r["amp"], "o", markersize=3, label="peaks used")
            n = np.arange(r["n_peaks"])
            env = np.exp(r["intercept"] + r["slope"] * n)
            a.plot(r["peak_idx"] / rate - t0, 1000 * env, "--",
                   label=f"fitted decay, zeta = {100 * r['zeta']:.2f} %")
            a.set_xlabel("time after heel-drop (s)")
            a.set_ylabel("acceleration (mg)")
            a.set_title(f"Free decay - {info['file']}")
            a.legend(fontsize=8)
            fig.tight_layout()
            figpath = Path("figures") / f"decay_{Path(path).stem}.png"
            figpath.parent.mkdir(exist_ok=True)
            fig.savefig(figpath, dpi=150)
            plt.close(fig)
            if not quiet:
                print(f"  figure: {figpath}")
    return summary, results


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("recording")
    p.add_argument("--f", type=float, required=True, help="natural frequency from spectrum.py, Hz")
    p.add_argument("--axis", default="z", choices=["x", "y", "z"])
    a = p.parse_args()
    analyse(a.recording, a.f, a.axis)


if __name__ == "__main__":
    main()
