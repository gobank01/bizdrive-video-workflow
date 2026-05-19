#!/usr/bin/env python3
"""Detect speech segments using Silero VAD.

Runs inside ~/.ii23/vad-env (sibling venv created by install_vad.sh).
Outputs JSON list of speech ranges [{start, end}, ...] in seconds.

Usage:
  ~/.ii23/vad-env/bin/python3 vad_detect.py <input.wav> [options]

Options:
  --min-silence-ms N   Gaps shorter than this are NOT cut (default 300)
  --min-speech-ms N    Speech blips shorter than this are dropped as noise (default 200)
  --pad-ms N           Padding added to each speech range edge (default 200)
  --merge-gap-ms N     After VAD, merge adjacent speech ranges that are this close
                       or closer. Default 0 (no merge). Use 300+ for long videos
                       (>30 min) to keep CapCut/NLE segment count manageable.
  --output PATH        Write JSON to file (else stdout)

Tuning by content type:
  TikTok/Reels:        --min-silence-ms 300 --pad-ms 150 --merge-gap-ms 0
  Talking head (default): --min-silence-ms 300 --pad-ms 200 --merge-gap-ms 0
  Long-form > 30min:   --min-silence-ms 500 --pad-ms 250 --merge-gap-ms 300
  Podcast / interview: --min-silence-ms 800 --pad-ms 300 --merge-gap-ms 300

Why merge-gap-ms matters for long video:
  A 2hr talk can produce 1500+ raw speech ranges. CapCut starts lagging at ~500
  segments, may crash at ~1000+. Merging ranges <300ms apart cuts segment count
  by ~half without changing what audio is kept (the gaps were too short to be
  perceived as cuts anyway).

The Silero model loads from ~/.cache/torch on first run (~1.8MB download).
"""

import argparse
import json
import sys
from typing import List, Dict

try:
    from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
except ImportError:
    print("error: silero_vad not installed. Run install_vad.sh first.", file=sys.stderr)
    sys.exit(2)


def merge_close(ranges: List[Dict], merge_gap_s: float) -> List[Dict]:
    """Merge adjacent speech ranges whose gap is <= merge_gap_s."""
    if merge_gap_s <= 0 or not ranges:
        return ranges
    out = [dict(ranges[0])]
    for r in ranges[1:]:
        if r["start"] - out[-1]["end"] <= merge_gap_s:
            out[-1]["end"] = r["end"]
        else:
            out.append(dict(r))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", help="path to mono 16kHz WAV (extract with ffmpeg first)")
    ap.add_argument("--min-silence-ms", type=int, default=300)
    ap.add_argument("--min-speech-ms", type=int, default=200)
    ap.add_argument("--pad-ms", type=int, default=200)
    ap.add_argument("--merge-gap-ms", type=int, default=0,
                    help="post-merge ranges this close together (default 0 = no merge)")
    ap.add_argument("--output", help="write JSON here (default: stdout)")
    args = ap.parse_args()

    model = load_silero_vad()
    wav = read_audio(args.audio, sampling_rate=16000)
    speech = get_speech_timestamps(
        wav, model,
        sampling_rate=16000,
        return_seconds=True,
        min_silence_duration_ms=args.min_silence_ms,
        min_speech_duration_ms=args.min_speech_ms,
        speech_pad_ms=args.pad_ms,
    )

    raw_count = len(speech)
    if args.merge_gap_ms > 0:
        speech = merge_close(speech, args.merge_gap_ms / 1000.0)
        print(f"merged: {raw_count} raw → {len(speech)} ranges", file=sys.stderr)

    out = json.dumps(speech, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(out)
        print(f"wrote {len(speech)} speech ranges to {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
