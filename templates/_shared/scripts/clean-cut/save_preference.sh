#!/usr/bin/env bash
# Save the user's detector preference to ~/.bizdrive/config.json so the skill
# doesn't ask every time.
#
# Usage: save_preference.sh vad      # or "ffmpeg"

set -e

CHOICE="$1"
if [ "$CHOICE" != "vad" ] && [ "$CHOICE" != "ffmpeg" ]; then
    echo "error: pass 'vad' or 'ffmpeg' as arg" >&2
    exit 1
fi

mkdir -p "$HOME/.bizdrive"
CONFIG="$HOME/.bizdrive/config.json"

python3 - <<PY
import json, os
path = "$CONFIG"
data = {}
if os.path.exists(path):
    try:
        data = json.load(open(path))
    except Exception:
        data = {}
data["preferred_detector"] = "$CHOICE"
with open(path, "w") as f:
    json.dump(data, f, indent=2)
print(f"saved preferred_detector={data['preferred_detector']} to {path}")
PY
