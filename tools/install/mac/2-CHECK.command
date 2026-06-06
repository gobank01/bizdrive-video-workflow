#!/usr/bin/env bash
# BIZDRIVE Video — install checker (Mac). Double-click to confirm everything
# is installed. Read-only — installs nothing.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
cd "$REPO_ROOT"

G=$'\e[32m'; R=$'\e[31m'; Y=$'\e[33m'; D=$'\e[2m'; Z=$'\e[0m'
pass=0; fail=0
yes() { printf "  ${G}[OK]${Z}   %s ${D}%s${Z}\n" "$1" "$2"; pass=$((pass+1)); }
no()  { printf "  ${R}[X]${Z}    %s ${Y}→ %s${Z}\n" "$1" "$2"; fail=$((fail+1)); }
chk() { command -v "$1" >/dev/null 2>&1; }

echo "============================================================"
echo "  BIZDRIVE Video — ตรวจว่าติดตั้งครบหรือยัง"
echo "============================================================"
echo ""

chk ffmpeg  && yes "ffmpeg (ตัด/เข้ารหัสวิดีโอ)" "$(ffmpeg -version 2>/dev/null | head -1)" || no "ffmpeg"  "เปิด 1-INSTALL.command อีกครั้ง"
chk ffprobe && yes "ffprobe" ""                                        || no "ffprobe" "มากับ ffmpeg"
chk python3 && yes "Python"  "$(python3 --version 2>&1)"               || no "Python"  "เปิด 1-INSTALL.command อีกครั้ง"
chk node    && yes "Node.js" "$(node --version 2>/dev/null)"          || no "Node.js" "เปิด 1-INSTALL.command อีกครั้ง"
chk claude  && yes "Claude Code" ""                                    || no "Claude Code" "ลงด้วย: curl -fsSL https://claude.ai/install.sh | bash"

# Silero VAD venv (Mac path: bin/python3)
VADPY="$HOME/.ii23/vad-env/bin/python3"
if [ -x "$VADPY" ] && "$VADPY" -c "from silero_vad import load_silero_vad" >/dev/null 2>&1; then
  yes "Silero VAD (ตรวจจับเสียงพูด)" ""
else
  no "Silero VAD" "เปิด 1-INSTALL.command อีกครั้ง"
fi

# Thai NLP
if python3 -c "import pythainlp" >/dev/null 2>&1; then yes "ไลบรารีตัดคำไทย (pythainlp)" ""; else no "ไลบรารีตัดคำไทย" "เปิด 1-INSTALL.command อีกครั้ง"; fi

# HyperFrames skills (installed by `npx hyperframes skills` into ~/.claude/skills)
if [ -d "$HOME/.claude/skills/hyperframes" ]; then
  yes "HyperFrames skills" ""
else
  no "HyperFrames skills" "ลงด้วย: npx hyperframes skills (แล้วปิด-เปิด Claude ใหม่)"
fi

# API keys in .env
ENVF="templates/_shared/env/.env"
if [ -f "$ENVF" ]; then
  grep -qE "^[[:space:]]*ELEVENLABS_API_KEY=[^[:space:]]" "$ENVF" && yes "ElevenLabs API key" "" || no "ElevenLabs API key" "จำเป็น — ใส่ key ลงในไฟล์ $ENVF"
  grep -qE "^[[:space:]]*OPENROUTER_API_KEY=[^[:space:]]" "$ENVF" && yes "OpenRouter API key" "" || no "OpenRouter API key" "ใช้ทำ B-roll — ใส่ key ลงในไฟล์ $ENVF"
else
  no "ElevenLabs API key" "ยังไม่มีไฟล์ .env — เปิด 1-INSTALL.command อีกครั้ง"
  no "OpenRouter API key" "ยังไม่มีไฟล์ .env — เปิด 1-INSTALL.command อีกครั้ง"
fi

echo ""
echo "------------------------------------------------------------"
if [ "$fail" -eq 0 ]; then
  printf "  ${G}ครบทุกอย่างแล้ว (ผ่าน %d ข้อ) — พร้อมทำวิดีโอ ✅${Z}\n" "$pass"
  echo "  ขั้นต่อไป: เปิด Terminal ตรงนี้แล้วพิมพ์ claude"
else
  printf "  ${Y}ยังขาด %d ข้อ (ผ่านแล้ว %d ข้อ) — แก้บรรทัดสีแดงด้านบน แล้วเปิดไฟล์นี้ใหม่${Z}\n" "$fail" "$pass"
fi
echo "------------------------------------------------------------"
echo ""
echo "กด Enter เพื่อปิดหน้าต่าง"
read -r _
