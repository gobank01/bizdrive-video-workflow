#!/usr/bin/env python3
"""
assembly.py — Merge multiple video clips into a single timeline.

The "assembly cut" is the first pass of editing: arrange the takes you want
into one continuous video. No silence trimming, no retake removal — just stitch.

Usage:
  python3 assembly.py CLIP1.mp4 CLIP2.mp4 CLIP3.mp4 -o assembled.mp4
  python3 assembly.py clip*.mp4 -o assembled.mp4   # shell glob
  python3 assembly.py --from-list clips.txt -o assembled.mp4

Inputs:
  - 2+ video files (mp4/mov/mkv) — order matters, it's the timeline order
  - All clips should be the same resolution + fps + audio format. If they
    differ, the script will re-encode to a common spec.

Output:
  - assembled.mp4 — single continuous video, all clips back-to-back
  - assembly.json — manifest (list of source clips + their cumulative offsets)

Notes:
  - Uses ffmpeg `concat demuxer` when codecs match (fast, no re-encode).
  - Falls back to re-encode + concat filter when codecs differ (slower but safe).
  - Honors CLAUDE.md Rule #10: re-encoded output gets dense keyframes
    (-r 30 -g 30 -keyint_min 30 -movflags +faststart).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple


def ffprobe_codec(path: str) -> Tuple[Optional[str], Optional[str], Optional[float], Optional[str]]:
    """Return (vcodec, acodec, duration_sec, resolution) for a file."""
    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-show_entries", "stream=codec_type,codec_name,width,height:format=duration",
            "-of", "json", path,
        ], stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe failed on {path}: {e.output.decode('utf-8', errors='replace')}")

    data = json.loads(out)
    vcodec = acodec = resolution = None
    for s in data.get("streams", []):
        if s.get("codec_type") == "video":
            vcodec = s.get("codec_name")
            w, h = s.get("width"), s.get("height")
            if w and h:
                resolution = f"{w}x{h}"
        elif s.get("codec_type") == "audio":
            acodec = s.get("codec_name")
    dur = float(data.get("format", {}).get("duration", 0)) or None
    return vcodec, acodec, dur, resolution


def codecs_match(clips: List[str]) -> bool:
    """Check whether all clips have the same vcodec/acodec/resolution."""
    spec = None
    for clip in clips:
        v, a, _, r = ffprobe_codec(clip)
        sig = (v, a, r)
        if spec is None:
            spec = sig
        elif spec != sig:
            return False
    return True


def concat_stream_copy(clips: List[str], output: str) -> None:
    """Fast concat: stream copy (no re-encode). Requires matching codecs."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for clip in clips:
            abs_path = os.path.abspath(clip).replace("'", r"'\''")
            f.write(f"file '{abs_path}'\n")
        list_path = f.name

    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", list_path,
            "-c", "copy",
            "-movflags", "+faststart",
            output,
        ], check=True)
    finally:
        os.unlink(list_path)


def concat_reencode(clips: List[str], output: str, fps: int = 30, crf: int = 20) -> None:
    """Safe concat: re-encode to common spec. Honors CLAUDE.md Rule #10."""
    inputs = []
    filter_parts = []
    for i, clip in enumerate(clips):
        inputs += ["-i", clip]
        filter_parts.append(f"[{i}:v:0][{i}:a:0]")
    filter_str = "".join(filter_parts) + f"concat=n={len(clips)}:v=1:a=1[v][a]"

    subprocess.run([
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_str,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", str(crf),
        "-r", str(fps), "-g", str(fps), "-keyint_min", str(fps),
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "128k",
        output,
    ], check=True)


def write_manifest(clips: List[str], output: str, manifest_path: str, mode: str) -> None:
    items = []
    cumulative = 0.0
    for clip in clips:
        _, _, dur, res = ffprobe_codec(clip)
        items.append({
            "path": os.path.abspath(clip),
            "duration_sec": dur,
            "resolution": res,
            "start_in_assembly_sec": cumulative,
        })
        cumulative += dur or 0
    manifest = {
        "skill": "ii23-clean-cut",
        "mode": "assembly",
        "concat_method": mode,
        "output": os.path.abspath(output),
        "total_duration_sec": cumulative,
        "clips": items,
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("clips", nargs="*", help="Video files in timeline order")
    parser.add_argument("--from-list", help="Path to a text file with one clip path per line")
    parser.add_argument("--output", "-o", required=True, help="Output video path")
    parser.add_argument("--force-reencode", action="store_true",
                        help="Always re-encode (slower, but safe across codecs)")
    parser.add_argument("--fps", type=int, default=30, help="Output fps (if re-encoding). Default 30.")
    parser.add_argument("--crf", type=int, default=20, help="x264 CRF (if re-encoding). Default 20.")
    parser.add_argument("--manifest", default=None,
                        help="Path to manifest JSON. Default: <output>.assembly.json")
    args = parser.parse_args()

    clips: List[str] = list(args.clips)
    if args.from_list:
        with open(args.from_list, "r", encoding="utf-8") as f:
            clips += [line.strip() for line in f if line.strip() and not line.startswith("#")]
    if len(clips) < 2:
        print("Need at least 2 clips to assemble.", file=sys.stderr)
        return 2

    for clip in clips:
        if not os.path.exists(clip):
            print(f"Clip not found: {clip}", file=sys.stderr)
            return 2

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    manifest_path = args.manifest or args.output + ".assembly.json"

    can_copy = (not args.force_reencode) and codecs_match(clips)
    mode = "stream-copy" if can_copy else "re-encode"

    print(f"→ Assembling {len(clips)} clips via {mode}...")
    if can_copy:
        concat_stream_copy(clips, args.output)
    else:
        concat_reencode(clips, args.output, fps=args.fps, crf=args.crf)

    write_manifest(clips, args.output, manifest_path, mode)

    print(json.dumps({
        "ok": True,
        "mode": mode,
        "clips": len(clips),
        "output": args.output,
        "manifest": manifest_path,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
