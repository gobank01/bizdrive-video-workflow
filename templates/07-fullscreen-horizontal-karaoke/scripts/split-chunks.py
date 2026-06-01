#!/usr/bin/env python3
"""V88 T07 chunked workflow — Step A: split source media into N chunks.

For long-form (10-30 min) jobs we run the v88 pipeline **per chunk** so that
a mistake in chunk 03 only re-does chunk 03, not the entire 30-minute cut.

This script slices the job's `input/bottom.mp4` into N time-windowed chunks
under `chunks/<NN>/input/bottom.mp4`, scaffolds each chunk's directory layout,
and writes a master state file `chunks.json` at the job root.

Usage (run from the job workspace):
    python3 scripts/split-chunks.py [--minutes 5] [--source input/bottom.mp4]

Default chunk size is 5 minutes. The final chunk is shorter — never padded.

State file `chunks.json` is the source of truth for chunked work; the
companion `chunk-status.py` CLI updates per-chunk status as you progress.

After splitting, follow `README.md` Section "Chunked workflow" (or
`templates/_shared/docs/V88_PLAYBOOK.md` Step 0c) to process each chunk.
"""
import argparse
import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]        # job workspace
JOB_DIR = WS.parent                              # jobs/<job>/
CHUNKS_DIR = JOB_DIR / "chunks"
STATE = JOB_DIR / "chunks.json"


def ffprobe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def slice_clip(src: Path, dst: Path, start: float, duration: float) -> None:
    """Accurate slice with re-encode (-c copy snaps to keyframes — too coarse
    for editorial). Normalises params (libx264 yuv420p 30 fps + AAC 48k 192k)
    so per-chunk v88 renders concat cleanly with -c copy at merge time."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error",
         "-ss", f"{start:.3f}", "-i", str(src), "-t", f"{duration:.3f}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", "30",
         "-g", "30", "-keyint_min", "30",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-avoid_negative_ts", "make_zero",
         "-movflags", "+faststart", str(dst)],
        check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=5.0,
                    help="chunk size in minutes (default 5)")
    ap.add_argument("--source", default="../input/bottom.mp4",
                    help="source path relative to workspace (default ../input/bottom.mp4)")
    ap.add_argument("--bg", default="../input/bg.png",
                    help="background path relative to workspace (default ../input/bg.png)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite chunks/ + chunks.json if they exist")
    args = ap.parse_args()

    src = (WS / args.source).resolve()
    bg = (WS / args.bg).resolve()
    if not src.exists():
        print(f"✗ source not found: {src}", file=sys.stderr)
        return 1
    if not bg.exists():
        print(f"⚠ bg.png not found: {bg} — chunks will lack a background fallback",
              file=sys.stderr)

    if STATE.exists() and not args.force:
        print(f"✗ chunks.json already exists at {STATE} — pass --force to overwrite",
              file=sys.stderr)
        return 1

    if args.force and CHUNKS_DIR.exists():
        print(f"  → removing existing {CHUNKS_DIR}")
        shutil.rmtree(CHUNKS_DIR)

    total_dur = ffprobe_duration(src)
    chunk_dur = args.minutes * 60.0
    n_chunks = int(total_dur // chunk_dur) + (1 if total_dur % chunk_dur > 0.5 else 0)
    if n_chunks == 0:
        print(f"✗ source duration {total_dur:.2f}s shorter than one chunk", file=sys.stderr)
        return 1

    print(f"→ source: {src.name}  duration={total_dur:.2f}s")
    print(f"→ chunk size: {args.minutes:.1f} min  → {n_chunks} chunks")

    chunks = []
    for i in range(n_chunks):
        cid = f"{i+1:02d}"
        start = i * chunk_dur
        end = min(start + chunk_dur, total_dur)
        dur = end - start
        cdir = CHUNKS_DIR / cid
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "input").mkdir(exist_ok=True)
        (cdir / "intermediates").mkdir(exist_ok=True)
        (cdir / "output").mkdir(exist_ok=True)

        slice_clip(src, cdir / "input" / "bottom.mp4", start, dur)
        if bg.exists():
            (cdir / "input" / "bg.png").write_bytes(bg.read_bytes())

        chunks.append({
            "id": cid,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(dur, 3),
            "status": "sliced",
            "logs": [{"at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "step": "split", "ok": True}],
        })
        print(f"  ✓ chunk {cid}  [{start:7.2f} → {end:7.2f}]  ({dur:6.2f}s)")

    state = {
        "schema": "bizdrive-t07-chunks/1",
        "createdAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "template": "07-fullscreen-horizontal-karaoke",
        "source": str(src.relative_to(JOB_DIR)),
        "sourceDuration": round(total_dur, 3),
        "chunkMinutes": args.minutes,
        "totalChunks": n_chunks,
        "chunks": chunks,
    }
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✓ wrote {STATE.relative_to(JOB_DIR)} — {n_chunks} chunks ready")
    print(f"\nNext: process each chunk with V88 Step 2-13 (see README chunked workflow).")
    print(f"      Track status:  python3 scripts/chunk-status.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
