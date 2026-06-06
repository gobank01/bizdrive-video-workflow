#!/usr/bin/env bash
# BIZDRIVE Video — one-click Mac installer.
#
# Double-click this in Finder. It finds the repo (this file lives inside it),
# then runs tools/setup.sh, which installs ffmpeg/Python/Node via Homebrew,
# the Thai NLP libs + Silero VAD, and asks for your API keys.
#
# First run only: if Homebrew isn't installed yet, macOS will ask for your
# login password once (that's Homebrew, not us). Everything after is automatic.

set -e

# This file is at tools/install/mac/ — the repo root is three levels up.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
cd "$REPO_ROOT"

echo "============================================================"
echo "  BIZDRIVE Video — ตัวติดตั้งสำหรับ Mac"
echo "  โฟลเดอร์โปรเจกต์: $REPO_ROOT"
echo "============================================================"
echo ""

bash tools/setup.sh

echo ""
echo "เสร็จแล้ว ✅  ขั้นต่อไป: ดับเบิลคลิก 2-CHECK.command เพื่อตรวจว่าครบ"
echo "หรือเปิด Terminal ตรงนี้แล้วพิมพ์ claude เพื่อเริ่มทำวิดีโอ"
echo "กด Enter เพื่อปิดหน้าต่าง"
read -r _
