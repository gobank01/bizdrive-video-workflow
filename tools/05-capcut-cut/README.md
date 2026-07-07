# Tool 05 — CapCut Pre-Cut (mini project / experimental)

**สองระดับ:** `capcut_cut.py` = ตัดอย่างเดียว (เร็ว ปลอดภัย) ·
`capcut_max.py` = โปรดักชั่นเต็ม T09-in-CapCut: jump cuts + punch-in keyframes +
แคปชั่นไทย pop-in (คำเน้นทอง+เงา) + hook/CTA (typewriter/slide-up) + effects
(zoom/shake/flash) + BGM + SFX + bg — สูตรที่ใช้จริง:

**ทางลัดคำสั่งเดียว (ใช้จริงบนเวทีได้):**

```bash
bash tools/05-capcut-cut/t09-show.sh <draft> "<hook>" [face-center] [ชื่อผลลัพธ์]
# ทำให้ครบ: หา media -> VAD ละเอียด -> EL transcribe -> prep_captions.py -> capcut_max.py
```

**เรียกเต็ม (คุมทุก option):**

```bash
python3 tools/05-capcut-cut/capcut_max.py <draft> \
  --edl <edl.json> --captions <caps.json> \
  --bgm templates/_shared/bgm/stock/mixkit/mixkit-1167-close-up.mp3 \
  --bg templates/09-split-vertical-burst/assets/bg.png \
  --sfx-dir templates/_shared/sfx \
  --broll "clip.mp4@4.5:4" \
  --layout t09 --face-center 0.545 --cap-size 19.5 \
  --hook "..." --cta "..." --name "ชื่อ draft"
```

- `--cap-size 19.5` = ค่าที่พี่แบงค์คาลิเบรตกับตาจริง (default แล้ว)
- `--layout t09` = กล้อง cover ครึ่งจอ + B-roll แทนที่เฉพาะจอบน (หน้าคนไม่โดนบัง)
- `--broll` gen ได้จาก `gen_broll.py --prompt "..." --output x.mp4`
  (OpenRouter seedance-1-5-pro, ~ไม่กี่บาท/คลิป 5s 720p, ธีมน้ำเงิน-ทองให้เข้า bg)
- media ทุกไฟล์ (bg/bgm/sfx/broll) ถูกก๊อปเข้า draft folder อัตโนมัติกัน sandbox;
  rebuild ทับชื่อเดิม reuse draft_id กัน CapCut แตกร่าง "(1)"

ให้ Claude ตัด dead air ใน draft CapCut ให้เสร็จ **ผู้ใช้แค่เปิด CapCut แล้วกด Export**
— ทางเลือกเทียบกับ v88 pipeline (v88 render เองจบ ไม่ต้องเปิดแอปตัดต่อ)

## Workflow

1. ผู้ใช้ลากคลิปดิบเข้า CapCut เป็น draft ใหม่ (วางเต็มเส้น ไม่ต้องตัดอะไร) แล้วปิดโปรเจค
2. รัน:
   ```bash
   # โหมด VAD (ตัด dead air อัตโนมัติ)
   python3 tools/05-capcut-cut/capcut_cut.py <ชื่อ-draft> [--media /path/ไฟล์.mp4] [--name "ชื่อใหม่"]

   # โหมด EDL (รับผลจาก editorial pass / เครื่องมืออื่นของ repo)
   python3 tools/05-capcut-cut/capcut_cut.py <ชื่อ-draft> --edl edl.json [--name "ชื่อใหม่"]
   ```
3. เปิด CapCut → เจอ draft ใหม่ "<ชื่อ> AI cut" ที่ตัดแล้ว → ตรวจ/แต่งต่อ → Export

## Editorial mode (rough cut ระดับ Tool 02 แต่แก้มือได้ใน CapCut)

Claude เป็น orchestrator เหมือน v88 (ไม่มี runner script — 5 ขั้น):

1. VAD: ใช้โหมด VAD ข้างบนดูก่อนว่า dead air เยอะไหม
2. Transcribe (ElevenLabs Scribe v2 เท่านั้น — กฎ repo):
   `python3 templates/_shared/scripts/transcribe/transcribe.py <media> --provider elevenlabs --lang th --output raw.json`
3. Spawn editorial subagent ด้วย prompt template จาก `tools/v88-clip.sh` Step 3
   (เติม slot: transcript/media/duration/topic/output) → ได้ `edl-rough.json`
4. Validate + refine:
   `python3 templates/_shared/scripts/clean-cut/editorial_pass.py edl-rough.json raw.json -o edl-safe.json`
   `python3 templates/_shared/scripts/clean-cut/refine_edl.py <media> edl-safe.json -o edl-final.json`
5. `python3 tools/05-capcut-cut/capcut_cut.py <draft> --edl edl-final.json --name "<ชื่อ> AI editorial"`

## มันทำอะไร

- แกะเสียงจากคลิป → Silero VAD (venv เดียวกับ v88, ค่า default talking-head:
  `--min-silence-ms 300 --pad-ms 200`) → ได้ช่วงพูด
- **copy** โฟลเดอร์ draft เป็น "<ชื่อ> AI cut" — **ไม่แตะต้นฉบับเด็ดขาด** (rerun ทับได้เฉพาะสำเนาของตัวเอง)
- เขียน segments ใหม่ (source_timerange ข้ามช่วงเงียบ, target ต่อชนกัน, clone
  `extra_material_refs` ต่อ segment) ลง **ทุกสำเนา** timeline (draft_info.json + .bak +
  template*.tmp + ชุดเดียวกันใน `Timelines/<id>/`) — CapCut 8.7+ เก็บซ้ำหลายไฟล์
- อัปเดต draft_meta_info + ลงทะเบียน root_meta_info.json + สร้าง cover

## ข้อจำกัด (by design)

- macOS CapCut international เท่านั้น (drafts ที่
  `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`, ไฟล์ `draft_info.json`
  เป็น plaintext JSON — ยืนยันกับ CapCut 9.0-beta 2026-07-06; JianYing จีน 6+ เข้ารหัส ใช้ไม่ได้)
- รับเฉพาะ draft ดิบ: 1 video track, 1 segment เต็มเส้น, ไม่มี track อื่น — เกินนั้น refuse
- คลิปยาวมาก: ใช้ `--merge-gap-ms 300+` กัน segment เกิน ~500 ชิ้น (CapCut เริ่มหน่วง)
- ควรปิด CapCut ก่อนรัน (เปิดอยู่ก็ใช้ได้เพราะเราสร้างโฟลเดอร์ใหม่ แต่ต้องปิด-เปิดแอปให้ draft โผล่)

## บทเรียนจากการเทส (สำคัญ)

- **สำเนาต้อง regenerate id ภายในทุกตัว** (timeline id ใน draft_info.json +
  project id ใน Timelines/project.json + rename โฟลเดอร์ Timelines/<id>/) —
  ถ้าแชร์ id กับต้นฉบับ CapCut จะมองเป็น draft ซ้ำแล้ว **auto-rename ต้นฉบับ**
  เป็น "(1)" ตอนเปิดแอป (เจอจริง 2026-07-07: "0706" → "0706(1)"; เนื้อในไม่เสียหาย)
  — สคริปต์เวอร์ชันปัจจุบันจัดการให้แล้ว
- CapCut ตอนเปิดแอปจะ rewrite draft_meta_info.json ของ draft ที่ scan เจอ
  ด้วย draft_id ของมันเอง — ไม่เป็นไร อย่าไปยึด id ที่เราใส่

## เทส

- 2026-07-06: `0706 AI cut` (VAD เล็มหัว 1.8s/ท้าย 1.5s) — CapCut รับเข้าระบบ ✅
- 2026-07-07: `0706 AI 3seg` (EDL 3 segments — พิสูจน์ multi-segment + clone
  extra_material_refs ×3, refs ครบ ไม่มีหลุด) + `0706 AI editorial`
  (สาย v88 เต็ม: EL Scribe → editorial subagent → editorial_pass → refine_edl →
  draft; คลิป 3C เทคเดียวสะอาด ตัดแค่หัว 1.7s) — ทั้ง 4 draft register นิ่ง
  ผ่าน restart, ไม่มี rename เพิ่ม ✅

อ้างอิงวงการ: pyCapCut, VectCutAPI, capcut-cli (docs/draft-schema ละเอียดสุด)
