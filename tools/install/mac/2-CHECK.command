#!/usr/bin/env bash
# BIZDRIVE Video — install checker (Mac). Double-click to confirm everything
# is installed. Read-only — installs nothing. Mirrors the Windows checker:
# it does NOT check for the Claude Code CLI (students use the VS Code extension).

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
cd "$REPO_ROOT" || exit 1

export PATH="$HOME/.local/bin:$HOME/.bizdrive/bin:$PATH"

G=$'\e[32m'; R=$'\e[31m'; Y=$'\e[33m'; D=$'\e[2m'; Z=$'\e[0m'
pass=0; fail=0
yes() { printf "  ${G}[OK]${Z}   %s ${D}%s${Z}\n" "$1" "$2"; pass=$((pass+1)); }
no()  { printf "  ${R}[X]${Z}    %s ${Y}-> %s${Z}\n" "$1" "$2"; fail=$((fail+1)); }
chk() { command -v "$1" >/dev/null 2>&1; }

echo "============================================================"
echo "  BIZDRIVE Video — install check"
echo "============================================================"
echo ""

if chk git;     then yes "Git"     "$(git --version 2>/dev/null)";    else no "Git"     "re-run 1-INSTALL.command"; fi
if chk ffmpeg;  then yes "ffmpeg"   "$(ffmpeg -version 2>/dev/null | head -1)"; else no "ffmpeg"  "re-run 1-INSTALL.command"; fi
if chk ffprobe; then yes "ffprobe"  "";                                else no "ffprobe" "ships with ffmpeg"; fi
if chk python3; then yes "Python"   "$(python3 --version 2>&1)";        else no "Python"  "re-run 1-INSTALL.command"; fi
if chk node;    then yes "Node.js"  "$(node --version 2>/dev/null)";    else no "Node.js" "re-run 1-INSTALL.command"; fi

# Silero VAD venv
VADPY="$HOME/.bizdrive/vad-env/bin/python3"
if [ -x "$VADPY" ] && "$VADPY" -c "from silero_vad import load_silero_vad" >/dev/null 2>&1; then
  yes "Silero VAD (voice detection)" ""
else
  no "Silero VAD" "re-run 1-INSTALL.command"
fi

# Thai NLP
if python3 -c "import pythainlp" >/dev/null 2>&1; then yes "Thai NLP (pythainlp)" ""; else no "Thai NLP (pythainlp)" "re-run 1-INSTALL.command"; fi

# API keys in .env (OpenRouter is optional — not counted as a failure)
ENVF="templates/_shared/env/.env"
if [ -f "$ENVF" ]; then
  if grep -qE "^[[:space:]]*ELEVENLABS_API_KEY=[^[:space:]]" "$ENVF"; then yes "ElevenLabs API key" ""; else no "ElevenLabs API key" "required — add it to $ENVF"; fi
  if grep -qE "^[[:space:]]*OPENROUTER_API_KEY=[^[:space:]]" "$ENVF"; then yes "OpenRouter API key (optional)" ""; else printf "  %s[--]   OpenRouter API key (optional)  not set — only needed for AI B-roll%s\n" "$D" "$Z"; fi
else
  no "ElevenLabs API key" "no .env yet — re-run 1-INSTALL.command"
fi

echo ""
echo "------------------------------------------------------------"
if [ "$fail" -eq 0 ]; then
  printf "  ${G}All good (%d checks passed) — ready to make videos.${Z}\n" "$pass"
  echo "  Next: open this folder in VS Code and use the Claude Code panel."
else
  printf "  ${Y}%d missing, %d OK. Fix the red lines, then run this again.${Z}\n" "$fail" "$pass"
fi
echo "------------------------------------------------------------"
echo ""
echo "Press Enter to close."
read -r _
