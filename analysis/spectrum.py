"""
spectrum.py - find the natural frequency in a recording.

    python3 analysis/spectrum.py RECORDING.csv [--control CONTROL.csv]
                                 [--axis z] [--fmin 1] [--fmax 20]

What it does, in order:
 1. Loads one axis (default z, vertical when the sensor lies flat),
    converts counts to g and removes the mean.
 2. Measures the true sample rate from the timestamps.
 3. Welch spectrum: cuts the recording into overlapping 4096-sample
    pieces (about 20 s each), Hann-windows each, and averages their power
    spectra. Averaging makes random noise smooth while a steady rhythm
    stays as a peak.
 4. Picks the tallest peak between fmin and fmax, refined between
    frequency bins by fitting a parabola through the top three points.
 5. Bootstrap: resamples the pieces 1000 times with replacement and
    re-finds the peak each time. The 2.5th-97.5th percentile of those
    peaks is the reported 95% range.
 6. With --control: computes the ground recording's spectrum the same
    way and reports how many times stronger the peak is on the bridge.
 7. Saves a figure and adds a row to results/frequencies.csv.
"""

import argparse
from pathlib import Path

import numpy as np
from scipy import signal

import common

NPERSEG = 4096          # samples per piece: ~20.5 s at 200 Hz -> ~0.049 Hz bins
N_BOOT = 1000
RNG_SEED = 1            # fixed seed: the same file always gives the same range


def pieces(sig, rate, nperseg=NPERSEG):
    """Power spectrum of every half-overlapping Hann-windowed piece.
    Returns (freqs, P) with P shaped (n_pieces, n_freqs). Their mean is the Welch spectrum."""
    nperseg = min(nperseg, len(sig))
    f, _, S = signal.spectrogram(sig, fs=rate, window="hann", nperseg=nperseg,
                                 noverlap=nperseg // 2, detrend="constant",
                                 scaling="density", mode="psd")
    return f, S.T


def peak(freqs, psd, fmin, fmax):
    """Tallest point between fmin and fmax, refined with a parabola on log power."""
    band = np.where((freqs >= fmin) & (freqs <= fmax))[0]
    i = band[np.argmax(psd[band])]
    if 0 < i < len(psd) - 1:
        a, b, c = np.log(psd[i - 1:i + 2])
        denom = a - 2 * b + c
        shift = 0.5 * (a - c) / denom if denom != 0 else 0.0
        shift = float(np.clip(shift, -0.5, 0.5))
    else:
        shift = 0.0
    df = freqs[1] - freqs[0]
    return float(freqs[i] + shift * df), float(psd[i])


def analyse(path, axis="z", fmin=1.0, fmax=20.0, control=None, nperseg=NPERSEG,
            save=True, quiet=False):
    sig, rate, info = common.axis_in_g(path, axis)
    freqs, P = pieces(sig, rate, nperseg)
    psd = P.mean(axis=0)
    f_peak, p_peak = peak(freqs, psd, fmin, fmax)

    rng = np.random.default_rng(RNG_SEED)
    n = P.shape[0]
    boots = [peak(freqs, P[rng.integers(0, n, n)].mean(axis=0), fmin, fmax)[0]
             for _ in range(N_BOOT)]
    lo, hi = np.percentile(boots, [2.5, 97.5])

    out = {"file": info["file"], **common.parse_name(path), "axis": axis,
           "n_samples": info["n_samples"], "rate_hz": round(rate, 4),
           "dropped_lines": info["dropped_lines"], "n_pieces": n,
           "resolution_hz": round(float(freqs[1] - freqs[0]), 4),
           "f_peak_hz": round(f_peak, 3), "ci95_low_hz": round(float(lo), 3),
           "ci95_high_hz": round(float(hi), 3), "period_s": round(1 / f_peak, 4),
           "control_file": "", "bridge_to_ground_ratio": "", "figure": ""}

    c_psd = None
    if control:
        csig, crate, cinfo = common.axis_in_g(control, axis)
        cf, CP = pieces(csig, crate, nperseg)
        c_psd = np.interp(freqs, cf, CP.mean(axis=0))
        # compare power within +/-1 bin of the bridge peak
        near = np.abs(freqs - f_peak) <= (freqs[1] - freqs[0])
        ratio = float(psd[near].max() / c_psd[near].max())
        out["control_file"] = cinfo["file"]
        out["bridge_to_ground_ratio"] = round(ratio, 1)

    if not quiet:
        print(f"File: {info['file']}   axis {axis}   {info['n_samples']} samples, "
              f"{info['duration_s']:.0f} s, measured rate {rate:.3f} Hz, "
              f"dropped lines {info['dropped_lines']}")
        print(f"Spectrum: {n} pieces of {min(nperseg, len(sig))} samples, "
              f"resolution {freqs[1] - freqs[0]:.3f} Hz, search {fmin}-{fmax} Hz")
        print(f"  PEAK  {f_peak:.3f} Hz   95% range {lo:.3f} - {hi:.3f} Hz   "
              f"period {1 / f_peak:.3f} s")
        if control:
            print(f"  GROUND CHECK  bridge is {out['bridge_to_ground_ratio']} times stronger "
                  f"than the ground at this frequency ({out['control_file']})")
        if n < 5:
            print("  note: fewer than 5 pieces - the range is unreliable; record longer")

    if save:
        plt = common.plt_or_none()
        if plt:
            fig, a = plt.subplots(figsize=(8, 4.5))
            a.semilogy(freqs, psd, label=f"recording ({info['file']})")
            if c_psd is not None:
                a.semilogy(freqs, c_psd, label=f"ground control ({out['control_file']})", alpha=0.8)
            a.axvspan(lo, hi, alpha=0.2, label=f"95% range {lo:.2f}-{hi:.2f} Hz")
            a.axvline(f_peak, linestyle="--", linewidth=1)
            a.set_xlim(0, max(fmax, 2 * f_peak))
            a.set_xlabel("frequency (Hz)")
            a.set_ylabel("power spectral density (g$^2$/Hz)")
            a.set_title(f"Peak {f_peak:.3f} Hz ({axis} axis)")
            a.legend(fontsize=8)
            fig.tight_layout()
            figpath = Path("figures") / f"spectrum_{Path(path).stem}_{axis}.png"
            figpath.parent.mkdir(exist_ok=True)
            fig.savefig(figpath, dpi=150)
            plt.close(fig)
            out["figure"] = str(figpath)
            if not quiet:
                print(f"  figure: {figpath}")
        common.append_result("results/frequencies.csv", out)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("recording")
    p.add_argument("--control", help="ground-control recording from the same bridge")
    p.add_argument("--axis", default="z", choices=["x", "y", "z"])
    p.add_argument("--fmin", type=float, default=1.0)
    p.add_argument("--fmax", type=float, default=20.0)
    p.add_argument("--nperseg", type=int, default=NPERSEG)
    a = p.parse_args()
    analyse(a.recording, a.axis, a.fmin, a.fmax, a.control, a.nperseg)


if __name__ == "__main__":
    main()
