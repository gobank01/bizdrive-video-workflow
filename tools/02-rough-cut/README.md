# Tool 02 — Rough Cut

คลิปดิบ 1 ไฟล์ → **rough cut ที่ดู/โพสต์ได้เลย** ในคำสั่งเดียว

"Rough cut" ที่นี่ = **ย่อให้กระชับ ไม่ใช่แค่ทำความสะอาด** — ตัดของเสีย + รีดน้ำ
(พูดวน/อธิบายเกิน/ออกทะเล) + ปรับระดับเสียงให้ฟังจบ **แต่ยังไม่ใส่
caption / template / B-roll / thumbnail** และคงสัดส่วน+fps เดิมของไฟล์ดิบ
(แนวตั้งเข้า→แนวตั้งออก) ดู [CONTEXT.md](../../CONTEXT.md) + [docs/adr/](../../docs/adr/)

## Quickstart

```bash
# โหมด Clean (default) — ตัดของเสีย+น้ำ, ไม่ตัดเนื้อหาทิ้ง, แถม "ตัดอะไรได้อีก"
bash tools/02-rough-cut/roughcut.sh raw-media/talk.mp4 my-talk \
  --context "พี่แบงค์อธิบายว่าทำไมต้องเริ่มลงมือก่อนพร้อม"

# โหมด Target — ขอความยาวเป๊ะ (ยอมตัดทั้งประเด็นทิ้งเพื่อเข้าเป้า)
bash tools/02-rough-cut/roughcut.sh raw-media/talk.mp4 my-talk --target 100
```

รันคำสั่งเดิมซ้ำเมื่อขึ้น `⏸ Editorial subagent needed` — script เดินต่อให้เอง

จบ → ได้ `staging/roughcut/<date>-<slug>/rough-cut.mp4` (+ `edl.json`)

## โหมด

| | ตัดของเสีย | รีดน้ำ | ตัดเนื้อหาทิ้ง |
|---|:---:|:---:|:---:|
| **Clean** (default) | ✓ | ✓ | ✗ (แค่ *แนะนำ*) |
| **`--target <sec>`** | ✓ | ✓ | ✓ (เข้าเป้า ±10%) |

- ไม่ใส่ `--context` ได้ — subagent จะ **เดาบริบทจาก transcript** ก่อนตัด
- `--target` เกิน 15% จากเป้า → script เตือนให้ rerun editorial เข้มขึ้น

## Pipeline (8 steps, resumable)

```
raw.mp4
 1 clean-copy + duration        5 apply rough EDL → cleaned-rough.mp4
 2 transcribe (ElevenLabs)      6 Silero VAD jump-cut EDL
 3 ⏸ Editorial subagent         7 apply jump-cut → jumpcut.mp4
 4 pad-bleed → safe EDL         8 loudnorm + mux → rough-cut.mp4 ✓
```

Step 3 เป็น pause จุดเดียว — spawn general-purpose subagent ด้วย
`editorial-prompt.txt` ที่ script เขียนให้ (slot เติมครบ) แล้ว rerun

## ไฟล์ใน folder นี้

| File | ทำอะไร |
|---|---|
| `roughcut.sh` | **Entry point** — orchestrator ครบ pipeline (resumable, standalone) |

ไม่มี script ของตัวเองนอกจากนี้ — เรียก
[`templates/_shared/scripts/clean-cut/*.py`](../../templates/_shared/scripts/clean-cut/)
(`editorial_pass.py`, `apply_edits.py`, `vad_detect.py`, `speech_to_edl.py`)
ตรงๆ ไม่ scaffold job/workspace/template ([docs/adr/0001](../../docs/adr/0001-tool02-bypasses-job-scaffold.md))

## ต่างจาก Tool 01 ยังไง

- **Tool 01** = คลิปยาว → shorts หลายตัว (split + v88 เต็ม + caption/template/render)
- **Tool 02** = คลิปเดี่ยว → rough cut **ตัวเดียว** หยุดที่ "ตัดกระชับ + เสียงดี"
  (ถ้าอยากได้ caption/template ค่อยเอา `rough-cut.mp4` ป้อนเข้า v88 ต่อเป็นคนละ tool)

## Requirements

ffmpeg · python3 · VAD env ที่ `~/.bizdrive/vad-env`
(ถ้ายังไม่มี: `bash templates/_shared/scripts/clean-cut/install_vad.sh`) ·
`templates/_shared/env/.env` ที่มี `ELEVENLABS_API_KEY`
