#!/usr/bin/env python3
"""De-prompter — remove an off-camera prompter's voice from "repeat-after" footage.

Shooting style: an off-camera person reads each line out loud (prompter), their
voice bleeds into the camera mic, then the on-camera talent repeats the line.
Raw audio = prompter + talent alternating. This tool keeps ONLY the talent and
emits a v88 keep-EDL (`{"segments":[{"start_ms","end_ms"}]}`) you can feed to
`templates/_shared/scripts/clean-cut/apply_edits.py`, or apply directly with
ffmpeg via `--apply`.

How it decides who the talent is (gender-agnostic, no hard-coded "male"):
  1. ElevenLabs Scribe v2 with diarize=true, num_speakers=N -> per-word speaker_id
  2. The talent is the speaker who, across adjacent A->B pairs, speaks SECOND
     (the repeater) most often AND holds the most total airtime.
  3. Confidence guard: if only ONE speaker is detected but the transcript has
     consecutive near-duplicate phrases (the tell-tale of repeat-after), the two
     voices were probably too similar to split (e.g. two same-gender voices) ->
     the tool refuses to guess and tells you to use a voice reference or lip-sync.

Stdlib only (mirrors transcribe.py). Needs ELEVENLABS_API_KEY in env.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, List, Dict


# ---------- audio + http helpers (same approach as transcribe.py) ----------

def extract_audio_mp3(video_path: str, out_path: str) -> None:
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-y", "-i", video_path, "-vn",
         "-ac", "1", "-ar", "44100", "-b:a", "128k", out_path],
        capture_output=True, check=True,
    )


def probe_duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def multipart_post(url: str, headers: Dict[str, str], fields: Dict[str, str],
                   file_path: str, file_field: str = "file") -> bytes:
    boundary = "----DePromptBoundary" + os.urandom(8).hex()
    body = bytearray()
    for k, v in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        body.extend(f"{v}\r\n".encode())
    fname = os.path.basename(file_path)
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="{file_field}"; filename="{fname}"\r\n'.encode())
    body.extend(b"Content-Type: audio/mpeg\r\n\r\n")
    with open(file_path, "rb") as f:
        body.extend(f.read())
    body.extend(f"\r\n--{boundary}--\r\n".encode())
    req_headers = dict(headers)
    req_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(url, data=bytes(body), headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}") from e


def diarize(audio_path: str, lang: str, num_speakers: int) -> Dict:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set (source templates/_shared/env/.env)")
    iso3 = {"th": "tha", "en": "eng"}.get(lang, lang)
    fields = {
        "model_id": "scribe_v2",
        "timestamps_granularity": "word",
        "diarize": "true",
        "num_speakers": str(num_speakers),
        "language_code": iso3,
    }
    raw = multipart_post(
        "https://api.elevenlabs.io/v1/speech-to-text",
        {"xi-api-key": api_key}, fields, audio_path,
    )
    return json.loads(raw)


# ---------- analysis ----------

def speaker_runs(words: List[Dict]) -> List[Dict]:
    """Collapse consecutive same-speaker words into runs with text + timing."""
    runs: List[Dict] = []
    for w in words:
        if w.get("type") != "word":
            continue
        s = w.get("speaker_id", "speaker_0")
        if not runs or runs[-1]["spk"] != s:
            runs.append({"spk": s, "start": w["start"], "end": w["end"], "text": w["text"]})
        else:
            runs[-1]["end"] = w["end"]
            runs[-1]["text"] += w["text"]
    return runs


def _norm(s: str) -> str:
    return "".join(ch for ch in s if not ch.isspace())


def phrase_split(words: List[Dict], gap: float = 0.35) -> List[Dict]:
    """Split words into phrases on speech gaps (speaker-independent).

    The repeat-after tell ("line ... pause ... same line") survives even when the
    diarizer merged both voices into one speaker, because the PAUSE is still there.
    """
    phrases: List[Dict] = []
    for w in words:
        if w.get("type") != "word":
            continue
        if phrases and w["start"] - phrases[-1]["end"] <= gap:
            phrases[-1]["end"] = w["end"]
            phrases[-1]["text"] += w["text"]
        else:
            phrases.append({"start": w["start"], "end": w["end"], "text": w["text"]})
    return phrases


def has_consecutive_duplicates(words: List[Dict]) -> int:
    """Count adjacent PHRASES whose text is a near-duplicate (repeat-after tell).

    Works on pause-split phrases, not speaker runs, so it still fires when the
    diarizer collapsed two similar voices into a single speaker.
    """
    phrases = phrase_split(words)
    dups = 0
    for i in range(1, len(phrases)):
        a, b = _norm(phrases[i - 1]["text"]), _norm(phrases[i]["text"])
        if not a or not b:
            continue
        shorter = min(len(a), len(b))
        same = sum(1 for x, y in zip(a, b) if x == y)  # Thai has no spaces; compare prefixes
        if shorter >= 3 and same / shorter >= 0.6:
            dups += 1
    return dups


def pick_talent(runs: List[Dict]) -> str:
    from collections import Counter
    airtime: Counter = Counter()
    second: Counter = Counter()
    for r in runs:
        airtime[r["spk"]] += r["end"] - r["start"]
    for i in range(1, len(runs)):
        second[runs[i]["spk"]] += 1
    # talent = repeats second most often; tie-break on airtime
    return max(airtime, key=lambda k: (second[k], airtime[k]))


def build_edl(runs: List[Dict], talent: str, dur: float,
              pad_l: float, pad_r: float) -> List[Dict]:
    keep = [r for r in runs if r["spk"] == talent]
    others = [r for r in runs if r["spk"] != talent]
    segs = []
    for k in keep:
        a = max(0.0, k["start"] - pad_l)
        b = min(dur, k["end"] + pad_r)
        for r in others:  # never let padding bleed into a prompter run
            if r["end"] <= k["start"] and r["end"] > a:
                a = r["end"] + 0.02
            if r["start"] >= k["end"] and r["start"] < b:
                b = r["start"] - 0.02
        if b - a > 0.05:
            segs.append({"start_ms": int(round(a * 1000)), "end_ms": int(round(b * 1000))})
    return segs


def apply_ffmpeg(video: str, segs: List[Dict], out: str,
                 xfade: float = 0.0, transition: str = "fade",
                 punch: float = 0.0, w: int = 720, h: int = 1280) -> None:
    """Cut to talent-only segments. DEFAULT = HARD CUT.

    Why hard cut: repeat-after takes differ a lot in pose (eyes/hands/head), and a
    dissolve is an ALPHA BLEND — it renders both poses at once = a ghost/double
    image ("ลายตา"). Smoothing is mathematically impossible across mismatched
    poses (longer fade = more ghost). Pros make the cut INTENTIONAL instead:

      - hard cut + continuous audio  (default here)
      - punch>0: alternating digital punch-in ("fake second camera") so each join
        reads as a deliberate angle change (30-degree rule), not a jump. Baked
        upstream here on purpose — do NOT scale the face layer inside HyperFrames
        T01/T05 (AGENTS.md motion-safety forbids it; `npm run check:motion` fails).
      - cover the biggest-delta joins with B-roll/caption downstream in v88.

    Audio: each segment gets a 15 ms in/out fade to de-click the butt-joins. These
    fades do NOT overlap, so audio length == video length (stays in sync) — unlike
    a crossfade, which shortens. xfade>0 re-enables the (discouraged) video blend.
    """
    n = len(segs)
    durs = [(s["end_ms"] - s["start_ms"]) / 1000.0 for s in segs]
    chains: List[str] = []
    for i, s in enumerate(segs):
        a, b = s["start_ms"] / 1000.0, s["end_ms"] / 1000.0
        vf = "setpts=PTS-STARTPTS"
        if punch > 0 and i % 2 == 1:  # alternate wide / punched-in
            sc = 1.0 + punch
            vf += f",scale=trunc({w}*{sc}/2)*2:trunc({h}*{sc}/2)*2,crop={w}:{h}"
        vf += ",fps=60,format=yuv420p"
        chains.append(f"[0:v]trim=start={a}:end={b},{vf}[v{i}]")
        fo = max(0.0, durs[i] - 0.015)
        chains.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,"
                      f"afade=t=in:st=0:d=0.015,afade=t=out:st={fo:.3f}:d=0.015[a{i}]")

    D = min(xfade, 0.9 * min(durs)) if (n >= 2 and xfade > 0) else 0.0
    if n < 2 or D <= 0.02:  # HARD cut (default): video concat + length-preserving audio
        concat = "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
        fc = ";".join(chains) + ";" + concat
    else:  # legacy crossfade — discouraged for large pose deltas (ghosting)
        prev, acc = "v0", durs[0]
        for i in range(1, n):
            offset = acc - D
            label = "[v]" if i == n - 1 else f"[vx{i}]"
            chains.append(f"[{prev}][v{i}]xfade=transition={transition}:duration={D}:offset={offset:.3f}{label}")
            acc += durs[i] - D
            prev = label.strip("[]")
        aprev = "a0"
        for i in range(1, n):
            label = "[a]" if i == n - 1 else f"[ax{i}]"
            chains.append(f"[{aprev}][a{i}]acrossfade=d={D}:c1=tri:c2=tri{label}")
            aprev = label.strip("[]")
        fc = ";".join(chains)

    subprocess.run(
        ["ffmpeg", "-hide_banner", "-y", "-i", video, "-filter_complex", fc,
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "18", "-c:a", "aac", "-b:a", "160k", out],
        check=True,
    )


# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser(description="Remove off-camera prompter voice from repeat-after footage.")
    ap.add_argument("video")
    ap.add_argument("--lang", default="tha")
    ap.add_argument("--num-speakers", type=int, default=2)
    ap.add_argument("--pad-l", type=float, default=0.12)
    ap.add_argument("--pad-r", type=float, default=0.20)
    ap.add_argument("--talent", default=None, help="force a speaker_id instead of auto-pick")
    ap.add_argument("--out-edl", default=None, help="write keep-EDL JSON here (v88 format)")
    ap.add_argument("--report", default=None, help="write a human-readable diarization report here")
    ap.add_argument("--apply", default=None, help="also render a talent-only mp4 to this path")
    ap.add_argument("--xfade", type=float, default=0.0,
                    help="video crossfade seconds (DISCOURAGED: ghosts on large pose deltas). default 0 = hard cut")
    ap.add_argument("--punch", type=float, default=0.0,
                    help="alternating punch-in amount, e.g. 0.12 = 12%% zoom on every other take "
                         "(makes hard joins read as a deliberate angle change). default 0 = off")
    ap.add_argument("--transition", default="fade",
                    help="xfade transition type when --xfade>0 (fadeblack avoids ghosting). default fade")
    ap.add_argument("--diar-json", default=None, help="reuse a cached diarization JSON instead of calling the API")
    ap.add_argument("--save-diar", default=None, help="write the raw diarization JSON here (for caching re-runs)")
    args = ap.parse_args()

    video = str(Path(args.video).expanduser())
    dur = probe_duration(video)
    work = Path(args.out_edl or "/tmp/deprompter_edl.json").parent
    work.mkdir(parents=True, exist_ok=True)

    if args.diar_json:
        data = json.load(open(args.diar_json))
    else:
        mp3 = str(work / "_deprompter_audio.mp3")
        extract_audio_mp3(video, mp3)
        data = diarize(mp3, args.lang, args.num_speakers)
        if args.save_diar:
            json.dump(data, open(args.save_diar, "w"), ensure_ascii=False)

    words = [w for w in data.get("words", []) if w.get("type") == "word"]
    runs = speaker_runs(words)
    speakers = sorted({r["spk"] for r in runs})
    dups = has_consecutive_duplicates(words)

    report = {
        "duration_s": round(dur, 2),
        "speakers_detected": speakers,
        "consecutive_duplicate_phrases": dups,
        "full_text": data.get("text", ""),
        "runs": [{"spk": r["spk"], "start": round(r["start"], 2),
                  "end": round(r["end"], 2), "text": r["text"]} for r in runs],
    }

    # Confidence guard ------------------------------------------------------
    if len(speakers) < 2:
        report["status"] = "AMBIGUOUS"
        if dups >= 2:
            report["warning"] = (
                "Only 1 speaker detected, but the transcript has repeated phrases "
                f"({dups}). The two voices were likely too similar to split "
                "(e.g. same gender). Do NOT auto-cut. Options: (a) provide a clean "
                "5-10s voice reference of the talent and use voice-fingerprint "
                "matching, or (b) use lip-sync (active-speaker) detection, or "
                "(c) cut by hand. See tools/deprompter/README.md."
            )
        else:
            report["warning"] = (
                "Only 1 speaker detected and no repeat pattern -> probably already "
                "clean (no prompter bleed). Safe to skip de-prompting."
            )
        _emit(args, report, None)
        print(json.dumps({k: report[k] for k in ("status", "warning", "speakers_detected")},
                         ensure_ascii=False, indent=2))
        return 0 if dups < 2 else 2

    talent = args.talent or pick_talent(runs)
    segs = build_edl(runs, talent, dur, args.pad_l, args.pad_r)
    kept = sum((s["end_ms"] - s["start_ms"]) for s in segs) / 1000.0
    report["status"] = "OK"
    report["talent_speaker"] = talent
    report["kept_s"] = round(kept, 2)
    report["dropped_s"] = round(dur - kept, 2)
    report["segments"] = segs
    if args.apply:
        report["join_style"] = ("hard-cut" if args.xfade <= 0 else f"xfade {args.xfade}s")
        report["punch"] = args.punch
        report["rendered"] = args.apply

    _emit(args, report, segs)

    if args.apply:
        apply_ffmpeg(video, segs, str(Path(args.apply).expanduser()),
                     xfade=args.xfade, transition=args.transition, punch=args.punch)

    print(json.dumps({"status": "OK", "talent_speaker": talent,
                      "kept_s": report["kept_s"], "dropped_s": report["dropped_s"],
                      "segments": len(segs)}, ensure_ascii=False, indent=2))
    return 0


def _emit(args, report, segs):
    if args.out_edl and segs is not None:
        json.dump({"segments": segs}, open(args.out_edl, "w"), ensure_ascii=False, indent=2)
    if args.report:
        json.dump(report, open(args.report, "w"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    sys.exit(main())
