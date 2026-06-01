# Longform → Shorts Playbook

จาก **คลิปยาว 1 ไฟล์** (5-60 นาที) → **shorts หลายตัว** (60-90s แต่ละตัว) พร้อมโพสต์
ลง Reels / TikTok / Shorts — ในคำสั่งเดียว

## TL;DR

```bash
bash tools/01-longform-shorts/shipit.sh \
  --source "/path/to/long-video.mp4" \
  --slug my-clip-name \
  --topic "หนึ่งประโยคบอกว่าวิดีโอเรื่องอะไร"
```

จากนั้น **รันคำสั่งเดิมซ้ำ** ทุกครั้งที่ script ขึ้นว่า `⏸ subagent needed`
มันจะอ่านว่าทำถึงไหนแล้วและเดินต่อให้เอง — จนได้ `<clip>.mp4` + `<clip>.png`
ในโฟลเดอร์ `jobs/<date>-<slug>-clipNN/output/finals/`

---

## ก่อนเริ่ม — มีอะไรพร้อมแล้ว

- คลิปยาวเป็น `.mp4` (filename ภาษาไทยได้ — script จัดการ encoding เอง)
- ความยาวอย่างน้อย **3 นาที** (สั้นกว่านี้ใช้ `tools/new-job.sh` แทน — เป็น single-clip workflow)
- API key ใน `templates/_shared/env/.env` → `ELEVENLABS_API_KEY=...` (จ่าย ~$0.024 ต่อ 100s)

---

## Workflow เต็ม (3 phase, รัน 1 คำสั่ง)

```
source.mp4 (เช่น 19 นาที)
       │
bash tools/01-longform-shorts/shipit.sh --source X --slug Y --topic Z
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Phase 1 — prep                                            │
│   • copy ไป ASCII path (กัน Thai filename ทำ ffprobe พัง) │
│   • silencedetect (-30dB, gaps ≥ 0.8s)                    │
│   • ElevenLabs Scribe v2 → raw-elevenlabs.json            │
│   เวลา ~2-5 นาที                                            │
└──────────────────────────────────────────────────────────┘
       │
       ▼  ⏸ pause #1 — Shorts Finder subagent
       │   (Claude/Codex/คน อ่าน staging/.../PROMPT.md
       │    แล้ว spawn subagent → เขียน shorts.json)
       │
       ▼  เรียก `bash tools/01-longform-shorts/shipit.sh <staging-dir>` อีกครั้ง
       │
┌──────────────────────────────────────────────────────────┐
│ Phase 2 — split                                           │
│   • slice source ตาม shorts.json                          │
│   • 30 fps + GOP 30 normalize อัตโนมัติ                    │
│   • copy bg.png จาก template                              │
│   • slice transcript per child (skip Step 2 ต่อไป)        │
│   • scaffold N child jobs ใน jobs/                        │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Phase 3 — v88-clip × N (loop ทุก child)                   │
│   Step 1-2:  inspect + transcript setup (auto)            │
│   Step 3:    ⏸ Editorial subagent ⏸                       │
│   Step 4-9:  pad-bleed → rough cut → VAD → audio polish   │
│              → re-transcribe (auto)                       │
│   Step 10:   ⏸ Post-process subagent ⏸                    │
│   Step 11-16: build composition + lint + render + mix     │
│               + thumbnail (auto, ~5-10 นาที per clip)      │
└──────────────────────────────────────────────────────────┘
       │
       ▼
N × jobs/<date>-<slug>-clipNN/output/finals/<...>.mp4 + .png
```

แต่ละ clip มี **2 จุด pause** (Editorial + Post-process) — รวมทั้ง source
มี **`2N+1` pause** (Shorts Finder + 2 ต่อ clip)

---

## ตัวอย่างจริง — Wealth Story EP.65 (8 min source)

```bash
# 1. รันครั้งแรก
$ bash tools/01-longform-shorts/shipit.sh \
    --source "/Users/gobank01/Downloads/wealth-story.mp4" \
    --slug wealth-story-ep65 \
    --topic "แกะรอยมหาเศรษฐี เงินไปไหนปี 2026"
[Phase 1] prep ...
✓ raw-elevenlabs.json, silence.json
═══ Phase 1.5 ⏸ Shorts Finder subagent needed ═══
  Read this file and feed it to a subagent:
    staging/longform/2026-05-27-wealth-story-ep65/PROMPT.md

# 2. คุยกับ Claude: "run shorts finder on staging/longform/2026-05-27-wealth-story-ep65"
#    Claude spawn subagent → เขียน shorts.json

# 3. รันคำสั่งเดิมอีกครั้ง
$ bash tools/01-longform-shorts/shipit.sh staging/longform/2026-05-27-wealth-story-ep65
[Phase 2] split → 3 child jobs
[Phase 3] v88-clip × 3
  clip01: ⏸ editorial needed
  clip02: ⏸ editorial needed
  clip03: ⏸ editorial needed

# 4. คุยกับ Claude: "spawn editorial subagent for clip01/02/03" (3 ครั้ง)
#    Prompt อยู่ที่ jobs/<...>/workspace/assets/intermediates/v88-test/editorial-prompt.txt

# 5. รันคำสั่งเดิม → continue ถึง Step 10 → ⏸ post-process needed × 3
# 6. spawn post-process × 3
# 7. รันคำสั่งเดิม → finish Steps 11-16 → ได้ 3 final .mp4 พร้อม thumbnail
```

---

## รัน v88 บน 1 clip (ถ้ามี child job อยู่แล้ว)

ถ้าจะรัน v88 บน job ที่ scaffold แล้วโดยไม่ต้องผ่าน Phase 1/2:

```bash
bash tools/v88-clip.sh jobs/<date>-<slug>-clipNN
```

Logic เหมือนกับใน shipit — pause 2 จุด, รันซ้ำเพื่อ resume

---

## ตัวเลือกที่ใช้บ่อย

| Flag | ค่า default | เปลี่ยนเมื่อไหร่ |
|---|---|---|
| `--template NN` (split.sh / shipit.sh) | ตามที่ Shorts Finder แนะ | ถ้า source เป็น single-camera และ subagent ออก T01/T05 (ที่ต้องการ top.mp4) — บังคับเป็น T02 หรือ T04 |
| `--ranks 1,3,5` (split.sh) | ทุก rank | ถ้าอยากตัดเฉพาะบาง clip |
| `--max N` (split.sh) | ไม่ cap | จำกัดจำนวน clip |
| `--bgm <id>` (v88-clip.sh) | `mixkit-720-new-bass-01` | เลือก BGM อื่นจาก `templates/_shared/bgm/stock/mixkit/` |
| `--main "X" --hero "Y" --sub "Z"` (v88-clip.sh) | auto-split topic | คุม thumbnail เอง 3 บรรทัด |
| `--caption-offset-ms N` (v88-clip.sh) | `120` | ปรับ caption timing (locked default — อย่าเปลี่ยนนอกจาก clip นี้ๆ ต่างจริง) |
| `--skip-thumbnail` (v88-clip.sh) | off | ข้าม thumbnail ทำ |

---

## Subagent — ทำยังไง

ทุกครั้งที่ script pause มัน **เขียน prompt file พร้อมใช้** ไว้แล้ว
ไม่ต้องกรอก slot เอง — แค่บอก Claude/agent ตัวเดิม

**Shorts Finder (Phase 1.5):**
```
"run shorts finder on staging/longform/<date>-<slug>"
```
Claude จะ:
- อ่าน `staging/.../PROMPT.md` (มี slot กรอกครบแล้ว)
- เรียก SUBAGENT_PROMPTS.md Section C (Shorts Finder)
- subagent เขียน `shorts.json`

**Editorial (Step 3, per clip):**
```
"run editorial subagent for jobs/<...>-clipNN"
```
Prompt อยู่ที่ `jobs/<...>/workspace/assets/intermediates/v88-test/editorial-prompt.txt`

**Post-process (Step 10, per clip):**
```
"run post-process subagent for jobs/<...>-clipNN"
```
Prompt อยู่ที่ `jobs/<...>/workspace/assets/intermediates/v88-test/post-process-prompt.txt`

(Subagent prompts ทุกตัว load-bearing — อย่าแก้ — เห็น `v88-subagent-prompts-immutable` memory rule)

---

## กฎที่ pipeline เคารพอัตโนมัติ

- **คลิป 60-90s** (`shorts-duration-rule`) — Shorts Finder ไม่ออก clip นอกช่วงนี้
- **Caption -120ms offset** (`caption-offset-120ms`) — fix ElevenLabs phrase-level lag
- **Thumbnail บังคับ on** (`always-build-thumbnail`) — ยกเว้น Job Spec ปิด
- **30 fps + GOP 30** — slice ทุก clip
- **Audio -16 LUFS / Peak -1.5 dBFS** — Step 8 polish chain

---

## Troubleshoot

| อาการ | สาเหตุ + แก้ |
|---|---|
| `UnicodeDecodeError` ตอน Phase 1 | ใช้ `tools/01-longform-shorts/prep.sh` ตรงๆ ไม่ผ่าน shipit — มันจะ copy เป็น ASCII path ก่อน (fix อยู่แล้ว 2026-05-27) |
| Render Phase 3 ขึ้น "sparse keyframes" warning | Cosmetic — ไม่ใช่ error; bottom_visual_master ใช้ -c copy หลัง apply_edits |
| Subagent ตัด tail ทิ้งจน clip < 60s | Editorial subagent ฉลาด — ถ้า tail เป็น verbatim duplicate ของ opening มันตัดออก แม้จะตก floor ของ shorts rule (case-by-case ship หรือไม่) |
| Caption ดู late / early เกินไป | Tune `--caption-offset-ms` (default 120) |
| T01/T05 (stacked) แต่มี source แค่ camera เดียว | ใช้ `--template 04` (fullscreen karaoke) หรือ `--template 02` (fullscreen burst) แทน |
| รันซ้ำกลัวลบของเก่า | ทุก step idempotent — script เช็คไฟล์ก่อนทำ ไม่ลบของเก่า |

---

## ไฟล์/Tool ที่เกี่ยวข้อง

- [`tools/01-longform-shorts/shipit.sh`](../../../tools/01-longform-shorts/shipit.sh) — orchestrator (entry point)
- [`tools/01-longform-shorts/prep.sh`](../../../tools/01-longform-shorts/prep.sh) — Phase 1
- [`tools/01-longform-shorts/split.sh`](../../../tools/01-longform-shorts/split.sh) — Phase 2
- [`tools/v88-clip.sh`](../../../tools/v88-clip.sh) — Phase 3 ต่อ 1 clip
- [`tools/01-longform-shorts/slice-transcript.py`](../../../tools/01-longform-shorts/slice-transcript.py) — helper slice transcript
- [`tools/01-longform-shorts/apply-caption-offset.py`](../../../tools/01-longform-shorts/apply-caption-offset.py) — caption -120ms shift
- [SUBAGENT_PROMPTS.md](SUBAGENT_PROMPTS.md) Section A/B/C — 3 prompts ที่ subagent ใช้

---

**Validated:** 2026-05-28 — รัน 3 clips จาก next-humans-finance (19-min source) + clip03 จาก wealth-story-ep65 (8-min source); pipeline ส่ง final.mp4 ทุกตัวสมบูรณ์ caption sync เป๊ะหลัง 120ms offset
