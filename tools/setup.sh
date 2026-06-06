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
echo " BIZDRIVE Video — กำลังติดตั้งเครื่องมือทั้งหมด"
echo "=================================================="
echo ""

ENV_FILE="templates/_shared/env/.env"
ENV_EXAMPLE="templates/_shared/env/.env.example"

# trim — strip leading/trailing whitespace and any CR (users paste keys with a
# trailing space or a Windows newline; an untrimmed key silently fails auth).
trim() {
  s="$1"
  s="${s%$'\r'}"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

# set_env_line <file> <KEY> <value> — set or replace KEY=value, uncommenting it.
set_env_line() {
  f="$1"; k="$2"; v="$3"
  if grep -qE "^\s*#?\s*$k=" "$f"; then
    tmp="$f.tmp.$$"; sed "s|^[[:space:]]*#\{0,1\}[[:space:]]*$k=.*|$k=$v|" "$f" > "$tmp" && mv "$tmp" "$f"
  else
    printf '%s=%s\n' "$k" "$v" >> "$f"
  fi
}

# key_filled <KEY> — true if that key already has a non-empty value in .env.
key_filled() {
  [ -f "$ENV_FILE" ] && grep -qE "^[[:space:]]*$1=[[:space:]]*[^[:space:]]" "$ENV_FILE"
}

# --- API keys FIRST, before the long installs, so the user pastes them up
# front and can walk away while everything downloads. ---
echo "→ ใส่ API key (วางตรงนี้ก่อนเลย แล้วระบบจะติดตั้งให้ระหว่างที่คุณรอ)..."
[ -f "$ENV_FILE" ] || { cp "$ENV_EXAMPLE" "$ENV_FILE"; echo "  ✓ สร้างไฟล์เก็บ key แล้ว"; }

NEED_EL=1; key_filled "ELEVENLABS_API_KEY" && NEED_EL=0
NEED_OR=1; key_filled "OPENROUTER_API_KEY" && NEED_OR=0

if [ "$NEED_EL" = 0 ] && [ "$NEED_OR" = 0 ]; then
  echo "  ✓ ใส่ key ครบแล้ว (ข้ามขั้นตอนนี้)"
elif [ -t 0 ]; then
  echo "    ElevenLabs (จำเป็น — ใช้ถอดเสียงเป็นข้อความ): https://elevenlabs.io/app/settings/api-keys"
  echo "    OpenRouter (ใช้สร้าง B-roll ด้วย AI)      : https://openrouter.ai/keys"
  if [ "$NEED_EL" = 1 ]; then
    printf "  วาง ElevenLabs API key: "; read -r EL_KEY; EL_KEY=$(trim "$EL_KEY")
    while [ -z "$EL_KEY" ]; do
      printf "  (จำเป็น ห้ามเว้นว่าง) ElevenLabs API key: "; read -r EL_KEY; EL_KEY=$(trim "$EL_KEY")
    done
    set_env_line "$ENV_FILE" "ELEVENLABS_API_KEY" "$EL_KEY"
  fi
  if [ "$NEED_OR" = 1 ]; then
    printf "  วาง OpenRouter API key (ถ้ายังไม่มี กด Enter ข้ามได้): "; read -r OR_KEY; OR_KEY=$(trim "$OR_KEY")
    [ -n "$OR_KEY" ] && set_env_line "$ENV_FILE" "OPENROUTER_API_KEY" "$OR_KEY"
  fi
  echo "  ✓ บันทึก key เรียบร้อย — เริ่มติดตั้งต่อเลย"
else
  echo "  ⚠ ยังไม่ได้ใส่ key — ก่อนทำวิดีโอ ให้ใส่ key ลงในไฟล์ $ENV_FILE :"
  [ "$NEED_EL" = 1 ] && echo "      ELEVENLABS_API_KEY=  (จำเป็น)"
  [ "$NEED_OR" = 1 ] && echo "      OPENROUTER_API_KEY=  (สำหรับ B-roll)"
fi
echo ""

# --- 0. Detect OS + package manager (for auto-install) ---
case "$(uname -s)" in
  Darwin*) OS="macos" ;;
  Linux*)  OS="linux" ;;          # includes WSL (Windows users run inside WSL/Ubuntu)
  MINGW*|MSYS*|CYGWIN*) OS="gitbash" ;;
  *) OS="unknown" ;;
esac

# auto_install <tool> — try to install a missing system tool for the current OS.
# Returns 0 if installed (or already adequate), 1 if it could not.
# "adequate" is tool-specific: python3 must also have pip+venv, node must be
# >= 18. A bare `command -v` is NOT enough — a fresh WSL has python3 without
# pip/venv, and apt may already have an old node; in both cases we must still
# install/upgrade rather than return early on the binary alone.
auto_install() {
  tool="$1"
  case "$tool" in
    python3) python_stack_ok && return 0 ;;
    node)    node_ok && return 0 ;;
    *)       command -v "$tool" >/dev/null 2>&1 && return 0 ;;
  esac
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
        git) brew install git ;;
        curl) brew install curl ;;
      esac ;;
    linux)
      if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update -qq
        case "$tool" in
          ffmpeg|ffprobe) sudo apt-get install -y ffmpeg ;;
          node) install_node_apt ;;
          python3) sudo apt-get install -y python3 python3-pip python3-venv ;;
          git) sudo apt-get install -y git ;;
          curl) sudo apt-get install -y curl ;;
        esac
      elif command -v dnf >/dev/null 2>&1; then
        case "$tool" in
          ffmpeg|ffprobe) sudo dnf install -y ffmpeg ;;
          node) sudo dnf install -y nodejs npm ;;
          python3) sudo dnf install -y python3 python3-pip ;;
          git) sudo dnf install -y git ;;
          curl) sudo dnf install -y curl ;;
        esac
      else
        return 1
      fi ;;
    *) return 1 ;;
  esac
  # Final verdict uses the same tool-specific adequacy check as the entry guard.
  case "$tool" in
    python3) python_stack_ok ;;
    node)    node_ok ;;
    *)       command -v "$tool" >/dev/null 2>&1 ;;
  esac
}

# Repo needs Node 18+. Ubuntu's apt often ships an older Node, so install the
# current LTS from NodeSource. Falls back to apt if the NodeSource setup fails.
install_node_apt() {
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - 2>/dev/null \
    && sudo apt-get install -y nodejs && return 0
  sudo apt-get install -y nodejs npm
}

# node_ok — true only if node exists AND is >= 18.
node_ok() {
  command -v node >/dev/null 2>&1 || return 1
  ver=$(node -p "process.versions.node.split('.')[0]" 2>/dev/null || echo 0)
  [ "$ver" -ge 18 ] 2>/dev/null
}

# py_ge_310 <cmd> — true if the given python command is >= 3.10.
py_ge_310() {
  "$1" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >/dev/null 2>&1
}

# pick_python — echo the best python command on this machine: the first one
# that is >= 3.10 AND has pip+venv. macOS ships /usr/bin/python3 = 3.9, so we
# must NOT trust a bare `python3` — we scan the versioned names Homebrew/apt
# install (python3.13 … python3.10) and prefer those. Echoes nothing if none
# qualify (caller then installs one).
pick_python() {
  for c in python3.13 python3.12 python3.11 python3.10 python3 python; do
    command -v "$c" >/dev/null 2>&1 || continue
    py_ge_310 "$c" || continue
    "$c" -c "import ensurepip, venv" >/dev/null 2>&1 || continue
    "$c" -m pip --version >/dev/null 2>&1 || continue
    echo "$c"; return 0
  done
  return 1
}

# python_stack_ok — true if SOME python >= 3.10 with pip+venv exists. Used as
# the auto_install guard so we don't reinstall when a good python is present
# under a versioned name even if bare `python3` is the old system 3.9.
python_stack_ok() { pick_python >/dev/null 2>&1; }

# --- 1. System tools (auto-install what's missing) ---
echo "→ กำลังตรวจเครื่องมือพื้นฐาน (ขาดตัวไหนจะลงให้อัตโนมัติ)..."
STILL_MISSING=""
auto_install git     || STILL_MISSING="$STILL_MISSING git"
auto_install curl    || STILL_MISSING="$STILL_MISSING curl"
auto_install ffmpeg  || STILL_MISSING="$STILL_MISSING ffmpeg"
auto_install ffprobe || STILL_MISSING="$STILL_MISSING ffprobe"

# python3: must have pip + venv too, not just the binary. A fresh WSL ships
# python3 without them, so command -v alone is not enough.
if ! python_stack_ok; then
  auto_install python3 || true
fi
python_stack_ok || STILL_MISSING="$STILL_MISSING python3(+pip/venv)"

# node: must be >= 18, not just present. apt may have an old node already.
if ! node_ok; then
  auto_install node || true
fi
node_ok || STILL_MISSING="$STILL_MISSING node(>=18)"

if [ -n "$STILL_MISSING" ]; then
  echo "✗ ลงเครื่องมือบางตัวให้อัตโนมัติไม่ได้:$STILL_MISSING" >&2
  echo "  ลองลงเองด้วยคำสั่งนี้ แล้วเปิดติดตั้งใหม่:" >&2
  echo "    macOS:        brew install ffmpeg python node" >&2
  echo "    Linux / WSL:  sudo apt-get install -y ffmpeg python3 python3-pip python3-venv" >&2
  echo "                  Node 18+: https://github.com/nodesource/distributions" >&2
  exit 1
fi
# Resolve the python we'll actually use everywhere below. By here auto_install
# has run, so a good one should exist; if not, fail with a clear message.
PY=$(pick_python || true)
if [ -z "$PY" ]; then
  echo "✗ ต้องใช้ Python 3.10 ขึ้นไป (พร้อม pip+venv) แต่หาไม่เจอในเครื่อง" >&2
  echo "  ตอนนี้ python3 คือ '$(command -v python3 >/dev/null 2>&1 && python3 --version 2>&1 || echo ไม่มี)'" >&2
  echo "  ลง Python ใหม่แล้วเปิดติดตั้งอีกครั้ง:" >&2
  echo "    macOS:        brew install python@3.12" >&2
  echo "    Linux / WSL:  sudo apt-get install -y python3 python3-pip python3-venv" >&2
  exit 1
fi
echo "  ✓ ติดตั้ง ffmpeg, ffprobe, Python ($("$PY" --version | cut -d' ' -f2)), Node เรียบร้อย"
export BIZDRIVE_PYTHON="$PY"   # so child scripts (install_vad.sh) reuse it

# python3 shim — the pipeline (v88-clip.sh etc.) calls `python3` ~20 times. On
# macOS that resolves to /usr/bin/python3 = 3.9, which does NOT have the deps we
# just installed into $PY (3.10+). Drop a shim at ~/.ii23/bin/python3 pointing at
# the right interpreter and put that dir first on PATH (via the shell rc) so the
# pipeline always gets the python that owns pythainlp/certifi. Mirrors the
# Windows installer's shim.
if [ "$(command -v python3 2>/dev/null)" != "$PY" ] && ! py_ge_310 "$(command -v python3 2>/dev/null || echo /nonexistent)"; then
  BIN_DIR="$HOME/.ii23/bin"
  mkdir -p "$BIN_DIR"
  PY_ABS="$(command -v "$PY")"
  printf '#!/usr/bin/env bash\nexec "%s" "$@"\n' "$PY_ABS" > "$BIN_DIR/python3"
  chmod +x "$BIN_DIR/python3"
  # Prepend to PATH for this run + persist in the user's rc files.
  case ":$PATH:" in *":$BIN_DIR:"*) : ;; *) PATH="$BIN_DIR:$PATH" ;; esac
  for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
    [ -f "$rc" ] || continue
    grep -qF '.ii23/bin' "$rc" 2>/dev/null || printf '\nexport PATH="$HOME/.ii23/bin:$PATH"\n' >> "$rc"
  done
  echo "  ✓ ตั้งค่าให้ใช้ Python ตัวที่ถูกต้องแล้ว ($PY_ABS)"
fi

# --- 2. Python deps ---
echo ""
echo "→ กำลังลงไลบรารีตัดคำไทย (pythainlp, nlpo3, certifi)..."
# --user fails on PEP 668 "externally-managed" Python (common on Ubuntu/WSL);
# fall back to --break-system-packages, which is safe for these pure-Python libs.
"$PY" -m pip install --user --quiet --upgrade pythainlp nlpo3 certifi 2>/dev/null \
  || "$PY" -m pip install --user --break-system-packages --quiet --upgrade pythainlp nlpo3 certifi
echo "  ✓ ลงไลบรารีตัดคำไทยเรียบร้อย"

# --- 3. Silero VAD venv ---
echo ""
echo "→ กำลังลงตัวตรวจจับเสียงพูด/เงียบ (Silero VAD, ~437 MB ลงครั้งเดียว)..."
if [ -d "$HOME/.ii23/vad-env" ] && "$HOME/.ii23/vad-env/bin/python3" -c "from silero_vad import load_silero_vad" 2>/dev/null; then
  echo "  ✓ ลง Silero VAD ไว้แล้ว"
else
  bash templates/_shared/scripts/clean-cut/install_vad.sh
  # torchaudio 2.11+ needs torchcodec for audio I/O
  "$HOME/.ii23/vad-env/bin/pip" install --quiet torchcodec 2>/dev/null || true
  echo "  ✓ ลง Silero VAD เรียบร้อย"
fi

# --- 4. HyperFrames + its skills ---
# Warm the pinned hyperframes (so the first render doesn't pause to download it)
# and install the HyperFrames skill family for the user's AI tool (Claude Code).
# Skills teach the agent the composition patterns; without them, caption/VFX
# authoring produces broken output. `npx hyperframes skills` is idempotent.
echo ""
echo "→ กำลังลงตัวเรนเดอร์วิดีโอ HyperFrames + skills (ใช้ Node)..."
if command -v npx >/dev/null 2>&1; then
  npx --yes hyperframes@0.6.25 --version >/dev/null 2>&1 \
    && echo "  ✓ เตรียม hyperframes@0.6.25 พร้อมแล้ว (โหลดเก็บไว้ใช้ตอนเรนเดอร์)" \
    || echo "  ⚠ เตรียม hyperframes ล่วงหน้าไม่ได้ — เดี๋ยวจะโหลดเองตอนเรนเดอร์ครั้งแรก"
  if npx --yes hyperframes@0.6.25 skills >/dev/null 2>&1; then
    echo "  ✓ ลง HyperFrames skills แล้ว (ปิด-เปิด Claude Code ใหม่ 1 ครั้งเพื่อโหลด)"
  else
    echo "  ⚠ ยังไม่ได้ลง skills — ลงทีหลังด้วยคำสั่ง: npx hyperframes skills"
  fi
else
  echo "  ⚠ ไม่พบ npx (Node อาจยังไม่ได้ลง) — ข้ามการลง HyperFrames skills"
fi

# --- 5. Preflight ---
echo ""
echo "→ กำลังตรวจสอบขั้นสุดท้ายว่าพร้อมจริงไหม..."
bash templates/_shared/scripts/clean-cut/preflight.sh

echo ""
echo "=================================================="
echo " ✅ ติดตั้งครบแล้ว — พร้อมทำวิดีโอ"
echo "=================================================="
echo ""
echo " ขั้นต่อไป:"
if ! key_filled "ELEVENLABS_API_KEY"; then
  echo "   1. ใส่ ElevenLabs API key ลงในไฟล์ templates/_shared/env/.env"
  echo "      ขอ key ได้ที่ https://elevenlabs.io/app/settings/api-keys"
else
  echo "   1. (ใส่ API key เรียบร้อยแล้ว ✓)"
fi
echo "   2. ปิด-เปิด Claude Code ใหม่ 1 ครั้ง (เพื่อโหลด HyperFrames skills)"
echo "   3. วางคลิปของคุณ แล้วบอก Claude เช่น \"ตัดต่อคลิปนี้ ใช้ Template 01\""
echo "=================================================="
