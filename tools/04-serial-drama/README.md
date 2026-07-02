# Tool 04 — Serial Drama (หนี้ 2 ล้าน กับ AI หนึ่งตัว)

ผลิตละครสั้น AI 30 วิ/ตอน เนื้อเรื่องต่อกัน (1080×1920, ละครเสียงบรรยาย ไม่มี lip-sync)
ซีรีส์ไบเบิล + กฎ continuity ทั้งหมดอยู่ใน [bible/SERIES_BIBLE.md](bible/SERIES_BIBLE.md) — **อ่านก่อนทำทุกตอน**

## ไฟล์

| ไฟล์ | หน้าที่ |
|---|---|
| `gen-shots.js` | gen ช็อตจาก `shots.json` (โคลน generate-openrouter-broll.js, 9:16, ฉีด bible blocks อัตโนมัติ) |
| `tts-thai.py` | เสียงบรรยายไทย ElevenLabs — **eleven_v3 เท่านั้น** (โมเดลเดียวที่พูดไทยได้บนบัญชีนี้) |
| `stitch.py` | ต่อ takes → visual base 1080×1920/30fps + grade เดียวกันทุกช็อต (hard cut เท่านั้น) |
| `polish-audio.sh` | chain เสียง v88 Step 8 (คัดจาก tools/v88-clip.sh บรรทัด 292-340 — ถ้า v88 แก้ ต้อง sync) |
| `bible/` | characters.json (frozen blocks) · season-state.json · voice.json (เสียงล็อก) · SERIES_BIBLE.md |
| `episodes/ep-NN/` | shots.json + vo-script.txt + chat-timeline.json ต่อตอน |

## Flow ต่อตอน

```bash
set -a; source ../../templates/_shared/env/.env; set +a   # ทุก script ต้องการ key
node gen-shots.js episodes/ep-NN/shots.json               # 1) gen รอบแรก 1 take/ช็อต
#    → continuity QA (checklist ใน bible) → เพิ่ม takes เฉพาะช็อตที่ไม่ผ่าน → เลือก take ใส่ shots.json
python3 stitch.py episodes/ep-NN/shots.json -o .../visual_base.mp4   # 2) ต่อ + grade
python3 tts-thai.py episodes/ep-NN/vo-script.txt -o .../vo_raw.wav   # 3) เสียงบรรยาย
bash polish-audio.sh .../vo_raw.wav .../speech_polished.wav          # 4) polish
# 5) transcribe (Scribe v2 โดยตรง ห้าม npm wrapper) → captions (-120ms offset)
# 6) composition: captions + LINE chat bubbles + EP badge + การ์ดบทเรียน → render
# 7) mix-sfx.py (BGM mixkit-770, gain 9-10) → thumbnail → DELIVERY_LOG → clean-job.sh
```

ขั้น 5-7 ใช้ workspace จาก `bash tools/new-job.sh 02 drama-epNN` (T02 fullscreen)
**ห้ามรัน v88-clip.sh** — มันบังคับ talking-head steps 1-7 ที่ซีรีส์นี้ไม่มี

## กติกาที่ห้ามลืม

- ห้ามพิมพ์ข้อความตัวละคร/ฉาก/สไตล์ในมือ — ใช้ `[BLOCK]` จาก bible เสมอ (gen-shots.js จะ error ถ้า block ไม่มีจริง)
- take budget: ช็อต object/ฉาก ×2, ช็อตมีคน ×3 — gen รอบแรก 1 take แล้ว re-roll เฉพาะที่ไม่ผ่าน QA
- ช็อตที่ผ่าน QA และ generic พอ → ลงทะเบียน anchor ใน `templates/_shared/broll/index.json` (คีย์เวิร์ด `nee2m-*`) ใช้ซ้ำฟรี
- เสียง George (bible/voice.json) = หน้าของซีรีส์ เปลี่ยนไม่ได้ · อาร์ไคฟ์ WAV ทุกตอน
- v3 รองรับ audio tags `[whispers]` `[sighs]` ใน vo-script — ใช้เท่าที่จำเป็น
- spike 2026-06-11: native 9:16 ผ่าน (720×1280 → lanczos upscale), ช็อตคนจากด้านหลังผ่าน seedance-1-5-pro รอบแรก, miss rate 0/3

## ต้นทุน/ตอน (อ้างอิง)

gen ~10-14 takes ≈ $0.20-0.28 · TTS v3 ~70 คำ ≈ $0.10 · Scribe ≈ $0.01 → **รวม ~$0.30-0.40** (เพดาน $1.00)
