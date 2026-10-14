"""
analyse_bridge.py - everything for one bridge, in one command.

    python3 analysis/analyse_bridge.py bridge01

Finds that bridge's newest ambient, control and decay recordings in
data/raw/, then:
 1. spectrum.py on ambient, compared with control  -> natural frequency
 2. damping.py on decay, using that frequency      -> damping ratio
and prints a plain-English summary. Results are added to
results/frequencies.csv and results/damping.csv; figures go in figures/.
"""

import argparse
import sys
from pathlib import Path

import damping
import spectrum

RAW = Path("data/raw")
GROUND_RULE = 10        # fixed 14 Oct 2026 (predictions file): bridge peak >= 10x the ground's power at that frequency


def newest(site, run):
    files = sorted(RAW.glob(f"*_{site}_{run}.csv"))
    return files[-1] if files else None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("site", help="bridge ID as used when recording, e.g. bridge01")
    p.add_argument("--fmin", type=float, default=1.0)
    p.add_argument("--fmax", type=float, default=20.0)
    a = p.parse_args()

    amb, ctl, dec = (newest(a.site, r) for r in ("ambient", "control", "decay"))
    print(f"Bridge {a.site}")
    print(f"  ambient: {amb.name if amb else 'MISSING'}")
    print(f"  control: {ctl.name if ctl else 'MISSING'}")
    print(f"  decay:   {dec.name if dec else 'MISSING'}\n")
    if not amb:
        sys.exit("No ambient recording - nothing to analyse.")

    print("=== 1. Natural frequency (ambient vs ground) ===")
    r = spectrum.analyse(amb, fmin=a.fmin, fmax=a.fmax, control=ctl)
    f = r["f_peak_hz"]

    print("\n=== 2. Damping (heel-drops) ===")
    summ = None
    if dec:
        summ, _ = damping.analyse(dec, f)
    else:
        print("  no decay recording")

    print("\n=== Summary in plain words ===")
    print(f"  The bridge bounces at about {f:.2f} times per second "
          f"(95% range {r['ci95_low_hz']:.2f}-{r['ci95_high_hz']:.2f} Hz), "
          f"a period of {r['period_s']:.2f} s.")
    if ctl:
        ratio = r["bridge_to_ground_ratio"]
        verdict = "belongs to the bridge" if ratio >= GROUND_RULE else "is NOT clearly the bridge's - check the figure"
        print(f"  On the bridge that peak is {ratio}x stronger than on the ground, so it {verdict} "
              f"(proposed rule: at least {GROUND_RULE}x).")
    else:
        print("  No ground control: the peak cannot be confirmed as the bridge's.")
    if summ:
        print(f"  Its bouncing dies away with damping of {100 * summ['zeta_mean']:.2f} % "
              f"(from {summ['n']} heel-drops, spread {100 * summ['zeta_sd']:.2f} %).")
    band = "outside" if 1 / f < 1.0 else "INSIDE"
    print(f"  Period {1 / f:.2f} s is {band} the 1-6 s band the clay amplified in 2025.")
    lo, hi = r["ci95_low_hz"], r["ci95_high_hz"]
    def overlaps(a, b):
        return hi >= a and lo <= b
    if overlaps(1.6, 2.4):
        walk = "overlaps normal walking pace (1.6-2.4 Hz)"
    elif overlaps(3.2, 4.8):
        walk = "overlaps TWICE walking pace (3.2-4.8 Hz), where footsteps can also push a bridge"
    else:
        walk = "is clear of walking pace (1.6-2.4 Hz) and twice walking pace (3.2-4.8 Hz)"
    print(f"  Its 95% range {lo:.2f}-{hi:.2f} Hz {walk}.")
    print(f"  Comfort check: {'below' if f < 5 else 'above'} 5 Hz, the level below which European guidance asks for a check.")
    print("\nNext: note these numbers in docs/build-log.md, then git add / commit / push.")


if __name__ == "__main__":
    main()
