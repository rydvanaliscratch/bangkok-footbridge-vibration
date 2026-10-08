"""
selftest.py - prove the analysis programs give the right answers.

    python3 analysis/selftest.py

It builds fake recordings whose true answers are known, in a temporary
folder (nothing is added to your data), runs every program on them and
checks the answers:

  - a bridge that bounces at 3.20 Hz with 0.80 % damping, excited by
    random footsteps, plus sensor noise like yours (about 26 counts)
  - a ground recording with traffic rumble but no bridge
  - ten heel-drops on that bridge
  - a 25 cm pendulum (0.997 Hz swing, 1.994 Hz string pull)
  - five bridges whose frequency follows span^-1.6 exactly

The fake bridge is a textbook resonator whose damping is known exactly,
so the programs must find 3.20 Hz and about 0.80 %.
"""

import contextlib
import io
import math
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy import signal

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import damping          # noqa: E402
import spectrum         # noqa: E402

RATE = 200.0
NOISE_COUNTS = 26.0
rng = np.random.default_rng(42)


def resonator(x, f, zeta):
    """Two-pole resonator: rings at f and decays with damping ratio zeta."""
    w = 2 * math.pi * f
    r = math.exp(-zeta * w / RATE)
    theta = w * math.sqrt(1 - zeta ** 2) / RATE
    return signal.lfilter([1.0], [1.0, -2 * r * math.cos(theta), r * r], x)


def write(path, z_g, x_g=None, y_g=None, z_offset=15000):
    n = len(z_g)
    t = (np.arange(n) * 5000 + rng.integers(-4, 5, n)).astype(np.int64) + 2_000_000
    def counts(sig, base):
        s = np.zeros(n) if sig is None else sig
        return np.round(base + s * 16384 + rng.normal(0, NOISE_COUNTS, n)).astype(int)
    xs, ys, zs = counts(x_g, 300), counts(y_g, -230), counts(z_g, z_offset)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write("# selftest synthetic recording\n# WHO_AM_I ok (0x68)\nt_us,ax,ay,az\n")
        for row in zip(t, xs, ys, zs):
            f.write("%d,%d,%d,%d\n" % row)


def rms_to(x, level):
    """Scale a signal to a given RMS level in g."""
    return x * level / x.std()


def footsteps(seconds, per_s=2.0, size=0.004):
    n = int(seconds * RATE)
    x = np.zeros(n)
    k = rng.random(n) < per_s / RATE
    x[k] = rng.normal(0, size, k.sum())
    return x


def traffic(seconds, level=0.0015):
    n = int(seconds * RATE)
    sos = signal.butter(2, [0.5, 15], btype="bandpass", fs=RATE, output="sos")
    w = signal.sosfilt(sos, rng.normal(0, 1, n))
    return level * w / w.std()


checks = []


def check(name, ok, detail):
    checks.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def main():
    F, ZETA = 3.20, 0.008
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        raw = Path("data/raw")
        print("Building fake recordings (about 20 s)...")
        # ambient: footsteps set the bridge ringing at about 5 mg RMS, plus traffic at 1.5 mg
        write(raw / "20261010_0930_bridgeT_ambient.csv", rms_to(resonator(footsteps(900), F, ZETA), 0.005) + traffic(900))
        write(raw / "20261010_0950_bridgeT_control.csv", traffic(300))
        d = np.zeros(int(300 * RATE))
        for k in range(10):
            d[int((5 + 28 * k) * RATE)] = 0.12
        ring = resonator(d, F, ZETA)
        ring = ring * 0.05 / np.abs(ring).max()          # each heel-drop rings at about 50 mg
        write(raw / "20261010_0945_bridgeT_decay.csv", ring + rms_to(resonator(footsteps(300), F, ZETA), 0.0005))
        tp = np.arange(int(60 * RATE)) / RATE
        fp = 1 / (2 * math.pi * math.sqrt(0.25 / 9.81))
        write(Path("data/calibration/20261004_1000_bench_pendulum.csv"),
              z_g=0.02 * np.cos(2 * 2 * math.pi * fp * tp), x_g=0.15 * np.sin(2 * math.pi * fp * tp))

        quiet = io.StringIO()
        print("\nChecks:")
        with contextlib.redirect_stdout(quiet):
            r = spectrum.analyse(raw / "20261010_0930_bridgeT_ambient.csv",
                                 control=raw / "20261010_0950_bridgeT_control.csv")
        check("natural frequency", abs(r["f_peak_hz"] - F) < 0.02,
              f"found {r['f_peak_hz']} Hz, true {F} Hz")
        check("95% range contains the truth", r["ci95_low_hz"] - 0.01 <= F <= r["ci95_high_hz"] + 0.01,
              f"{r['ci95_low_hz']}-{r['ci95_high_hz']} Hz")
        check("measured sample rate", abs(r["rate_hz"] - 200) < 0.01, f"{r['rate_hz']} Hz")
        check("ground check", r["bridge_to_ground_ratio"] >= 10,
              f"bridge {r['bridge_to_ground_ratio']}x stronger than ground")

        with contextlib.redirect_stdout(quiet):
            summ, res = damping.analyse(raw / "20261010_0945_bridgeT_decay.csv", r["f_peak_hz"])
        check("heel-drops found", len(res) == 10, f"{len(res)} of 10")
        check("damping", summ is not None and abs(summ["zeta_mean"] - ZETA) < 0.15 * ZETA,
              f"found {100 * summ['zeta_mean']:.3f} %, true {100 * ZETA:.2f} %" if summ else "none usable")

        import pendulum_check
        sys.argv = ["pendulum_check.py", "data/calibration/20261004_1000_bench_pendulum.csv"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pendulum_check.main()
        check("pendulum B5", "RESULT: PASS" in buf.getvalue(),
              [l.strip() for l in buf.getvalue().splitlines() if "axis" in l and "peak" in l][0])

        spans = [14.0, 19.0, 24.0, 31.0, 40.0]
        with open("data/bridges.csv", "w") as f:
            f.write("bridge_id,span_m\n")
            for i, L in enumerate(spans):
                f.write(f"span{i},{L}\n")
        for i, L in enumerate(spans):
            fi = 400 * L ** -1.6                          # 5.9 Hz at 14 m down to 1.1 Hz at 40 m
            write(raw / f"20261017_1000_span{i}_ambient.csv", rms_to(resonator(footsteps(240), fi, 0.01), 0.005))
            with contextlib.redirect_stdout(quiet):
                spectrum.analyse(raw / f"20261017_1000_span{i}_ambient.csv", fmin=0.5)
        import span_fit
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            span_fit.main()
        slope = float(buf.getvalue().split("Slope ")[1].split()[0])
        check("span slope", abs(slope + 1.6) < 0.15, f"found {slope}, true -1.60")

    print(f"\n{'ALL PASS' if all(checks) else 'SOME CHECKS FAILED'} ({sum(checks)} of {len(checks)})")


if __name__ == "__main__":
    main()
