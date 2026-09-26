"""
capture.py - record the footbridge logger's serial output to a CSV file.

Run from the repository folder, with the Arduino Serial Monitor CLOSED:

    python3 analysis/capture.py SITE RUN SECONDS

Examples:
    python3 analysis/capture.py bench rest 60          # gates B3 + B4
    python3 analysis/capture.py bench pendulum 60      # gate B5
    python3 analysis/capture.py bridge01 ambient 900   # 15 min on a bridge

Every line the Uno sends is written to the file exactly as received,
including its '#' header lines. Nothing is filtered or changed here;
the analysis scripts decide which lines to use.
"""

import sys
import time
from datetime import datetime
from pathlib import Path

import serial

PORT = "/dev/cu.usbmodem1101"   # the Uno, as shown in Arduino IDE > Tools > Port
BAUD = 115200                   # must match Serial.begin(115200) in logger.ino
BOOT_WAIT_S = 2.0               # opening the port resets the Uno; let it restart

RUN_TYPES = {"ambient", "decay", "control", "remount", "pendulum", "rest", "tilt"}


def main():
    # 1. Read the three words typed after the script name.
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    site = sys.argv[1]
    run = sys.argv[2]
    seconds = float(sys.argv[3])

    if run not in RUN_TYPES:
        print(f"Unknown run type '{run}'. Use one of: {', '.join(sorted(RUN_TYPES))}")
        sys.exit(1)

    # 2. Build the output file name, following data/README.md:
    #    YYYYMMDD_HHMM_<site>_<run>.csv
    folder = Path("data/calibration") if site == "bench" else Path("data/raw")
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    path = folder / f"{stamp}_{site}_{run}.csv"
    if path.exists():
        print(f"{path} already exists (same site, run and minute). Wait a minute and run again.")
        sys.exit(1)

    # 3. Open the USB connection to the Uno, then wait while it restarts.
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
    except serial.SerialException as err:
        print(f"Could not open {PORT}: {err}")
        print("Is the Uno plugged in, and is the Arduino Serial Monitor closed?")
        sys.exit(1)
    time.sleep(BOOT_WAIT_S)

    # 4. Create the file. Mode "x" refuses to overwrite an existing file,
    #    so a recording can never be destroyed by a repeated name.
    n_lines = 0
    silent_seconds = 0
    with open(path, "x", newline="") as f:
        f.write(f"# capture.py: started {datetime.now().isoformat(timespec='seconds')}, "
                f"port {PORT}, baud {BAUD}, requested {seconds:g} s\n")
        print(f"Recording {seconds:g} s to {path}   (Control+C stops early)")

        start = time.monotonic()
        try:
            # 5. Copy lines from the Uno into the file until time is up.
            while time.monotonic() - start < seconds:
                raw = ser.readline()            # waits for one line, at most 1 s
                if not raw:                     # nothing arrived within 1 s
                    silent_seconds += 1
                    print("  warning: no data for 1 s - is the board plugged in?")
                    continue
                line = raw.decode("ascii", errors="replace").rstrip("\r\n")
                f.write(line + "\n")
                n_lines += 1
                if n_lines % 1000 == 0:
                    elapsed = time.monotonic() - start
                    print(f"  {n_lines} lines, {elapsed:.0f} s")
        except KeyboardInterrupt:
            print("  stopped early by Control+C")

    # 6. Close the connection and report.
    ser.close()
    elapsed = time.monotonic() - start
    print(f"Saved {n_lines} lines in {elapsed:.1f} s to {path}")
    if silent_seconds:
        print(f"  {silent_seconds} s with no data - check the cable and connections")


if __name__ == "__main__":
    main()
