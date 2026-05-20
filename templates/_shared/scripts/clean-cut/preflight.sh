#!/usr/bin/env bash
# Check what's installed for bizdrive-clean-cut. Outputs JSON.
# Used by the skill at trigger time before doing any work.
# Portable across macOS / Linux / Windows (Git Bash, WSL).

check() { command -v "$1" >/dev/null 2>&1 && echo yes || echo no; }

FFMPEG=$(check ffmpeg)
FFPROBE=$(check ffprobe)
PYTHON3=$(check python3)
BREW=$(check brew)

# Python version (e.g. 3.9.6). Empty if python3 missing.
PYTHON3_VERSION=""
if [ "$PYTHON3" = "yes" ]; then
    PYTHON3_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null || echo "")
fi

# Platform detection
case "$(uname -s)" in
    Darwin*) PLATFORM="macos" ;;
    Linux*)  PLATFORM="linux" ;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
    *)       PLATFORM="unknown" ;;
esac

# Silero VAD = venv exists AND imports cleanly
VENV="$HOME/.ii23/vad-env"
SILERO=no
if [ -d "$VENV" ] && [ -x "$VENV/bin/python3" ]; then
    if "$VENV/bin/python3" -c "from silero_vad import load_silero_vad" >/dev/null 2>&1; then
        SILERO=yes
    fi
fi

# Saved preference (from save_preference.sh). Falls back to "unset".
CONFIG="$HOME/.ii23/config.json"
PREF="unset"
if [ -f "$CONFIG" ]; then
    # naive JSON read — works as long as save_preference.sh writes the same shape
    PREF_VAL=$(python3 -c "import json,sys; print(json.load(open('$CONFIG')).get('preferred_detector','unset'))" 2>/dev/null || echo "unset")
    [ -n "$PREF_VAL" ] && PREF="$PREF_VAL"
fi

cat <<EOF
{
  "ffmpeg": "$FFMPEG",
  "ffprobe": "$FFPROBE",
  "python3": "$PYTHON3",
  "python3_version": "$PYTHON3_VERSION",
  "silero_vad": "$SILERO",
  "brew": "$BREW",
  "platform": "$PLATFORM",
  "vad_env_path": "$VENV",
  "preferred_detector": "$PREF"
}
EOF
