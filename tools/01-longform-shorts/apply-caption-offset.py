#!/usr/bin/env python3
"""
Shift every caption group's [start, end] earlier by N ms.

Why: ElevenLabs Scribe v2 returns phrase-level entries whose `start` is often
80-200ms after the actual audio onset (perceived as "captions feel late").
A universal -120 ms shift fixes ~80% of cases without re-aligning.

Usage:
    python3 tools/01-longform-shorts/apply-caption-offset.py <input.json> <output.json> --offset-ms 120

Behaviour:
- Every group's start AND end shifted -offset_ms (clamped to [0, duration]).
- Span (end - start) is preserved.
- Token timings inside groups are NOT stored separately; the downstream
  build-{burst,highlight}-captions.py re-derives per-token timing from the
  group window, so shifting the group window is enough.
- Original file is never mutated.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--offset-ms", type=int, default=120,
                    help="Shift every group earlier by this many ms (default 120)")
    args = ap.parse_args()

    offset_s = args.offset_ms / 1000.0
    data = json.loads(Path(args.inp).read_text())
    duration = float(data.get("duration", 0))

    if "groups" not in data:
        print("✗ caption-groups schema missing 'groups'", file=sys.stderr)
        return 1

    shifted = 0
    for g in data["groups"]:
        new_start = max(0.0, float(g["start"]) - offset_s)
        new_end = max(new_start + 0.01, float(g["end"]) - offset_s)
        if duration > 0:
            new_end = min(new_end, duration)
            new_start = min(new_start, new_end - 0.01)
        g["start"] = round(new_start, 3)
        g["end"] = round(new_end, 3)
        shifted += 1

    notes = data.setdefault("notes", [])
    if isinstance(notes, list):
        notes.append(f"applied caption offset: -{args.offset_ms}ms (start+end shifted earlier)")

    Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"  ✓ shifted {shifted} groups by -{args.offset_ms}ms → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
