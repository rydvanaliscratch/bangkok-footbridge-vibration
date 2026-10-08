"""
common.py - shared helpers used by every analysis program.

Nothing here is run directly. The other programs import it, so every
program loads files, measures the sample rate and converts units the
same way.
"""

import csv
import subprocess
from datetime import datetime
from pathlib import Path

import numpy as np

COUNTS_PER_G = 16384        # +/-2 g full scale (AFS_SEL = 0)
G = 9.80665                 # standard gravity, m/s^2
AXES = {"x": 1, "y": 2, "z": 3}


def load(path):
    """Read a recording. Returns (t_us, ax, ay, az, not_data).

    Skips '#' notes and the 't_us,ax,ay,az' title line. Lines that are
    not four whole numbers (e.g. junk while the Uno restarts) are
    counted in not_data, never silently dropped.
    """
    rows, not_data = [], 0
    with open(path, encoding="ascii", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#") or line.startswith("t_us"):
                continue
            parts = line.split(",")
            try:
                if len(parts) != 4:
                    raise ValueError
                rows.append([int(p) for p in parts])
            except ValueError:
                not_data += 1
    if not rows:
        raise SystemExit(f"{path}: no data lines found")
    d = np.array(rows, dtype=np.int64)
    return d[:, 0], d[:, 1], d[:, 2], d[:, 3], not_data


def gaps_us(t_us):
    """Gaps between consecutive timestamps, corrected for micros() wraparound."""
    g = np.diff(t_us)
    g[g < 0] += 2**32
    return g


def measured_rate(t_us):
    """True sample rate in Hz, from the median gap. Never assume 200."""
    return 1e6 / float(np.median(gaps_us(t_us)))


def axis_in_g(path, axis="z"):
    """Load one axis, convert counts to g and remove the mean (offset + gravity).

    Returns (signal_g, rate_hz, info) where info describes the file.
    """
    t, ax, ay, az, not_data = load(path)
    raw = {"x": ax, "y": ay, "z": az}[axis]
    sig = raw / COUNTS_PER_G
    sig = sig - sig.mean()
    g = gaps_us(t)
    rate = measured_rate(t)
    missing = int(np.clip(np.round(g / np.median(g)).astype(int) - 1, 0, None).sum())
    info = {"file": Path(path).name, "n_samples": len(t), "rate_hz": rate,
            "duration_s": g.sum() / 1e6, "dropped_lines": missing,
            "not_data_lines": not_data,
            "mean_counts": {"x": float(ax.mean()), "y": float(ay.mean()), "z": float(az.mean())}}
    return sig, rate, info


def parse_name(path):
    """Split YYYYMMDD_HHMM_site_run.csv into its parts."""
    parts = Path(path).stem.split("_")
    if len(parts) >= 4:
        return {"date": parts[0], "time": parts[1], "site": parts[2], "run": "_".join(parts[3:])}
    return {"date": "", "time": "", "site": Path(path).stem, "run": ""}


def code_version():
    """Short git commit id of the code that produced a result, for traceability."""
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                             text=True, check=True, cwd=Path(__file__).parent)
        dirty = subprocess.run(["git", "status", "--porcelain", "."], capture_output=True,
                               text=True, cwd=Path(__file__).parent).stdout.strip()
        return out.stdout.strip() + ("+uncommitted" if dirty else "")
    except Exception:
        return "unknown"


def append_result(csv_path, row):
    """Add one row to a results table, creating the file with a header if needed."""
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    new = not csv_path.exists()
    row = {"analysed_at": datetime.now().isoformat(timespec="seconds"),
           "code_version": code_version(), **row}
    with open(csv_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if new:
            w.writeheader()
        w.writerow(row)


def plt_or_none():
    """matplotlib in file-only mode, or None if not installed."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        return None
