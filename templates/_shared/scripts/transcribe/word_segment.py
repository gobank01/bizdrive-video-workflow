#!/usr/bin/env python3
"""
word_segment.py — Turn ElevenLabs character-level transcripts into real word-level
timestamps using a Thai NLP tokenizer.

Problem this solves:
  ElevenLabs Scribe v2 returns "timestamps_granularity=word" for Thai, but Thai has
  no spaces between words — so ELL effectively returns one entry per character.
  Each entry has its own (start, end) timestamp. To build word-level captions
  (Submagic-style kinetic typography), we need:
    1. Read all character-level entries from raw.json
    2. Reconstruct full text + a char_index → (start, end) map
    3. Segment the full text into Thai words using a real tokenizer (pythainlp)
    4. Walk through the segmented words, matching characters back to the char map,
       to derive each word's real start/end from ELL's actual audio timing

Usage:
  python3 word_segment.py raw.json --output captions-words.json
                                   [--engine newmm|nlpo3]
                                   [--words-per-group N]
                                   [--custom-dict word1,word2,brand1]

Output (captions-words.json):
  {
    "duration": 21.0,
    "language": "th",
    "engine": "nlpo3",
    "words_per_group": 1,
    "groups": [
      {"start": 0.10, "end": 0.30, "text": "อยาก"},
      {"start": 0.30, "end": 0.42, "text": "จะ"},
      ...
    ]
  }
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def load_raw(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_char_map(raw: dict) -> Tuple[str, List[Tuple[float, float]]]:
    """
    Build full reconstructed text + per-character (start, end) list.

    Both ElevenLabs (with timestamps_granularity=word for Thai) and Whisper-style
    providers fit this shape: words[] entries where each entry is a single character
    (or whitespace) with its own timestamps. The function is provider-agnostic.

    Returns (full_text, list_of_(start,end)_per_char).
    """
    full_text = ""
    char_timestamps: List[Tuple[float, float]] = []
    for entry in raw.get("words", []):
        text = entry.get("text", "")
        start = float(entry.get("start", 0.0))
        end = float(entry.get("end", start))
        for ch in text:
            full_text += ch
            char_timestamps.append((start, end))
    return full_text, char_timestamps


def segment(text: str, engine: str, custom_words: Optional[List[str]] = None) -> List[str]:
    """
    Segment Thai text into words.

    engine='newmm' — dict-based, fast, built-in (no deps beyond pythainlp itself)
    engine='nlpo3' — Rust dict-based, ~3x faster than newmm, same accuracy
                     (recommended default)
    """
    from pythainlp.tokenize import word_tokenize, Tokenizer

    if custom_words:
        from pythainlp.corpus.common import thai_words
        base = set(thai_words())
        for w in custom_words:
            base.add(w)
        tokenizer = Tokenizer(custom_dict=base, engine="newmm")
        words = tokenizer.word_tokenize(text)
    elif engine == "nlpo3":
        # nlpo3 needs explicit dict load on first call
        try:
            import nlpo3
            import pythainlp
            from pathlib import Path as _Path
            dict_path = _Path(pythainlp.__file__).parent / "corpus" / "words_th.txt"
            try:
                nlpo3.load_dict(str(dict_path), "default")
            except Exception:
                # already loaded
                pass
            words = word_tokenize(text, engine="nlpo3", keep_whitespace=False)
        except ImportError:
            print("⚠ nlpo3 not installed. Run: pip install nlpo3", file=sys.stderr)
            print("  Falling back to newmm.", file=sys.stderr)
            words = word_tokenize(text, engine="newmm", keep_whitespace=False)
    else:
        words = word_tokenize(text, engine=engine, keep_whitespace=False)

    # Drop empty / pure-whitespace tokens
    return [w for w in words if w and not w.isspace()]


def align_words(text: str, char_map: List[Tuple[float, float]], words: List[str]) -> List[Dict]:
    """
    Walk through words, consume characters from the char_map, record start (first char
    of word) and end (last char of word) of each word.

    The Thai 'ๆ' repetition marker is merged into the previous word — it doesn't read
    naturally as its own caption pop.
    """
    result: List[Dict] = []
    char_idx = 0
    n = len(char_map)

    for w in words:
        # Skip whitespace chars in the char_map between words
        while char_idx < n and text[char_idx].isspace():
            char_idx += 1
        if char_idx >= n:
            break

        word_start = char_map[char_idx][0]
        matched = 0
        last_char_end = word_start
        target_len = len(w)
        while matched < target_len and char_idx < n:
            # If the char at char_idx matches the next char of w, consume it.
            # Otherwise skip (e.g. ELL emitted a stray spacing).
            if text[char_idx] == w[matched]:
                last_char_end = char_map[char_idx][1]
                matched += 1
            char_idx += 1

        # Merge 'ๆ' into previous word — it's a repetition marker, not a standalone word
        if w == "ๆ" and result:
            result[-1]["text"] += "ๆ"
            result[-1]["end"] = round(last_char_end, 3)
            continue

        result.append({
            "start": round(word_start, 3),
            "end": round(last_char_end, 3),
            "text": w,
        })
    return result


def group_words(words: List[Dict], words_per_group: int) -> List[Dict]:
    """
    Bucket consecutive words into groups of N. start = first word's start,
    end = last word's end, text = space-joined (Thai natural — no actual space inserted).
    """
    if words_per_group <= 1:
        return words
    groups: List[Dict] = []
    for i in range(0, len(words), words_per_group):
        chunk = words[i:i + words_per_group]
        groups.append({
            "start": chunk[0]["start"],
            "end": chunk[-1]["end"],
            "text": "".join(w["text"] for w in chunk),
        })
    return groups


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("raw_json", help="Path to raw.json from transcribe.py")
    parser.add_argument("--output", "-o", required=True, help="Output captions JSON path")
    parser.add_argument("--engine", default="nlpo3", choices=["newmm", "nlpo3"],
                        help="Thai word segmenter (default: nlpo3 — 3x faster, same accuracy)")
    parser.add_argument("--words-per-group", type=int, default=1,
                        help="Words per caption group (1 = pure kinetic per-word, 3 = phrase-style). Default: 1")
    parser.add_argument("--custom-dict", default="",
                        help="Comma-separated extra words the segmenter should keep intact (e.g. 'บอกว่า,Mark Zuckerberg,GPU')")
    args = parser.parse_args()

    raw = load_raw(args.raw_json)
    text, char_map = build_char_map(raw)

    custom = [w.strip() for w in args.custom_dict.split(",") if w.strip()] if args.custom_dict else None
    words_seg = segment(text, args.engine, custom_words=custom)
    aligned = align_words(text, char_map, words_seg)
    groups = group_words(aligned, args.words_per_group)

    out = {
        "duration": raw.get("audio_duration_secs") or raw.get("duration"),
        "language": raw.get("language") or raw.get("language_code"),
        "engine": args.engine if not custom else f"{args.engine}+custom-dict",
        "words_per_group": args.words_per_group,
        "char_count": len(char_map),
        "word_count": len(aligned),
        "group_count": len(groups),
        "groups": groups,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "engine": out["engine"],
        "words_per_group": args.words_per_group,
        "chars": len(char_map),
        "words": len(aligned),
        "groups": len(groups),
        "output": args.output,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
