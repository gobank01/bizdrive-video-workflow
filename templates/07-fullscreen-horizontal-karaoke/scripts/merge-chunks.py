#!/usr/bin/env python3
"""V88 T07 chunked workflow — Step Z: merge rendered chunks + finalise.

Reads `chunks.json` and concatenates every rendered chunk into a single MP4,
then runs the soft lint, mixes BGM/SFX (Step 14), and prepends the thumbnail
poster frame (Step 16). The deliverable lands at:

    <job>/output/finals/<clip>.mp4

Prerequisites (verified before doing anything):
  - chunks.json exists at <job>/chunks.json
  - every chunk has status == "rendered"
  - every chunk has output/chunk.mp4 on disk
  - codec params match across chunks (we re-encode if they don't)

Usage (run from the job workspace):
    python3 scripts/merge-chunks.py                     # default: speech-only mux
    python3 scripts/merge-chunks.py --skip-thumbnail    # no Step 16
    python3 scripts/merge-chunks.py --skip-lint         # no soft lint pass
    python3 scripts/merge-chunks.py --no-bgm            # no BGM/SFX (visual + speech only)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
JOB_DIR = WS.parent
STATE = JOB_DIR / "chunks.json"
FINALS = (JOB_DIR / "output/finals").resolve()


def fail(msg: str) -> None:
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(1)


def load_state() -> dict:
    if not STATE.exists():
        fail(f"no chunks.json at {STATE}")
    return json.loads(STATE.read_text(encoding="utf-8"))


def verify(state: dict) -> list[Path]:
    paths: list[Path] = []
    bad: list[str] = []
    for c in state["chunks"]:
        cdir = JOB_DIR / "chunks" / c["id"]
        clip = cdir / "output" / "chunk.mp4"
        if c["status"] != "rendered":
            bad.append(f"chunk {c['id']} status={c['status']!r} (want 'rendered')")
        elif not clip.exists():
            bad.append(f"chunk {c['id']} missing {clip}")
        else:
            paths.append(clip)
    if bad:
        print("✗ not ready to merge:", file=sys.stderr)
        for b in bad:
            print(f"    {b}", file=sys.stderr)
        sys.exit(1)
    return paths


def concat_chunks(paths: list[Path], out: Path) -> None:
    """Concat with -c copy if codec params match, otherwise re-encode."""
    # Probe first chunk's params; if any other differs, fall back to re-encode.
    def probe(p: Path) -> tuple[str, int, int, str, int]:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=codec_name,width,height,pix_fmt,r_frame_rate",
             "-of", "csv=p=0", str(p)],
            capture_output=True, text=True, check=True).stdout.strip()
        codec, w, h, pix, fr = r.split(",")
        return codec, int(w), int(h), pix, fr

    first = probe(paths[0])
    uniform = all(probe(p) == first for p in paths[1:])

    list_file = out.parent / "_concat-list.txt"
    list_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in paths) + "\n", encoding="utf-8")

    if uniform:
        print("  → codec params match, using -c copy concat (fast, lossless)")
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
             "-i", str(list_file), "-c", "copy",
             "-movflags", "+faststart", str(out)],
            check=True)
    else:
        print("  ⚠ codec params differ — re-encoding (slower)")
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
             "-i", str(list_file),
             "-c:v", "libx264", "-preset", "fast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "30", "-g", "30", "-keyint_min", "30",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
             "-movflags", "+faststart", str(out)],
            check=True)
    list_file.unlink()


def soft_lint() -> None:
    """Best-effort hyperframes lint on the job workspace."""
    print("  → soft lint (npm run check) — failures will not block merge")
    try:
        subprocess.run(["npm", "run", "check"], cwd=str(WS), check=False)
    except FileNotFoundError:
        print("  ⚠ npm not on PATH — skipped")


def maybe_run_thumbnail() -> Path | None:
    """If thumbnail/thumbnail.json exists from a prior build, re-run.
       Otherwise return None (caller should call build-thumbnail.py manually)."""
    plan = WS / "thumbnail" / "thumbnail.json"
    if not plan.exists():
        return None
    try:
        cfg = json.loads(plan.read_text(encoding="utf-8"))
        args = ["python3", str(WS / "scripts" / "build-thumbnail.py"),
                cfg["main"], cfg["hero"], cfg["sub"]]
        subprocess.run(args, cwd=str(WS), check=True)
        clip = cfg.get("clip")
        return FINALS / f"{clip}.mp4" if clip else None
    except Exception as e:
        print(f"  ⚠ thumbnail re-build failed: {e}", file=sys.stderr)
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-thumbnail", action="store_true")
    ap.add_argument("--skip-lint", action="store_true")
    ap.add_argument("--no-bgm", action="store_true",
                    help="skip Step 14 BGM/SFX mix — output is concatenated visual + speech only")
    args = ap.parse_args()

    state = load_state()
    paths = verify(state)
    print(f"→ merging {len(paths)} chunks ({state['sourceDuration']:.1f}s source)")

    FINALS.mkdir(parents=True, exist_ok=True)
    merged = FINALS / "visual.mp4"
    concat_chunks(paths, merged)
    print(f"  ✓ concatenated → {merged.relative_to(JOB_DIR)}")

    if not args.no_bgm:
        plan = WS / "assets" / "intermediates" / "sfx-plan.json"
        if plan.exists():
            print("  → running mix-sfx.py (Step 14)")
            subprocess.run(
                ["python3", str(WS / "scripts" / "mix-sfx.py")],
                cwd=str(WS), check=True)
        else:
            print(f"  ⚠ no {plan.relative_to(WS)} — skipping BGM/SFX mix "
                  f"(write a plan referencing visual.mp4 + the merged speech wav, then re-run)")

    if not args.skip_lint:
        soft_lint()

    if not args.skip_thumbnail:
        thumb_out = maybe_run_thumbnail()
        if thumb_out is None:
            print("  ⚠ no thumbnail/thumbnail.json — call build-thumbnail.py manually "
                  "with <main> <hero> <sub> to prepend the poster frame")
        else:
            print(f"  ✓ thumbnail prepended → {thumb_out.name}")

    print("\n✓ merge complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
