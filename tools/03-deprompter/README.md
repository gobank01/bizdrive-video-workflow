# Tool 03 — De-prompter · ลบเสียง "คนบอกบท" ออกจากคลิปถ่ายแบบพูดตาม

**คลิปดิบเข้า → คลิปที่เหลือแต่เสียง talent ออก (1 คำสั่ง).** entry: `deprompt.sh`
(เครื่องยนต์คือ `deprompter.py`). น้องของ Tool 01 (longform→shorts) และ Tool 02 (rough-cut).

```bash
bash tools/03-deprompter/deprompt.sh <raw.mp4> [slug] [--punch <n>|--no-punch] [--talent <id>]
# ผลออกที่ staging/deprompter/<DATE>-<SLUG>/talent-only.mp4 (+ edl.json, report.json)
```

## ปัญหาที่แก้
ถ่ายคลิปแบบ **พูดตาม (repeat-after)**: มีคนนอกกล้องอ่านบทให้ฟัง เสียงคนอ่านเข้าไมค์
กล้องด้วย แล้วคนหน้ากล้อง (talent) พูดตาม → เสียงดิบ = เสียงคนบอกบท + เสียง talent
สลับกันไปมา (ปกติไม่พูดทับกัน)

ถ้ายัดเข้า v88 ตรงๆ จะพังเงียบ: transcribe ติดทั้งสองเสียง, caption ขึ้นซ้ำทุกประโยค,
cut dead air ไม่รู้ว่าเสียงคนบอกบทคือส่วนที่ต้องทิ้ง

## วิธีที่ใช้ (พิสูจน์แล้วกับคลิปจริง)
1. **ElevenLabs Scribe v2 + `diarize=true, num_speakers=2`** → ได้ `speaker_id` ราย
   คำ (ของที่ pipeline เราใช้อยู่แล้ว แค่เปิดสวิตช์)
2. **เลือก talent อัตโนมัติ แบบไม่อิงเพศ:** talent = คนที่ในแต่ละคู่ A→B พูด **ทีหลัง**
   (คนพูดตาม) บ่อยสุด + มี airtime รวมเยอะสุด
3. สร้าง **keep-EDL เฉพาะช่วง talent** (ฟอร์แมต v88: `{"segments":[{"start_ms","end_ms"}]}`)
   พร้อม pad ±0.12/0.20s และ clamp ไม่ให้ล้ำเข้าช่วงคนบอกบท
4. ป้อน EDL เข้า `templates/_shared/scripts/clean-cut/apply_edits.py` (หรือใช้ `--apply`
   ให้ตัดด้วย ffmpeg เลย)

### ทำไมคลิปทั่วไปของเราถึงง่าย
คนบอกบทกับ talent มัก**คนละเพศ/คนละเสียง** → diarization แยกได้เป๊ะ ไม่สลับ
(เคสที่ยากคือ 2 คนเพศเดียวกันเสียงเหมือนกัน — ดูหัวข้อถัดไป)

## ตัวกันพลาด (สำคัญ — กันตัดมั่ว)
ถ้า diarizer เจอ **speaker เดียว** แต่ transcript มี **ประโยคซ้ำติดกัน** (ตรวจจาก
ช่องว่างจังหวะพูด ไม่อิง speaker) แปลว่าสองเสียงเหมือนกันจนแยกไม่ออก →
**tool จะไม่ตัด** และคืน `status: AMBIGUOUS` (exit 2) พร้อมบอกทางแก้:
- (a) อัดเสียง talent สะอาด 5–10 วิ เป็น reference แล้วใช้ voice-fingerprint (Resemblyzer/ECAPA)
- (b) ใช้ lip-sync / active-speaker detection (LR-ASD, TalkNet) — จับว่า "ปากในจอขยับตรงเสียงไหม"
- (c) ตัดมือ

> หมายเหตุ: (a)/(b) ยังไม่ได้ทำในสคริปต์นี้ — เป็น roadmap สำหรับเคสเพศเดียวกัน
> เมื่อมีคลิปตัวอย่างจริงค่อยต่อ

## วิธีใช้ — ทางหลัก (entry script, จัดการ env + staging + cache ให้)
```bash
# ดีฟอลต์: hard cut + เสียงต่อเนื่อง + punch-in 0.12 → staging/deprompter/<DATE>-<SLUG>/talent-only.mp4
bash tools/03-deprompter/deprompt.sh raw-media/talk.mp4

bash tools/03-deprompter/deprompt.sh raw-media/talk.mp4 bank-ai --punch 0.15   # ซูมแรงขึ้น
bash tools/03-deprompter/deprompt.sh raw-media/talk.mp4 --no-punch             # ตัดชนล้วน
bash tools/03-deprompter/deprompt.sh raw-media/talk.mp4 --talent speaker_0     # บังคับ speaker
bash tools/03-deprompter/deprompt.sh raw-media/talk.mp4 --fresh                # เรียก API ใหม่ (ไม่ใช้ cache)
```
re-run ซ้ำ: ใช้ diarization ที่ cache ไว้ (`diarization.json`) ไม่เสียค่า API อีก เว้นใส่ `--fresh`.

## วิธีใช้ — เรียกเครื่องยนต์ตรงๆ (advanced)
```bash
cd templates/_shared/env && set -a && source ./.env && set +a && cd -   # ต้องมี ELEVENLABS_API_KEY
python3 tools/03-deprompter/deprompter.py INPUT.mp4 --out-edl /tmp/edl.json --report /tmp/report.json   # ดูผล ยังไม่ตัด
python3 tools/03-deprompter/deprompter.py INPUT.mp4 --apply OUT.mp4 --punch 0.12                         # ตัด + punch
```

ฟลายต์สำคัญ (deprompter.py): `--lang tha`, `--num-speakers 2`, `--pad-l/--pad-r`,
`--punch 0.12` (สลับซูม fake-2nd-cam, 0=ปิด), `--diar-json`/`--save-diar` (cache),
`--xfade` (เปิด crossfade — **ไม่แนะนำ** ดูด้านล่าง)

## รอยต่อ: ทำไม "ตัดชน" ถึงถูก ไม่ใช่ "ละลาย"
คลิปพูดตามมีท่าต่างกันมากในแต่ละช่วง (หลับ↔ลืมตา, มือขึ้น↔ลง). dissolve/crossfade คือ
**alpha-blend = เบลนด์ 2 ภาพทับกัน** → โชว์ 2 ท่าซ้อนกัน = ภาพซ้อน/ลายตา. ยิ่ง fade ยาว
ยิ่งซ้อนหนัก แก้ไม่ได้ในทางคณิตศาสตร์ (Premiere Morph Cut / Resolve Smooth Cut คู่มือเอง
ก็บอกว่าใช้ได้เฉพาะตอนท่าเปลี่ยนน้อย). วิธีถูกคือ **ทำให้รอยตัดดูตั้งใจ** ไม่ใช่ทำให้นุ่ม:

1. **Hard cut + เสียงต่อเนื่อง** (ดีฟอลต์) — ตัดชนภาพ + แต่ละช่วง fade เสียง 15ms กัน
   เสียงป๊อก (ไม่ overlap → เสียง=ภาพ ยาวเท่ากัน ไม่หลุดซิงค์)
2. **Punch-in สลับซูม** (`--punch`) — รอยตัดอ่านเป็น "เปลี่ยนมุม" (กฎ 30 องศา). **เบคใน
   ffmpeg ที่ขั้นนี้** ห้ามไปสเกลเลเยอร์หน้าใน HyperFrames T01/T05 (AGENTS.md motion-safety
   ห้าม `npm run check:motion` จะ fail)
3. **B-roll/caption บัง** รอยต่อที่ท่าต่างเยอะสุด — มาตรฐานทอง (ทำตอนต่อ v88)
4. **ต้นทาง:** สั่ง talent กลับท่ากลางๆ (มือลง มองเลนส์) ก่อนพูดประโยคใหม่ → รอยตัดเล็กลงเอง

> `--xfade > 0` ยังเปิด crossfade ได้ (legacy) แต่จะ **ลายตา** กับคลิปท่าต่างเยอะ — อย่าใช้
> เป็นค่าเริ่มต้น. ถ้าจะใช้ flash ให้ใช้ `--transition fadeblack --xfade 0.10` เฉพาะจุดเปลี่ยนหัวข้อ

## ต่อเข้า v88 ตรงไหน
แทรกเป็น **step แรกสุด** ก่อน Step 2 (load transcript) ของ `v88-clip.sh`:

```
raw.mp4 ──> deprompter.py --apply ──> raw_clean.mp4 ──> (เข้า v88 ปกติ)
```

หลังจากนี้ทุก step เดิม (transcribe / editorial / VAD jump-cut / caption) ทำงานบน
เสียงสะอาดที่มีแต่ talent → ไม่ต้องแก้อย่างอื่น

## Job Spec (ข้อเสนอ)
เพิ่ม feature toggle เช่น `deprompter.on=true` ใน Template Manager Job Spec เพื่อสั่ง
ให้ pipeline รัน step นี้เฉพาะคลิปที่ถ่ายแบบพูดตาม
