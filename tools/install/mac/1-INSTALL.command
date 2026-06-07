#!/usr/bin/env bash
# BIZDRIVE Video — one-click Mac installer.
#
# Double-click this in Finder. It finds the repo (this file lives inside it),
# then runs tools/setup.sh, which installs ffmpeg/Python/Node, the Thai NLP libs
# + Silero VAD, and asks for your API keys. It does NOT install the Claude Code
# CLI — use the Claude Code VS Code extension.
# If Homebrew already exists, setup uses it. If not, setup downloads user-level
# tools into ~/.bizdrive/bin so a fresh Mac does not need a password prompt.

set -e

# This file is at tools/install/mac/ — the repo root is three levels up.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
cd "$REPO_ROOT"

echo "============================================================"
echo "  BIZDRIVE Video — Mac installer"
echo "  project folder: $REPO_ROOT"
echo "============================================================"
echo ""

bash tools/setup.sh

echo ""
echo "Done. Next: double-click 2-CHECK.command to verify everything is installed."
echo "Then open this folder in VS Code and use the Claude Code panel."
echo "Press Enter to close."
read -r _
