#!/usr/bin/env python3
"""Transcribe audio/video files via OpenAI Whisper, Grok (xAI), or ElevenLabs Scribe.

Outputs raw JSON with normalized shape so the calling agent can post-process.
The calling agent is responsible for spelling fixes, segmentation, and topic
inference — this script only handles the API call and output normalization.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, List, Dict

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
MAX_OPENAI_SIZE = 25 * 1024 * 1024
MAX_GROK_SIZE = 25 * 1024 * 1024
MAX_ELEVEN_SIZE = 1024 * 1024 * 1024  # 1GB practical limit
CHUNK_DURATION = 600


# ---------- ffmpeg helpers ----------

def count_audio_tracks(file_path: str) -> int:
    result = subprocess.run(
        ["ffprobe", "-i", file_path, "-show_streams", "-select_streams", "a"],
        capture_output=True, text=True,
    )
    return result.stdout.count("codec_type=audio")


def extract_audio(video_path: str, output_path: str) -> None:
    """Extract a 16k mono wav suitable for any STT provider."""
    tracks = count_audio_tracks(video_path)
    if tracks > 1:
        filter_str = "".join(f"[0:a:{i}]" for i in range(tracks))
        filter_str += f"amix=inputs={tracks}:duration=longest"
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-filter_complex", filter_str,
             "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
             "-y", output_path],
            capture_output=True, check=True,
        )
    else:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000",
             "-c:a", "pcm_s16le", "-y", output_path],
            capture_output=True, check=True,
        )


def get_duration(file_path: str) -> float:
    result = subprocess.run(
        ["ffmpeg", "-i", file_path, "-f", "null", "-"],
        capture_output=True, text=True,
    )
    for line in result.stderr.split("\n"):
        if "Duration:" in line:
            time_str = line.split("Duration:")[1].split(",")[0].strip()
            parts = time_str.split(":")
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return 0.0


# ---------- multipart helper (no external deps) ----------

def multipart_post(url: str, headers: Dict[str, str], fields: Dict[str, str], file_path: str, file_field: str = "file") -> bytes:
    """POST multipart/form-data without requests/form-data. Stdlib only."""
    boundary = "----HFBoundary" + os.urandom(8).hex()
    body = bytearray()
    for k, v in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        body.extend(f"{v}\r\n".encode())
    fname = os.path.basename(file_path)
    ext = os.path.splitext(fname)[1].lower()
    mime = {".wav": "audio/wav", ".mp3": "audio/mpeg", ".m4a": "audio/mp4",
            ".webm": "audio/webm", ".flac": "audio/flac", ".ogg": "audio/ogg"}.get(ext, "application/octet-stream")
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="{file_field}"; filename="{fname}"\r\n'.encode())
    body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
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
        msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {msg}") from e


# ---------- providers ----------

def transcribe_openai(audio_path: str, lang: Optional[str], prompt: Optional[str]) -> Dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    fields = {"model": "whisper-1", "response_format": "verbose_json",
              "timestamp_granularities[]": "word"}
    if lang:
        fields["language"] = lang
    if prompt:
        fields["prompt"] = prompt
    raw = multipart_post(
        "https://api.openai.com/v1/audio/transcriptions",
        {"Authorization": f"Bearer {api_key}"},
        fields, audio_path,
    )
    data = json.loads(raw)
    words = []
    for w in data.get("words", []):
        words.append({"text": w.get("word", ""),
                      "start": float(w.get("start", 0)),
                      "end": float(w.get("end", 0))})
    return {
        "provider": "openai",
        "language": data.get("language"),
        "duration": data.get("duration"),
        "text": data.get("text", ""),
        "words": words,
    }


def transcribe_grok(audio_path: str, lang: Optional[str]) -> Dict:
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        raise RuntimeError("XAI_API_KEY not set")
    fields = {"format": "true"}
    if lang:
        fields["language"] = lang
    raw = multipart_post(
        "https://api.x.ai/v1/stt",
        {"Authorization": f"Bearer {api_key}"},
        fields, audio_path,
    )
    data = json.loads(raw)
    words = []
    # Grok returns word-level timing as `words` with text+start+end (phrase granularity).
    for w in data.get("words", []) or []:
        words.append({"text": w.get("text", ""),
                      "start": float(w.get("start", 0)),
                      "end": float(w.get("end", 0))})
    return {
        "provider": "grok",
        "language": data.get("language"),
        "duration": data.get("duration"),
        "text": data.get("text", ""),
        "words": words,
    }


def transcribe_elevenlabs(audio_path: str, lang: Optional[str]) -> Dict:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set")
    # ElevenLabs uses ISO 639-3 codes (tha, eng, jpn). Map common 2-letter inputs.
    iso3 = {"th": "tha", "en": "eng", "ja": "jpn", "zh": "zho", "ko": "kor",
            "es": "spa", "fr": "fra", "de": "deu", "id": "ind", "vi": "vie"}.get(lang, lang)
    fields = {"model_id": "scribe_v2", "timestamps_granularity": "word"}
    if iso3:
        fields["language_code"] = iso3
    raw = multipart_post(
        "https://api.elevenlabs.io/v1/speech-to-text",
        {"xi-api-key": api_key},
        fields, audio_path,
    )
    data = json.loads(raw)
    # ElevenLabs returns per-character "words" entries. Merge runs of word/spacing
    # into actual whitespace-delimited tokens so the agent gets phrase-level timing.
    raw_words = data.get("words", []) or []
    merged: List[Dict] = []
    cur_text = ""
    cur_start: Optional[float] = None
    cur_end: float = 0.0
    for w in raw_words:
        wtype = w.get("type", "word")
        text = w.get("text", "")
        start = float(w.get("start", 0))
        end = float(w.get("end", start))
        if wtype == "spacing" or text.isspace():
            if cur_text:
                merged.append({"text": cur_text, "start": cur_start or 0, "end": cur_end})
                cur_text = ""
                cur_start = None
                cur_end = 0.0
            continue
        if cur_start is None:
            cur_start = start
        cur_text += text
        cur_end = end
    if cur_text:
        merged.append({"text": cur_text, "start": cur_start or 0, "end": cur_end})
    return {
        "provider": "elevenlabs",
        "language": data.get("language_code"),
        "duration": None,
        "text": data.get("text", ""),
        "words": merged,
    }


PROVIDERS = {
    "openai": transcribe_openai,
    "grok": transcribe_grok,
    "elevenlabs": transcribe_elevenlabs,
}


def auto_provider() -> str:
    """Pick best available provider in order: grok > elevenlabs > openai."""
    for p in ("grok", "elevenlabs", "openai"):
        env = {"grok": "XAI_API_KEY", "elevenlabs": "ELEVENLABS_API_KEY",
               "openai": "OPENAI_API_KEY"}[p]
        if os.environ.get(env):
            return p
    raise RuntimeError("No STT provider env keys set (XAI_API_KEY / ELEVENLABS_API_KEY / OPENAI_API_KEY)")


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio/video to JSON.")
    parser.add_argument("file", help="Audio or video file path")
    parser.add_argument("--provider", choices=["openai", "grok", "elevenlabs", "auto"],
                        default="auto",
                        help="STT provider. auto = grok > elevenlabs > openai by env keys")
    parser.add_argument("--lang", help="Language hint (e.g. th, en). Provider-specific code mapping handled internally.")
    parser.add_argument("--prompt", help="Optional vocabulary/context prompt (OpenAI only)")
    parser.add_argument("--output", help="Output JSON path. Default: <input>.transcript.json next to input")
    parser.add_argument("--save-all", metavar="DIR",
                        help="Save raw + captions + words.json to a directory (3-output mode for CapCut workflow). "
                             "raw-elevenlabs.json kept for re-segmentation. captions.json is phrase-level. "
                             "words.json is nlpo3-segmented (needs --words-per-group N).")
    parser.add_argument("--words-per-group", type=int, default=2,
                        help="With --save-all: words per caption group for words.json (default 2)")
    args = parser.parse_args()

    file_path = os.path.expanduser(args.file)
    if not os.path.exists(file_path):
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    provider = args.provider if args.provider != "auto" else auto_provider()
    fn = PROVIDERS[provider]

    with tempfile.TemporaryDirectory() as tmp:
        ext = Path(file_path).suffix.lower()
        if ext in VIDEO_EXTENSIONS:
            audio_path = os.path.join(tmp, "audio.wav")
            extract_audio(file_path, audio_path)
        else:
            audio_path = file_path

        size = os.path.getsize(audio_path)
        # Most sources we hit are <25MB after wav-16k. If bigger, agent should
        # split first — keep this script simple.
        if size > MAX_ELEVEN_SIZE:
            print(f"Error: audio is {size/1024/1024:.0f}MB; split with ffmpeg first", file=sys.stderr)
            sys.exit(1)
        if provider in ("openai", "grok") and size > MAX_OPENAI_SIZE:
            print(f"Error: {provider} caps at 25MB. Re-encode or chunk before retry.", file=sys.stderr)
            sys.exit(1)

        if args.prompt and provider != "openai":
            print(f"Note: --prompt is ignored for provider={provider} (OpenAI-only).", file=sys.stderr)

        result = fn(audio_path, args.lang) if provider != "openai" \
            else fn(audio_path, args.lang, args.prompt)

    # Pin language from --lang if provided. Otherwise providers may auto-detect
    # per-segment and the last segment's detection wins, which is misleading.
    if args.lang:
        result["language"] = args.lang

    if args.save_all:
        # 3-output mode: raw + captions + words.json
        save_dir = Path(os.path.expanduser(args.save_all))
        save_dir.mkdir(parents=True, exist_ok=True)
        raw_path = save_dir / "raw-elevenlabs.json"
        captions_path = save_dir / "captions.json"
        words_path = save_dir / "words.json"
        meta_path = save_dir / "meta.json"

        # raw — what API returned (or what our normalize layer gave; for true char-level call API direct)
        with open(raw_path, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        # captions — phrase-level (same as normalized result for now; agent runs post-process #1 on it)
        with open(captions_path, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        # words.json: nlpo3 segment if provider is elevenlabs (it has char-level we can re-segment).
        # For other providers, skip — they don't have char-level.
        words_data = None
        if result.get("provider") == "elevenlabs":
            # word_segment.py expects raw ElevenLabs response. Call it.
            seg_script = Path(__file__).parent / "word_segment.py"
            tmp_words = save_dir / f"_seg_tmp.json"
            r = subprocess.run([
                sys.executable, str(seg_script), str(raw_path),
                "-o", str(words_path),
                "--engine", "nlpo3",
                "--words-per-group", str(args.words_per_group),
            ], capture_output=True, text=True)
            if r.returncode == 0:
                words_data = {"output": str(words_path), "words_per_group": args.words_per_group}
            else:
                words_data = {"error": "word_segment failed", "stderr": r.stderr[:200]}

        meta = {
            "skill": "bizdrive-transcribe", "version": "v1",
            "source_file": file_path, "provider": result["provider"],
            "language": result.get("language"),
            "words_per_group": args.words_per_group,
            "ran_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with open(meta_path, "w") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        summary = {
            "ok": True,
            "provider": result["provider"],
            "language": result.get("language"),
            "wordCount": len(result.get("words", [])),
            "outputs": {
                "raw": str(raw_path),
                "captions": str(captions_path),
                "words": str(words_path) if words_data and "output" in words_data else None,
                "meta": str(meta_path),
            },
            "words_per_group": args.words_per_group,
            "words_status": words_data,
            "note": "captions.json needs post-process #1 (text fix). words.json needs post-process #2 (boundary fix). See bizdrive-transcribe/references/post-process-protocol.md and bizdrive-capcut/references/post-process-protocol-v2.md.",
        }
        print(json.dumps(summary, ensure_ascii=False))
        return

    out_path = args.output or str(Path(file_path).with_suffix("")) + ".transcript.json"
    with open(out_path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    summary = {
        "ok": True,
        "provider": result["provider"],
        "language": result.get("language"),
        "wordCount": len(result.get("words", [])),
        "transcriptPath": out_path,
    }
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
