#!/usr/bin/env python3
"""
Slice an ElevenLabs Scribe v2 raw transcript by a [start_ms, end_ms] window
and rebase timestamps to the new clip's timeline (t' = t - start_ms/1000).

Used by tools/01-longform-shorts/split.sh to give each child job its own
raw-elevenlabs.json without re-calling the ElevenLabs API.

Usage:
    python3 tools/01-longform-shorts/slice-transcript.py \\
        --in  staging/longform/<slug>/raw-elevenlabs.json \\
        --out jobs/<date>-<slug>-clip01/intermediates/raw-elevenlabs.json \\
        --start-ms 124300 \\
        --end-ms   207800

The output keeps the same schema as the input. Words whose [start, end]
fall fully inside the window are kept; words partially overlapping the
boundary are clipped to the window edge.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def slice_words(words: list[dict], start_s: float, end_s: float) -> list[dict]:
    out = []
    for w in words:
        w_start = float(w.get("start", 0.0))
        w_end = float(w.get("end", w_start))
        # Drop words fully outside the window
        if w_end <= start_s or w_start >= end_s:
            continue
        # Clip partial overlaps
        new_start = max(w_start, start_s) - start_s
        new_end = min(w_end, end_s) - start_s
        if new_end <= new_start:
            continue
        nw = dict(w)
        nw["start"] = round(new_start, 4)
        nw["end"] = round(new_end, 4)
        out.append(nw)
    return out


def slice_segments(segments: list[dict], start_s: float, end_s: float) -> list[dict]:
    """Some ElevenLabs payloads also carry segment-level grouping."""
    out = []
    for seg in segments:
        s_start = float(seg.get("start", 0.0))
        s_end = float(seg.get("end", s_start))
        if s_end <= start_s or s_start >= end_s:
            continue
        new_seg = dict(seg)
        new_seg["start"] = round(max(s_start, start_s) - start_s, 4)
        new_seg["end"] = round(min(s_end, end_s) - start_s, 4)
        if "words" in seg and isinstance(seg["words"], list):
            new_seg["words"] = slice_words(seg["words"], start_s, end_s)
        out.append(new_seg)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--start-ms", type=int, required=True)
    ap.add_argument("--end-ms", type=int, required=True)
    args = ap.parse_args()

    if args.end_ms <= args.start_ms:
        print("✗ end-ms must be > start-ms", file=sys.stderr)
        return 1

    start_s = args.start_ms / 1000.0
    end_s = args.end_ms / 1000.0
    new_duration = round(end_s - start_s, 4)

    raw = json.loads(Path(args.inp).read_text())

    sliced: dict = {
        "language": raw.get("language", "th"),
        "duration": new_duration,
        "provider": raw.get("provider", "elevenlabs"),
        "model": raw.get("model"),
        "sliced_from": {
            "source": str(args.inp),
            "start_ms": args.start_ms,
            "end_ms": args.end_ms,
        },
    }

    if isinstance(raw.get("words"), list):
        sliced["words"] = slice_words(raw["words"], start_s, end_s)

    if isinstance(raw.get("segments"), list):
        sliced["segments"] = slice_segments(raw["segments"], start_s, end_s)

    if "text" in raw and isinstance(sliced.get("words"), list):
        sliced["text"] = " ".join(w.get("text", w.get("word", ""))
                                  for w in sliced["words"]).strip()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(sliced, ensure_ascii=False, indent=2))

    word_count = len(sliced.get("words", []))
    print(f"  ✓ sliced {word_count} words, {new_duration}s → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
