#!/usr/bin/env python3
"""v88 Step 14 — mix the final audio: polished speech + BGM + context SFX.

Reads the per-job plan at assets/intermediates/sfx-plan.json and writes:
  ../output/finals/no-bgm.mp4   visual + speech only (frame-lock QA reference)
  ../output/finals/final.mp4    visual + speech + BGM + SFX  ⭐ deliverable

v88 SFX rules — ENFORCED here:
  - At most 5 SFX per clip (hard cap).
  - ~1 SFX per 12s of final video; fewer for clips under 60s (warned).
  - SFX starts must be >= 4s apart and inside [0, duration].
  - SFX are context-matched — picked from templates/_shared/sfx/sfx-library.json.

Each SFX is auto-normalised to a target peak (default -5 dBFS) so picks of
different inherent loudness land at a consistent accent level. The whole mix
is summed (amix normalize=0) and passed through alimiter so it never clips.

sfx-plan.json schema:
{
  "duration": 65.313333,
  "visual": "../output/finals/visual.mp4",
  "speech": "assets/intermediates/speech_polished.wav",
  "bgm": "assets/bgm/stock/mixkit/mixkit-480-curiosity.mp3",
  "bgmGainPercent": 6,
  "sfxTargetPeakDb": -5,
  "sfx": [
    { "file": "whoosh-soft", "at": 0.1,  "note": "opening hook" },
    { "file": "ding",        "at": 60.9, "note": "follow-card slide-in" }
  ]
}
Notes:
  - "file" is a bare library name (resolved against assets/sfx/) or a path.
  - per-SFX "targetPeakDb" or "gainDb" override the auto-normalised level.
  - "bgm" may be omitted — then final.mp4 has speech + SFX only.

Usage (run from the job workspace):
    python3 scripts/mix-sfx.py
    python3 scripts/mix-sfx.py --plan assets/intermediates/sfx-plan.json
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # job workspace
MAX_SFX = 5
MIN_SPACING = 4.0
DEFAULT_TARGET_PEAK_DB = -5.0


def die(msg: str):
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(1)


def resolve_sfx(file_ref: str) -> Path:
    """Resolve an SFX reference: a library name (assets/sfx/<name>) or a path."""
    if "/" in file_ref:
        p = Path(file_ref) if file_ref.startswith("/") else (ROOT / file_ref).resolve()
        if p.exists():
            return p
        die(f"SFX file not found: {file_ref}")
    base = ROOT / "assets/sfx"          # symlink → templates/_shared/sfx
    if (base / file_ref).exists():
        return base / file_ref
    for ext in (".mp3", ".wav"):
        if (base / f"{file_ref}{ext}").exists():
            return base / f"{file_ref}{ext}"
    die(f"SFX '{file_ref}' not in assets/sfx/ — see templates/_shared/sfx/sfx-library.json")


def measure_peak_db(path: Path) -> float:
    out = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    m = re.search(r"max_volume:\s*(-?\d+\.?\d*) dB", out)
    return float(m.group(1)) if m else 0.0


def frame_count(path: Path) -> str:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
         "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    return out or "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="assets/intermediates/sfx-plan.json")
    args = ap.parse_args()

    plan_path = ROOT / args.plan
    if not plan_path.exists():
        die(f"plan not found: {args.plan}")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    duration = float(plan["duration"])
    visual = ROOT / plan.get("visual", "../output/finals/visual.mp4")
    speech = ROOT / plan["speech"]
    out_dir = (ROOT / "../output/finals").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    no_bgm = out_dir / "no-bgm.mp4"
    final = out_dir / "final.mp4"
    target_peak = float(plan.get("sfxTargetPeakDb", DEFAULT_TARGET_PEAK_DB))

    for label, p in (("visual", visual), ("speech", speech)):
        if not p.exists():
            die(f"{label} not found: {p}")

    sfx = sorted(plan.get("sfx", []), key=lambda s: float(s["at"]))

    # --- enforce v88 SFX rules ---
    if len(sfx) > MAX_SFX:
        die(f"{len(sfx)} SFX — v88 cap is {MAX_SFX} per clip. Trim the plan.")
    recommended = min(MAX_SFX, max(1, round(duration / 12)))
    if len(sfx) > recommended:
        print(f"  ⚠ {len(sfx)} SFX for a {duration:.0f}s clip — recommended ≤ {recommended} (~1 per 12s)")
    for i, s in enumerate(sfx):
        at = float(s["at"])
        if at < 0 or at > duration - 0.05:
            die(f"SFX '{s['file']}' at {at}s is outside [0, {duration:.2f}]")
        if i > 0 and at - float(sfx[i - 1]["at"]) < MIN_SPACING:
            die(f"SFX at {sfx[i-1]['at']}s and {at}s are < {MIN_SPACING}s apart (clumping)")

    # --- 1. no-bgm.mp4 — speech only ---
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(visual), "-i", str(speech),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
         "-b:a", "192k", "-ar", "48000", "-t", f"{duration:.6f}",
         "-movflags", "+faststart", str(no_bgm)],
        check=True, capture_output=True,
    )

    # --- 2. final.mp4 — speech + BGM + SFX ---
    inputs = ["-i", str(visual), "-i", str(speech)]
    parts = ["[1:a]aformat=sample_rates=48000:channel_layouts=stereo[sp]"]
    mix_labels = ["[sp]"]
    idx = 2

    bgm = plan.get("bgm")
    if bgm:
        bgm_path = ROOT / bgm
        if not bgm_path.exists():
            die(f"bgm not found: {bgm}")
        bgm_gain = float(plan.get("bgmGainPercent", 6)) / 100.0
        inputs += ["-i", str(bgm_path)]
        parts.append(
            f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"atrim=0:{duration:.6f},asetpts=N/SR/TB,volume={bgm_gain:.4f}[bg]"
        )
        mix_labels.append("[bg]")
        idx += 1

    for n, s in enumerate(sfx):
        path = resolve_sfx(s["file"])
        delay_ms = int(round(float(s["at"]) * 1000))
        if "gainDb" in s:
            gain = float(s["gainDb"])
        else:
            tgt = float(s.get("targetPeakDb", target_peak))
            gain = round(tgt - measure_peak_db(path), 2)
        inputs += ["-i", str(path)]
        parts.append(
            f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"volume={gain}dB,adelay={delay_ms}|{delay_ms}[x{n}]"
        )
        mix_labels.append(f"[x{n}]")
        print(f"  SFX {n+1}: {path.name} @ {s['at']}s  gain {gain:+.1f}dB"
              f"  — {s.get('note', '')}")
        idx += 1

    parts.append(
        "".join(mix_labels)
        + f"amix=inputs={len(mix_labels)}:normalize=0:dropout_transition=0:"
        + "duration=longest[mx]"
    )
    parts.append("[mx]alimiter=level_in=1:level_out=1:limit=0.95[aout]")

    subprocess.run(
        ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(parts),
         "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac",
         "-b:a", "192k", "-ar", "48000", "-t", f"{duration:.6f}",
         "-movflags", "+faststart", str(final)],
        check=True, capture_output=True,
    )

    # --- QA ---
    nb_frames, fn_frames = frame_count(no_bgm), frame_count(final)
    loud = subprocess.run(
        ["ffmpeg", "-i", str(final), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    # ebur128 prints "I: <x> LUFS" per frame while streaming; the final
    # integrated value is the LAST occurrence (the summary block).
    loud_matches = re.findall(r"I:\s*(-?\d+\.?\d*) LUFS", loud)
    print(f"\n  ✓ no-bgm.mp4  ({nb_frames} frames)")
    print(f"  ✓ final.mp4   ({fn_frames} frames, {len(sfx)} SFX"
          + (f", BGM {plan.get('bgmGainPercent', 6)}%" if bgm else "") + ")")
    if nb_frames != fn_frames:
        print(f"  ⚠ frame-count mismatch ({nb_frames} vs {fn_frames})")
    if loud_matches:
        print(f"  ✓ integrated loudness: {loud_matches[-1]} LUFS  (v88 target -16, range -18..-14)")


if __name__ == "__main__":
    main()
