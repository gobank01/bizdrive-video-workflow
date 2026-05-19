#!/usr/bin/env python3
"""Convert Silero VAD speech ranges JSON to EDL JSON for apply_edits.py.

Input  (from vad_detect.py):  [{"start": 1.02, "end": 3.84}, ...]   (seconds)
Output (for apply_edits.py): {"segments": [{"start_ms": 1020, "end_ms": 3840}, ...]}

The two scripts speak different shapes because:
  - VAD naturally talks in seconds (model output)
  - apply_edits.py uses milliseconds (ffmpeg-style, less precision drift on long cuts)

This converter is the bridge.
"""

import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("speech_json", help="speech ranges JSON from vad_detect.py")
    ap.add_argument("-o", "--output", help="write EDL JSON here (default: stdout)")
    ap.add_argument("--language", default="unknown",
                    help="optional language tag to embed in EDL (e.g. 'th')")
    args = ap.parse_args()

    with open(args.speech_json, encoding="utf-8") as f:
        speech = json.load(f)

    if not isinstance(speech, list):
        print(f"error: expected list, got {type(speech).__name__}", file=sys.stderr)
        sys.exit(1)

    segments = []
    total_kept = 0.0
    for s in speech:
        start_ms = int(round(s["start"] * 1000))
        end_ms = int(round(s["end"] * 1000))
        if end_ms <= start_ms:
            continue  # skip degenerate
        segments.append({"start_ms": start_ms, "end_ms": end_ms})
        total_kept += (end_ms - start_ms) / 1000.0

    edl = {
        "segments": segments,
        "language": args.language,
        "kept_seconds": round(total_kept, 3),
        "source": "vad_detect.py",
    }

    out = json.dumps(edl, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"wrote {len(segments)} EDL segments ({total_kept:.1f}s kept) to {args.output}",
              file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
