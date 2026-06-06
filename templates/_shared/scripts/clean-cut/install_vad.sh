#!/usr/bin/env bash
# Install Silero VAD into ~/.bizdrive/vad-env (Python venv).
# ~437MB total (torch is the bulk). Idempotent — safe to re-run.

set -e

VENV="$HOME/.bizdrive/vad-env"

# Already installed? Done. (venv python is bin/python3 on macOS/Linux.)
if [ -d "$VENV" ] && "$VENV/bin/python3" -c "from silero_vad import load_silero_vad" 2>/dev/null; then
    echo "✓ Silero VAD already installed at $VENV"
    exit 0
fi

# Choose the interpreter that BUILDS the venv. setup.sh exports the one it
# vetted (>= 3.10) as BIZDRIVE_PYTHON; honour it so we never build the venv with
# macOS's system python3 (3.9). When run standalone, scan for a 3.10+ python the
# same way — falling back to bare python3 only as a last resort.
PY="${BIZDRIVE_PYTHON:-}"
if [ -z "$PY" ]; then
    for c in python3.13 python3.12 python3.11 python3.10 python3; do
        command -v "$c" >/dev/null 2>&1 || continue
        "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >/dev/null 2>&1 || continue
        PY="$c"; break
    done
fi
if [ -z "$PY" ] || ! command -v "$PY" >/dev/null 2>&1; then
    echo "✗ Python 3.10+ not found. Install one first:" >&2
    echo "  macOS:   brew install python@3.12" >&2
    echo "  Linux:   sudo apt-get install python3 python3-venv" >&2
    exit 1
fi

PY_OK=$("$PY" -c "import sys; print('yes' if sys.version_info >= (3, 10) else 'no')" 2>/dev/null || echo "no")
if [ "$PY_OK" != "yes" ]; then
    echo "✗ Need Python 3.10+, '$PY' is $("$PY" --version 2>&1). Upgrade before retrying." >&2
    exit 1
fi

# venv module available?
if ! "$PY" -c "import venv" 2>/dev/null; then
    echo "✗ Python venv module missing. On Debian/Ubuntu run:" >&2
    echo "  sudo apt-get install python3-venv" >&2
    exit 1
fi

# Free disk: need ~600MB headroom in $HOME (~437MB install + safety margin)
if command -v df >/dev/null 2>&1; then
    AVAIL_KB=$(df -k "$HOME" | tail -1 | awk '{print $4}')
    AVAIL_MB=$((AVAIL_KB / 1024))
    if [ "$AVAIL_MB" -lt 600 ]; then
        echo "⚠ Only ${AVAIL_MB}MB free in \$HOME — install needs ~600MB. Free up space and retry." >&2
        exit 1
    fi
fi

echo "→ Creating venv at $VENV (~437MB, ~3-5 min) using $("$PY" --version 2>&1)"
mkdir -p "$HOME/.bizdrive"
"$PY" -m venv "$VENV" || {
    echo "✗ venv creation failed. Common causes:" >&2
    echo "  - python3-venv missing (Linux): apt-get install python3-venv" >&2
    echo "  - corporate proxy blocking download" >&2
    echo "  - disk full or permissions issue" >&2
    exit 1
}

echo "→ Upgrading pip..."
"$VENV/bin/pip" install --quiet --upgrade pip 2>&1 | tail -3 || {
    echo "✗ pip upgrade failed. Network issue? Re-run when connected." >&2
    exit 1
}

echo "→ Installing silero-vad + soundfile + numpy (this is the slow step)..."
"$VENV/bin/pip" install --quiet silero-vad soundfile numpy 2>&1 | tail -3 || {
    echo "✗ pip install failed. Common causes:" >&2
    echo "  - network interrupted partway through 400MB download" >&2
    echo "  - pip cache corrupted: rm -rf ~/.cache/pip and retry" >&2
    echo "  - older Python (< 3.9): check 'python3 --version'" >&2
    exit 1
}

# Verify the whole chain imports
if "$VENV/bin/python3" -c "from silero_vad import load_silero_vad, read_audio, get_speech_timestamps" 2>/dev/null; then
    echo "✓ Silero VAD installed at $VENV"
    echo "  Use: $VENV/bin/python3 <script>"
else
    echo "✗ Install verification failed — silero_vad imports but missing helpers." >&2
    echo "  Try: rm -rf $VENV  and re-run this script." >&2
    exit 1
fi
