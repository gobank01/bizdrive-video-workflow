#!/usr/bin/env python3
"""Post-process: raw ElevenLabs transcript -> caption-groups.json (arm2 / 9arm clip).

Segments each transcript phrase into 1-3 token caption groups (<=22 Thai chars),
interpolates per-group timing across the phrase by character weight, applies
text fixes, and tags gold tokens (brand/place/headline terms).
"""

import json
from pathlib import Path
from pythainlp.tokenize import word_tokenize

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets/intermediates/transcript/raw-elevenlabs.json"
OUT = ROOT / "assets/intermediates/transcript/caption-groups.json"
DURATION = 65.313333

# --- text fixes (STT glitches) ---
FIXES = {
    "이사าน": "อีสาน",       # Korean-char glitch -> Thai
    "กูกงงว่า": "กูก็งงว่า",  # dropped syllable
}

# gold = brand/tech + place names that are headline terms
GOLD_EXACT_SUBSTR = ["Twitter", "norm", "อีสาน", "ขอนแก่น", "ราชสีมา", "มินิโซต้า"]
MAX_GROUP_CHARS = 22
MAX_TOKENS = 3
TARGET_TOKEN_CHARS = 9


def clean(text: str) -> str:
    for k, v in FIXES.items():
        text = text.replace(k, v)
    return text


def tokenize_display(text: str):
    words = [w for w in word_tokenize(text, engine="newmm") if w.strip()]
    tokens, cur = [], ""
    for w in words:
        if cur and len(cur) + len(w) > TARGET_TOKEN_CHARS:
            tokens.append(cur)
            cur = w
        else:
            cur += w
    if cur:
        if tokens and len(cur) <= 2:
            tokens[-1] += cur
        else:
            tokens.append(cur)
    return tokens


def main():
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    phrases = []
    for w in raw["words"]:
        t = w["text"].strip()
        if t.startswith("[") and t.endswith("]"):
            continue  # non-speech tag — drop
        t = clean(t)
        if t == "บ้านกูอยู่จ-อ":
            t = "บ้านกูอยู่"  # speaker cut off mid-word
        phrases.append({
            "text": t,
            "start": float(w["start"]),
            "end": min(float(w["end"]), DURATION),
        })

    groups = []
    for ph in phrases:
        tokens = tokenize_display(ph["text"])
        cgroups, cur, cur_chars = [], [], 0
        for tok in tokens:
            if cur and (len(cur) >= MAX_TOKENS or cur_chars + len(tok) > MAX_GROUP_CHARS):
                cgroups.append(cur)
                cur, cur_chars = [], 0
            cur.append(tok)
            cur_chars += len(tok)
        if cur:
            cgroups.append(cur)

        total_chars = sum(sum(len(t) for t in g) for g in cgroups) or 1
        span = max(0.001, ph["end"] - ph["start"])
        cursor = ph["start"]
        for g in cgroups:
            gchars = sum(len(t) for t in g)
            gend = min(ph["end"], cursor + span * (gchars / total_chars))
            groups.append({
                "start": round(cursor, 3),
                "end": round(gend, 3),
                "tokens": [{"text": t, "gold": False} for t in g],
            })
            cursor = gend

    # --- gold tagging ---
    korat_seen = 0
    gold_count = 0
    for g in groups:
        for tok in g["tokens"]:
            txt = tok["text"]
            if any(k in txt for k in GOLD_EXACT_SUBSTR):
                tok["gold"] = True
            elif "โคราช" in txt:
                korat_seen += 1
                if korat_seen % 2 == 1:  # gold every other Korat token
                    tok["gold"] = True
            if tok["gold"]:
                gold_count += 1

    data = {
        "duration": DURATION,
        "language": "th",
        "groups": groups,
        "notes": [
            "Built from raw-elevenlabs.json by scripts/make-caption-groups.py.",
            "Fixes: Korean-char glitch -> อีสาน; กูกงง -> กูก็งง; trailing cut word trimmed.",
            "Non-speech tags [..] dropped. Profanity kept verbatim (creator style).",
        ],
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tok_total = sum(len(g["tokens"]) for g in groups)
    print(f"  Wrote {OUT.relative_to(ROOT)}")
    print(f"  Groups: {len(groups)} | tokens: {tok_total} (gold {gold_count} / white {tok_total - gold_count})")


if __name__ == "__main__":
    main()
