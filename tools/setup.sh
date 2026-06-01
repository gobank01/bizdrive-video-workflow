#!/usr/bin/env bash
#
# One-command environment setup for the BIZDRIVE video workflow.
# Run once after cloning the repo.
#
# Usage:
#   bash tools/setup.sh
#
# What it does:
#   1. Checks ffmpeg / ffprobe / python3 / node
#   2. Installs Python deps (pythainlp, nlpo3, certifi) to user site-packages
#   3. Installs the Silero VAD venv (~437 MB) into ~/.ii23/vad-env
#   4. Creates templates/_shared/env/.env from .env.example (if missing)
#   5. Runs preflight to confirm everything is ready

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=================================================="
echo " BIZDRIVE video workflow — environment setup"
echo "=================================================="
echo ""

# --- 0. Detect OS + package manager (for auto-install) ---
case "$(uname -s)" in
  Darwin*) OS="macos" ;;
  Linux*)  OS="linux" ;;          # includes WSL (Windows users run inside WSL/Ubuntu)
  MINGW*|MSYS*|CYGWIN*) OS="gitbash" ;;
  *) OS="unknown" ;;
esac

# auto_install <tool> — try to install a missing system tool for the current OS.
# Returns 0 if installed (or already present), 1 if it could not.
auto_install() {
  tool="$1"
  command -v "$tool" >/dev/null 2>&1 && return 0
  echo "  → installing $tool..."
  case "$OS" in
    macos)
      command -v brew >/dev/null 2>&1 || {
        echo "    Homebrew not found. Installing it first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || return 1
        eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null)"
      }
      case "$tool" in
        ffmpeg|ffprobe) brew install ffmpeg ;;   # ffprobe ships with ffmpeg
        node) brew install node ;;
        python3) brew install python ;;
      esac ;;
    linux)
      if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update -qq
        case "$tool" in
          ffmpeg|ffprobe) sudo apt-get install -y ffmpeg ;;
          node) sudo apt-get install -y nodejs npm ;;
          python3) sudo apt-get install -y python3 python3-pip python3-venv ;;
        esac
      elif command -v dnf >/dev/null 2>&1; then
        case "$tool" in
          ffmpeg|ffprobe) sudo dnf install -y ffmpeg ;;
          node) sudo dnf install -y nodejs npm ;;
          python3) sudo dnf install -y python3 python3-pip ;;
        esac
      else
        return 1
      fi ;;
    *) return 1 ;;
  esac
  command -v "$tool" >/dev/null 2>&1
}

# --- 1. System tools (auto-install what's missing) ---
echo "→ Checking system tools (will auto-install any that are missing)..."
STILL_MISSING=""
for t in ffmpeg ffprobe python3 node; do
  auto_install "$t" || STILL_MISSING="$STILL_MISSING $t"
done
if [ -n "$STILL_MISSING" ]; then
  echo "✗ Could not auto-install:$STILL_MISSING" >&2
  echo "  Install them by hand, then re-run this script:" >&2
  echo "    macOS:        brew install ffmpeg python node" >&2
  echo "    Linux / WSL:  sudo apt-get install -y ffmpeg python3 python3-venv nodejs npm" >&2
  exit 1
fi
PY_OK=$(python3 -c "import sys; print('yes' if sys.version_info >= (3,10) else 'no')")
if [ "$PY_OK" != "yes" ]; then
  echo "✗ Python 3.10+ required (found $(python3 --version))" >&2
  exit 1
fi
echo "  ✓ ffmpeg, ffprobe, python3 ($(python3 --version | cut -d' ' -f2)), node"

# --- 2. Python deps ---
echo ""
echo "→ Installing Python deps (pythainlp, nlpo3, certifi)..."
# --user fails on PEP 668 "externally-managed" Python (common on Ubuntu/WSL);
# fall back to --break-system-packages, which is safe for these pure-Python libs.
python3 -m pip install --user --quiet --upgrade pythainlp nlpo3 certifi 2>/dev/null \
  || python3 -m pip install --user --break-system-packages --quiet --upgrade pythainlp nlpo3 certifi
echo "  ✓ Thai NLP libs + certifi installed"

# --- 3. Silero VAD venv ---
echo ""
echo "→ Installing Silero VAD venv (~437 MB, one-time)..."
if [ -d "$HOME/.ii23/vad-env" ] && "$HOME/.ii23/vad-env/bin/python3" -c "from silero_vad import load_silero_vad" 2>/dev/null; then
  echo "  ✓ Silero VAD already installed"
else
  bash templates/_shared/scripts/clean-cut/install_vad.sh
  # torchaudio 2.11+ needs torchcodec for audio I/O
  "$HOME/.ii23/vad-env/bin/pip" install --quiet torchcodec 2>/dev/null || true
  echo "  ✓ Silero VAD installed"
fi

# --- 4. .env ---
echo ""
echo "→ Setting up API key file..."
ENV_FILE="templates/_shared/env/.env"
ENV_EXAMPLE="templates/_shared/env/.env.example"
if [ -f "$ENV_FILE" ]; then
  echo "  ✓ $ENV_FILE already exists (left untouched)"
else
  cp "$ENV_EXAMPLE" "$ENV_FILE"
  echo "  ✓ Created $ENV_FILE from template"
  echo "  ⚠ EDIT IT — add your ELEVENLABS_API_KEY (and OPENROUTER_API_KEY for B-roll)"
fi

# --- 5. Preflight ---
echo ""
echo "→ Running preflight..."
bash templates/_shared/scripts/clean-cut/preflight.sh

echo ""
echo "=================================================="
echo " Setup complete."
echo ""
echo " Next steps:"
echo "   1. Edit templates/_shared/env/.env — add your API keys"
echo "      ElevenLabs: https://elevenlabs.io/app/settings/api-keys"
echo "      OpenRouter: https://openrouter.ai/keys"
echo "   2. Read ONBOARDING.md"
echo "   3. Start a job:  bash tools/new-job.sh 01 <slug> --raw <raw-slug>"
echo "=================================================="
