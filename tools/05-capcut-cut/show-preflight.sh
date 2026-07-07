#!/usr/bin/env bash
# เช็คความพร้อมก่อนเดโม่สด — รัน 30 นาทีก่อนขึ้นเวที
# Usage: bash tools/05-capcut-cut/show-preflight.sh [draft-name]
set -uo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
DRAFT="${1:-}"
PASS=0; FAIL=0
ok()   { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad()  { echo "  ❌ $1"; FAIL=$((FAIL+1)); }

echo "── เครื่องมือพื้นฐาน"
command -v ffmpeg  >/dev/null && ok "ffmpeg"  || bad "ffmpeg หาย"
command -v ffprobe >/dev/null && ok "ffprobe" || bad "ffprobe หาย"
python3 -c "import pythainlp" 2>/dev/null && ok "pythainlp" || bad "pythainlp หาย (แคปชั่นตัดคำไม่ได้)"
VADPY="$HOME/.bizdrive/vad-env/bin/python3"
[ -x "$VADPY" ] && "$VADPY" -c "from silero_vad import load_silero_vad" 2>/dev/null \
  && ok "Silero VAD venv" || bad "VAD venv พัง — รัน install_vad.sh + pip install torchcodec"

echo "── เน็ต + API"
if curl -sm 8 https://api.elevenlabs.io >/dev/null 2>&1; then ok "อินเทอร์เน็ต"; else bad "เน็ตล่ม (ใช้ cache ได้: t09-show.sh ข้าม EL อัตโนมัติถ้า cache มี)"; fi
set -a; source "$REPO/templates/_shared/env/.env" 2>/dev/null; set +a
if [ -n "${ELEVENLABS_API_KEY:-}" ]; then
  SUB=$(curl -sm 10 -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user/subscription 2>/dev/null)
  LEFT=$(echo "$SUB" | python3 -c "import json,sys;d=json.load(sys.stdin);print(int(d.get('character_limit',0))-int(d.get('character_count',0)))" 2>/dev/null)
  if [ -n "$LEFT" ] && [ "$LEFT" -gt 3000 ] 2>/dev/null; then
    ok "ElevenLabs quota เหลือพอ"
  else
    # คีย์จำกัดสิทธิ์อ่านยอดไม่ได้ (missing user_read) — ทดสอบยิง STT จริง 0.5 วิแทน
    TW="$(mktemp -d)/t.wav"
    ffmpeg -y -v error -f lavfi -i "sine=frequency=440:duration=0.5" -ar 16000 -ac 1 "$TW" 2>/dev/null
    STT=$(curl -sm 30 -H "xi-api-key: $ELEVENLABS_API_KEY" \
      -F "file=@$TW" -F "model_id=scribe_v1" \
      https://api.elevenlabs.io/v1/speech-to-text 2>/dev/null)
    echo "$STT" | grep -q '"text"' && ok "ElevenLabs STT ยิงจริงผ่าน (คีย์จำกัดสิทธิ์ อ่านยอดตรงๆ ไม่ได้)" \
      || bad "ElevenLabs STT ยิงไม่ผ่าน: $(echo "$STT" | head -c 120)"
  fi
else bad "ELEVENLABS_API_KEY ว่าง"; fi
if [ -n "${OPENROUTER_API_KEY:-}" ]; then
  CRED=$(curl -sm 10 -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/credits 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin)['data'];print(round(d['total_credits']-d['total_usage'],2))" 2>/dev/null)
  [ -n "$CRED" ] && ok "OpenRouter เครดิตเหลือ \$$CRED" || bad "เช็คเครดิต OpenRouter ไม่ได้"
else echo "  ⚠️  OPENROUTER_API_KEY ว่าง (gen B-roll สดไม่ได้ — ใช้ตัวอบไว้ใน cache)"; fi

echo "── CapCut + draft"
[ -d "/Applications/CapCut.app" ] && ok "CapCut ติดตั้งอยู่" || bad "ไม่พบ CapCut.app"
pgrep -x CapCut >/dev/null && echo "  ⚠️  CapCut เปิดอยู่ — สคริปต์จะปิดให้เองตอนรัน" || ok "CapCut ปิดอยู่"
DROOT="$HOME/Movies/CapCut/User Data/Projects/com.lveditor.draft"
[ -f "$DROOT/root_meta_info.json" ] && ok "โฟลเดอร์ drafts ปกติ" || bad "หา drafts root ไม่เจอ"
if [ -n "$DRAFT" ]; then
  DRAFT="$DRAFT" DROOT="$DROOT" python3 - <<'PY' && ok "draft '$DRAFT' เป็น draft ดิบพร้อมตัด" || bad "draft '$DRAFT' ไม่ผ่าน (ไม่มี/ถูกตัดแล้ว/ไฟล์วิดีโอหาย)"
import json, os, sys
D = os.path.join(os.environ["DROOT"], os.environ["DRAFT"], "draft_info.json")
d = json.load(open(D))
vt = [t for t in d["tracks"] if t["type"] == "video"]
assert vt and all(len(t["segments"]) == 1 for t in vt)
assert all(os.path.isfile(v["path"]) for v in d["materials"]["videos"])
PY
fi

echo "── พื้นที่ดิสก์ + cache"
AVAIL=$(df -g "$HOME" | awk 'NR==2{print $4}')
[ "$AVAIL" -ge 5 ] 2>/dev/null && ok "ดิสก์เหลือ ${AVAIL}GB" || bad "ดิสก์เหลือ ${AVAIL}GB (<5GB เสี่ยง)"
CACHE="$HOME/.bizdrive/capcut-show-cache"
if [ -d "$CACHE" ]; then
  for c in "$CACHE"/*/; do
    n=$(basename "$c")
    have=""
    [ -f "$c/raw.json" ] && have="$have EL✓"
    [ -f "$c/vad.json" ] && have="$have VAD✓"
    [ -f "$c/x-captions.json" ] && have="$have captions✓"
    ls "$c"/broll-*.mp4 >/dev/null 2>&1 && have="$have broll✓"
    echo "  📦 cache[$n]:$have"
  done
else echo "  ⚠️  ยังไม่มี show-cache (รัน t09-show.sh 1 รอบเพื่ออุ่นเครื่อง)"; fi

echo
[ "$FAIL" -eq 0 ] && echo "🟢 พร้อมขึ้นเวที ($PASS checks)" || echo "🔴 มี $FAIL จุดต้องแก้ก่อนโชว์"
exit "$FAIL"
