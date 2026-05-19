#!/usr/bin/env python3
"""Apply an edit decision list (EDL) to a video using ffmpeg.

Reads an EDL JSON (list of keep-segments with start_ms/end_ms) and uses ffmpeg
to cut the original MP4 into segments, then concatenate them into the final edit.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile


def apply_edits(mp4_path: str, edl_path: str, output_path: str, temp_dir=None) -> None:
    """Cut video into segments and concatenate."""
    with open(edl_path) as f:
        edl = json.load(f)

    segments = edl["segments"]
    if not segments:
        print("No segments to keep — nothing to output.", file=sys.stderr)
        sys.exit(1)

    print(f"Applying {len(segments)} segments to {mp4_path}")
    print(f"Output: {output_path}")

    # Use ffmpeg filter_complex for precise cutting and joining
    # Build a complex filter that trims and concatenates all segments
    workdir = temp_dir or tempfile.mkdtemp(prefix="video_edit_")
    segment_files = []

    for i, seg in enumerate(segments):
        start_s = seg["start_ms"] / 1000.0
        end_s = seg["end_ms"] / 1000.0
        duration_s = end_s - start_s

        seg_path = os.path.join(workdir, f"seg_{i:04d}.mp4")
        segment_files.append(seg_path)

        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{start_s:.3f}",
            "-i", mp4_path,
            "-t", f"{duration_s:.3f}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-avoid_negative_ts", "make_zero",
            "-movflags", "+faststart",
            seg_path,
        ]

        print(f"  Segment {i + 1}/{len(segments)}: {start_s:.2f}s - {end_s:.2f}s ({duration_s:.2f}s)")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ffmpeg error on segment {i}: {result.stderr[-500:]}", file=sys.stderr)
            sys.exit(1)

    # Write concat file
    concat_path = os.path.join(workdir, "concat.txt")
    with open(concat_path, "w") as f:
        for seg_path in segment_files:
            f.write(f"file '{seg_path}'\n")

    # Concatenate all segments
    print(f"\nConcatenating {len(segment_files)} segments...")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_path,
        "-c", "copy",
        "-movflags", "+faststart",
        output_path,
    ]
    result = subprocess.run(concat_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Concat error: {result.stderr[-500:]}", file=sys.stderr)
        sys.exit(1)

    # Get output file size and duration
    probe_cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration,size",
                 "-of", "json", output_path]
    probe = subprocess.run(probe_cmd, capture_output=True, text=True)
    if probe.returncode == 0:
        info = json.loads(probe.stdout)
        duration = float(info["format"]["duration"])
        size_mb = int(info["format"]["size"]) / (1024 * 1024)
        print(f"\nOutput: {output_path}")
        print(f"Duration: {duration:.1f}s ({duration / 60:.1f}min)")
        print(f"Size: {size_mb:.1f}MB")

    # Cleanup temp segment files
    if not temp_dir:
        for f_path in segment_files:
            os.remove(f_path)
        os.remove(concat_path)
        os.rmdir(workdir)
        print("Temp files cleaned up.")


def main():
    parser = argparse.ArgumentParser(description="Apply EDL cuts to a video")
    parser.add_argument("mp4", help="Path to original MP4 file")
    parser.add_argument("edl", help="Path to EDL JSON file")
    parser.add_argument("-o", "--output", help="Path for output MP4 (default: <basename>_edited.mp4)")
    parser.add_argument("--temp-dir", help="Directory for temp segment files (default: system temp)")
    args = parser.parse_args()

    output_path = args.output or os.path.splitext(args.mp4)[0] + "_edited.mp4"
    apply_edits(args.mp4, args.edl, output_path, args.temp_dir)


if __name__ == "__main__":
    main()
