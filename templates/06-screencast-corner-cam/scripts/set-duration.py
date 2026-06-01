#!/usr/bin/env python3
"""Set the composition duration across index.html consistently.

Template 01's index.html carries the v88 reference duration (103.561333) in
several spots: the root composition, background, topVideo (data-duration +
data-motion-duration), bottomVideo, the captions mount, and the JS
`compositionDuration` constant. A new job has a different duration, and all of
them must match — a mismatch produces lint errors and timing drift.

Usage (run from the job workspace):
    python3 scripts/set-duration.py <seconds>

Example:
    python3 scripts/set-duration.py 92.748632

This rewrites EVERY duration token in index.html that currently equals the
old composition duration. It auto-detects the old value from the #root
element's data-duration, so it works no matter what the file currently holds.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/set-duration.py <seconds>", file=sys.stderr)
        sys.exit(1)

    try:
        new_dur = float(sys.argv[1])
    except ValueError:
        print(f"Error: '{sys.argv[1]}' is not a number", file=sys.stderr)
        sys.exit(1)

    html = INDEX.read_text(encoding="utf-8")

    # Detect the current composition duration from #root data-duration
    m = re.search(r'id="root"[^>]*data-duration="(\d+\.?\d*)"', html)
    if not m:
        print("Error: could not find #root data-duration in index.html", file=sys.stderr)
        sys.exit(1)
    old_dur = m.group(1)

    new_str = f"{new_dur:.6f}"
    # Replace every literal occurrence of the old duration string.
    # Covers data-duration, data-motion-duration, and the JS constant.
    count = html.count(old_dur)
    html = html.replace(old_dur, new_str)

    INDEX.write_text(html, encoding="utf-8")
    print(f"  Composition duration: {old_dur} -> {new_str}")
    print(f"  Rewrote {count} occurrence(s) in index.html")


if __name__ == "__main__":
    main()
