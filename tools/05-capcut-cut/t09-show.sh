#!/usr/bin/env bash
# คำสั่งเดียว: draft CapCut ดิบ -> T09 จัดเต็ม (ตัด+แคปชั่น+effect+BGM+SFX+bg+endcard)
# Usage: bash tools/05-capcut-cut/t09-show.sh <draft> "<hook>" [face-center] [ชื่อผลลัพธ์] [args เพิ่มของ capcut_max...]
# Cache: ~/.bizdrive/capcut-show-cache/<draft>/ — ขั้นที่มีผลแล้วข้ามอัตโนมัติ
#        (เดโม่สดปลอดเน็ตล่ม/EL quota) ล้างด้วย FORCE=1
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
DRAFT="$1"; HOOK="${2:-}"; FACE="${3:-0.5}"; NAME="${4:-$DRAFT AI show}"
shift $(( $# > 4 ? 4 : $# ))
EXTRA=("$@")
DROOT="$HOME/Movies/CapCut/User Data/Projects/com.lveditor.draft"
WORK="$HOME/.bizdrive/capcut-show-cache/$DRAFT"
mkdir -p "$WORK"
[ "${FORCE:-0}" = "1" ] && rm -f "$WORK"/a.wav "$WORK"/vad.json "$WORK"/raw.json "$WORK"/x-*.json

MEDIA=$(DROOT="$DROOT" DRAFT="$DRAFT" python3 - <<'PY'
import json, os
d = json.load(open(os.path.join(os.environ["DROOT"], os.environ["DRAFT"], "draft_info.json")))
vs = d["materials"]["videos"]
c = [v for v in vs if "bottom" in os.path.basename(v["path"]).lower()] \
    or [v for v in vs if v.get("has_audio")] or vs
print(c[0]["path"])
PY
)
echo "── media: $MEDIA"
[ -f "$WORK/a.wav" ]    || ffmpeg -y -v error -i "$MEDIA" -ac 1 -ar 16000 "$WORK/a.wav"
[ -f "$WORK/vad.json" ] || "$HOME/.bizdrive/vad-env/bin/python3" \
  "$REPO/templates/_shared/scripts/clean-cut/vad_detect.py" "$WORK/a.wav" \
  --min-silence-ms 150 --min-speech-ms 150 --pad-ms 100 --output "$WORK/vad.json"
if [ ! -f "$WORK/raw.json" ]; then
  set -a; source "$REPO/templates/_shared/env/.env"; set +a
  python3 "$REPO/templates/_shared/scripts/transcribe/transcribe.py" "$MEDIA" \
    --provider elevenlabs --lang th --output "$WORK/raw.json" >/dev/null
else echo "── transcribe: ใช้ cache"; fi
[ -f "$WORK/x-captions.json" ] || python3 "$REPO/tools/05-capcut-cut/prep_captions.py" \
  --transcript "$WORK/raw.json" --vad "$WORK/vad.json" --out-prefix "$WORK/x"
osascript -e 'tell application "CapCut" to quit' 2>/dev/null || true
for _ in $(seq 1 20); do pgrep -x CapCut >/dev/null || break; sleep 1; done
python3 "$REPO/tools/05-capcut-cut/capcut_max.py" "$DRAFT" \
  --edl "$WORK/x-edl.json" --captions "$WORK/x-captions.json" \
  --bgm "$REPO/templates/_shared/bgm/stock/mixkit/mixkit-1167-close-up.mp3" \
  --bg "$REPO/templates/09-split-vertical-burst/assets/bg.png" \
  --sfx-dir "$REPO/templates/_shared/sfx" \
  --layout t09 --face-center "$FACE" --endcard 3.2 \
  ${HOOK:+--hook "$HOOK"} --cta "ติดตามพี่แบงค์ BizDrive" \
  --name "$NAME" \
  ${EXTRA[@]+"${EXTRA[@]}"}
open -a CapCut
echo "── เปิด CapCut -> '$NAME' -> Export"
