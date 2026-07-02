#!/usr/bin/env python3
"""tts-thai.py — ElevenLabs Thai narration TTS for the serial drama.

The narrator voice IS the series' face: voice_id is pinned in bible/voice.json
and must never change mid-season. Archive every episode's WAV + the settings
JSON (done automatically below) in case the voice is ever removed from the
ElevenLabs library.

Usage:
  python3 tts-thai.py --list-voices [--search TEXT]     # own library + Thai shared library
  python3 tts-thai.py --add-voice OWNER_ID VOICE_ID NAME  # copy a shared voice into the library
  python3 tts-thai.py --sample VOICE_ID "ข้อความ" -o sample.mp3
  python3 tts-thai.py vo-script.txt -o vo_raw.wav [--voice VOICE_ID]

Requires ELEVENLABS_API_KEY (templates/_shared/env/.env). Stdlib-only HTTP,
same pattern as templates/_shared/scripts/transcribe/transcribe.py.
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# macOS framework python lacks system certs (same fix as inbox-sync / transcribe:el)
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
except ImportError:
    pass

API_BASE = "https://api.elevenlabs.io"
HERE = Path(__file__).resolve().parent
VOICE_FILE = HERE / "bible" / "voice.json"

# eleven_v3 is the ONLY model on this account that supports Thai (checked via
# /v1/models 2026-06-11). v3 stability accepts 0.0 creative / 0.5 natural / 1.0 robust.
DEFAULT_MODEL = "eleven_v3"
DEFAULT_SETTINGS = {"stability": 0.5}


def api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("ELEVENLABS_API_KEY is missing. Source templates/_shared/env/.env first.")
    return key


def request(method: str, path: str, payload=None, query=None) -> bytes:
    url = f"{API_BASE}{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"xi-api-key": api_key(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs {method} {path} failed: {e.code} {e.read().decode(errors='replace')[:500]}")


def list_voices(search: str | None) -> None:
    own = json.loads(request("GET", "/v1/voices"))
    print("=== OWN LIBRARY ===")
    for v in own.get("voices", []):
        labels = v.get("labels") or {}
        print(f"{v['voice_id']}  {v['name']}  [{labels.get('gender','?')}/{labels.get('age','?')}/{labels.get('language', labels.get('accent','?'))}]")

    query = {"page_size": "20", "language": "th", "gender": "male"}
    if search:
        query["search"] = search
    shared = json.loads(request("GET", "/v1/shared-voices", query=query))
    print("\n=== SHARED LIBRARY (Thai, male) ===")
    for v in shared.get("voices", []):
        print(json.dumps({
            "voice_id": v.get("voice_id"),
            "public_owner_id": v.get("public_owner_id"),
            "name": v.get("name"),
            "age": v.get("age"),
            "accent": v.get("accent"),
            "descriptive": v.get("descriptive"),
            "use_case": v.get("use_case"),
            "cloned_by_count": v.get("cloned_by_count"),
            "preview_url": v.get("preview_url"),
        }, ensure_ascii=False))


def add_voice(owner_id: str, voice_id: str, name: str) -> None:
    body = json.loads(request("POST", f"/v1/voices/add/{owner_id}/{voice_id}", payload={"new_name": name}))
    print(json.dumps(body, ensure_ascii=False))


def design_previews(description: str, text: str, out_dir: Path) -> None:
    """Voice Design: generate candidate voices from a description, save previews
    as mp3 + a previews.json with generated_voice_ids for --create-from-preview."""
    payload = {"voice_description": description, "text": text, "model_id": "eleven_ttv_v3"}
    try:
        body = json.loads(request("POST", "/v1/text-to-voice/create-previews", payload=payload))
    except SystemExit:
        payload.pop("model_id")
        body = json.loads(request("POST", "/v1/text-to-voice/create-previews", payload=payload))
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for i, p in enumerate(body.get("previews", []), 1):
        mp3 = out_dir / f"preview-{i}.mp3"
        mp3.write_bytes(base64.b64decode(p["audio_base_64"]))
        index.append({"file": mp3.name, "generated_voice_id": p["generated_voice_id"]})
        print(f"saved {mp3}  generated_voice_id={p['generated_voice_id']}")
    (out_dir / "previews.json").write_text(json.dumps(
        {"description": description, "text": text, "previews": index}, ensure_ascii=False, indent=2))


def create_from_preview(generated_voice_id: str, name: str, description: str) -> None:
    body = json.loads(request("POST", "/v1/text-to-voice/create-voice-from-preview", payload={
        "voice_name": name,
        "voice_description": description,
        "generated_voice_id": generated_voice_id,
    }))
    print(json.dumps({"voice_id": body.get("voice_id"), "name": body.get("name")}, ensure_ascii=False))


def tts(voice_id: str, text: str, output: Path, settings=None) -> None:
    payload = {
        "text": text,
        "model_id": DEFAULT_MODEL,
        "voice_settings": settings or DEFAULT_SETTINGS,
    }
    audio = request("POST", f"/v1/text-to-speech/{voice_id}", payload=payload,
                    query={"output_format": "mp3_44100_128"})
    if output.suffix == ".mp3":
        output.write_bytes(audio)
    else:
        tmp = output.with_suffix(".tts.mp3")
        tmp.write_bytes(audio)
        subprocess.run(
            ["ffmpeg", "-nostdin", "-y", "-i", str(tmp), "-ac", "1", "-ar", "48000",
             "-c:a", "pcm_s16le", str(output)],
            check=True, capture_output=True,
        )
        tmp.unlink()
    print(f"saved {output}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", nargs="?", help="vo-script.txt to narrate")
    ap.add_argument("-o", "--output", default="vo_raw.wav")
    ap.add_argument("--voice", help="override pinned voice_id (samples/casting only)")
    ap.add_argument("--list-voices", action="store_true")
    ap.add_argument("--search")
    ap.add_argument("--add-voice", nargs=3, metavar=("OWNER_ID", "VOICE_ID", "NAME"))
    ap.add_argument("--sample", nargs=2, metavar=("VOICE_ID", "TEXT"))
    ap.add_argument("--design", nargs=2, metavar=("DESCRIPTION", "TEXT"),
                    help="voice design casting: generate candidate previews into --output dir")
    ap.add_argument("--create-from-preview", nargs=3, metavar=("GENERATED_VOICE_ID", "NAME", "DESCRIPTION"))
    args = ap.parse_args()

    if args.list_voices:
        return list_voices(args.search)
    if args.add_voice:
        return add_voice(*args.add_voice)
    if args.design:
        return design_previews(args.design[0], args.design[1], Path(args.output))
    if args.create_from_preview:
        return create_from_preview(*args.create_from_preview)
    if args.sample:
        return tts(args.sample[0], args.sample[1], Path(args.output))

    if not args.script:
        sys.exit("usage: tts-thai.py vo-script.txt -o vo_raw.wav (or --list-voices / --sample)")

    if args.voice:
        voice_id, settings = args.voice, DEFAULT_SETTINGS
    else:
        if not VOICE_FILE.exists():
            sys.exit(f"{VOICE_FILE} missing — run voice casting and pin a voice_id first")
        pinned = json.loads(VOICE_FILE.read_text())
        voice_id, settings = pinned["voice_id"], pinned.get("voice_settings", DEFAULT_SETTINGS)

    text = Path(args.script).read_text(encoding="utf-8").strip()
    tts(voice_id, text, Path(args.output), settings)


if __name__ == "__main__":
    main()
