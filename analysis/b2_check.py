"""
b2_check.py - gate B2 (does the sensor read gravity correctly?) from six
still recordings, one per face of a small box the sensor is taped to.

    python3 analysis/b2_check.py 20261012

It looks in data/calibration/ for files made on that date named
    <date>_<time>_bench_tilt_<position>.csv
with position = flat, upside, side1, side2, side3, side4.
(Recorded with: python3 analysis/capture.py bench tilt 15 <position>)

Known answer: in each position one axis points straight up or down and
must read +/-16384 counts (1 g) within +/-800; the other two axes are
level and must read 0 within +/-800. The six positions must point each
axis up once and down once.

From each up/down pair it also works out the axis's
    offset = (up + down) / 2      (reading at zero g - should be 0)
    scale  = (up - down) / 2      (counts per g - should be 16384)
and compares the offset with the MPU-6050 datasheet's factory tolerance
(+/-50 mg for X and Y, +/-80 mg for Z). That comparison is information,
not part of the pass mark.
"""

import sys
from pathlib import Path

import numpy as np

from common import COUNTS_PER_G, load, append_result

POSITIONS = ["flat", "upside", "side1", "side2", "side3", "side4"]
SKIP_S = 1.0                  # ignore the first second (Uno restart, hand leaving the box)
TOL = 800                     # pass window, counts (about 0.05 g)
MOVED_SD = 200                # SD above this means the box moved during the recording
DATASHEET_MG = {"x": 50, "y": 50, "z": 80}


def find(date, position):
    files = sorted(Path("data/calibration").glob(f"{date}_*_bench_tilt_{position}.csv"))
    if not files:
        return None, 0
    return files[-1], len(files)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    date = sys.argv[1]

    rows = []
    for pos in POSITIONS:
        path, n = find(date, pos)
        if path is None:
            print(f"Missing: no file for position '{pos}' on {date}. Record it, then run again.")
            sys.exit(1)
        if n > 1:
            print(f"Note: {n} files for '{pos}'; using the latest, {path.name}")
        t, ax, ay, az, not_data = load(path)
        skip = int(SKIP_S * 200)
        a = np.vstack([ax, ay, az]).T[skip:].astype(float)
        if len(a) < 400:
            print(f"{path.name}: only {len(a)} usable samples - record at least 5 s.")
            sys.exit(1)
        mean = a.mean(axis=0)
        sd = a.std(axis=0, ddof=1)
        k = int(np.argmax(np.abs(mean)))           # the axis feeling gravity
        rows.append({"pos": pos, "file": path.name, "n": len(a), "mean": mean, "sd": sd,
                     "axis": "xyz"[k], "sign": "+" if mean[k] > 0 else "-"})

    print(f"B2 - gravity check, {date}\n")
    print(f"{'position':9} {'ax':>8} {'ay':>8} {'az':>8}   gravity on   check")
    all_ok = True
    for r in rows:
        m = r["mean"]
        k = "xyz".index(r["axis"])
        g_ok = abs(abs(m[k]) - COUNTS_PER_G) <= TOL
        level_ok = all(abs(m[j]) <= TOL for j in range(3) if j != k)
        still = all(r["sd"] < MOVED_SD)
        ok = g_ok and level_ok and still
        all_ok &= ok
        why = [] if ok else (["gravity axis off"] if not g_ok else []) + \
              (["level axes off"] if not level_ok else []) + (["moved"] if not still else [])
        print(f"{r['pos']:9} {m[0]:8.0f} {m[1]:8.0f} {m[2]:8.0f}   {r['sign']}{r['axis']}"
              f"          {'ok' if ok else 'FAIL: ' + ', '.join(why)}")

    seen = sorted(r["sign"] + r["axis"] for r in rows)
    if seen != sorted(["+x", "-x", "+y", "-y", "+z", "-z"]):
        print(f"\nThe six positions pointed gravity along {seen}.")
        print("Each axis must point up once and down once - check the box was turned onto")
        print("all six faces, one recording each, and that the labels match the faces.")
        sys.exit(1)

    print(f"\n{'axis':4} {'up':>8} {'down':>8} {'offset':>8} {'offset mg':>10} {'datasheet':>10} {'scale':>8}")
    for axis in "xyz":
        k = "xyz".index(axis)
        up = next(r["mean"][k] for r in rows if r["axis"] == axis and r["sign"] == "+")
        down = next(r["mean"][k] for r in rows if r["axis"] == axis and r["sign"] == "-")
        offset = (up + down) / 2
        scale = (up - down) / 2
        mg = 1000 * offset / COUNTS_PER_G
        inside = abs(mg) <= DATASHEET_MG[axis]
        print(f"{axis:4} {up:8.0f} {down:8.0f} {offset:8.0f} {mg:10.1f} "
              f"{'within' if inside else 'OUTSIDE':>7} {DATASHEET_MG[axis]:>2} {scale:8.0f}")
        append_result("results/b2_calibration.csv", {
            "date": date, "axis": axis, "up_counts": round(up, 1), "down_counts": round(down, 1),
            "offset_counts": round(offset, 1), "offset_mg": round(mg, 2),
            "datasheet_limit_mg": DATASHEET_MG[axis], "scale_counts_per_g": round(scale, 1)})

    # Information only: the same check after removing each axis's own offset.
    # If this passes while the main check fails, the only problem is the offset,
    # which every vibration analysis removes anyway (it subtracts the mean).
    offsets = {}
    for axis in "xyz":
        k = "xyz".index(axis)
        up = next(r["mean"][k] for r in rows if r["axis"] == axis and r["sign"] == "+")
        down = next(r["mean"][k] for r in rows if r["axis"] == axis and r["sign"] == "-")
        offsets[k] = (up + down) / 2
    corrected_ok = True
    for r in rows:
        m = np.array([r["mean"][j] - offsets[j] for j in range(3)])
        k = "xyz".index(r["axis"])
        corrected_ok &= abs(abs(m[k]) - COUNTS_PER_G) <= TOL
        corrected_ok &= all(abs(m[j]) <= TOL for j in range(3) if j != k)

    print(f"\nRESULT: {'PASS' if all_ok else 'FAIL'}   (each reading within +/-{TOL} counts of 1 g or 0)")
    print(f"Same check after removing each axis's offset (information only): "
          f"{'PASS' if corrected_ok else 'FAIL'}")
    print("Offsets and scales added to results/b2_calibration.csv")


if __name__ == "__main__":
    main()
