#!/usr/bin/env python3
"""stitch.py — stitch chosen takes into one 1080x1920/30fps visual base.

Reads the same shots.json used by gen-shots.js. Per-shot fields used here:
  id     — clip basename ({id}-take{take}.mp4 in outputDir)
  take   — chosen take number after continuity QA (default 1)
  file   — explicit clip path relative to the shots.json (anchor reuse); overrides id/take
  trim   — final seconds of this shot in the episode (default: full clip)
  html   — true = shot is rendered in the composition (end card), skipped here

Every shot gets the same locked post-grade (warm tungsten + teal) so the
model's lighting drift is absorbed into one look. Hard cuts by default —
xfade ghosts on dark footage (see tools/03-deprompter/deprompter.py warning).

Usage: python3 stitch.py <shots.json> -o visual_base.mp4
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# One look for the whole series: teal shadows, warm highlights, slight punch.
GRADE = "eq=contrast=1.05:saturation=1.06,colorbalance=bs=0.06:gs=0.02:rs=-0.02:rh=0.05:bh=-0.04"
NORMALIZE = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=30,setsar=1"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("shots")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    shots_path = Path(args.shots).resolve()
    spec = json.loads(shots_path.read_text())
    out_dir = (shots_path.parent / spec.get("outputDir", "takes")).resolve()

    inputs, filters, labels = [], [], []
    for shot in spec["shots"]:
        if shot.get("html"):
            continue
        if shot.get("file"):
            clip = (shots_path.parent / shot["file"]).resolve()
        else:
            take = shot.get("take", 1)
            clip = out_dir / f"{shot['id']}-take{take}.mp4"
        if not clip.exists():
            sys.exit(f"missing {clip} — run gen-shots.js (or fix 'take'/'file') first")
        i = len(labels)
        inputs += ["-i", str(clip)]
        trim = f"trim=duration={shot['trim']}," if shot.get("trim") else ""
        filters.append(f"[{i}:v]{NORMALIZE},{trim}setpts=PTS-STARTPTS,{GRADE}[v{i}]")
        labels.append(f"[v{i}]")

    if not labels:
        sys.exit("no stitchable shots in spec")

    filter_complex = ";".join(filters) + f";{''.join(labels)}concat=n={len(labels)}:v=1:a=0[out]"
    cmd = ["ffmpeg", "-nostdin", "-y", *inputs,
           "-filter_complex", filter_complex, "-map", "[out]",
           "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
           "-an", args.output]
    subprocess.run(cmd, check=True)

    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", args.output],
        capture_output=True, text=True, check=True).stdout.strip()
    print(f"stitched {len(labels)} shots -> {args.output} ({float(dur):.2f}s)")


if __name__ == "__main__":
    main()
