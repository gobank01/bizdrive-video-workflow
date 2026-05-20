#!/usr/bin/env python3
"""Set the composition duration across index.html consistently (Template 03).

Template 03's index.html carries a reference duration (103.561333) in several
spots: the root composition, background, bottomVideo (data-duration +
data-motion-duration), the captions mount, the caption scrim, and the JS
`compositionDuration` constant. A new job has a different duration, and all of
them must match — a mismatch produces lint errors and timing drift.

The TikTok follow end-card (#tiktok-follow-mount) is special: it is a fixed
4.5s block that must always finish at the composition end, so its data-start
is repositioned to (new duration - 4.5) rather than rewritten 1:1.

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
TIKTOK_CARD_DURATION = 4.5


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

    # Reposition the TikTok follow end-card to finish at the composition end.
    card_start = max(new_dur - TIKTOK_CARD_DURATION, 0.0)
    card_start_str = f"{card_start:.6f}"
    html, card_hits = re.subn(
        r'(id="tiktok-follow-mount"[^>]*?\sdata-start=")[\d.]+(")',
        rf'\g<1>{card_start_str}\g<2>',
        html,
    )

    INDEX.write_text(html, encoding="utf-8")
    print(f"  Composition duration: {old_dur} -> {new_str}")
    print(f"  Rewrote {count} occurrence(s) in index.html")
    if card_hits:
        print(f"  TikTok follow end-card start -> {card_start_str} (ends at composition end)")


if __name__ == "__main__":
    main()
