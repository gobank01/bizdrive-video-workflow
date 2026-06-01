# Tool 01 — Longform → Shorts

จากคลิปยาว 1 ไฟล์ (5-60 นาที) → shorts หลายตัว (60-90s) พร้อมโพสต์ — รันคำสั่งเดียว

## Quickstart

```bash
bash tools/01-longform-shorts/shipit.sh \
  --source "/path/to/long-video.mp4" \
  --slug my-clip \
  --topic "หนึ่งประโยคบอกว่าวิดีโอเรื่องอะไร"
```

รันคำสั่งเดิมซ้ำทุกครั้งที่ขึ้น `⏸ subagent needed` — script จะเดินต่อให้เอง

จบ → ได้ N ไฟล์ที่ `jobs/<date>-<slug>-clipNN/output/finals/<...>.mp4` (+ `.png` thumbnail)

## ไฟล์ใน folder นี้

| File | ทำอะไร |
|---|---|
| `shipit.sh` | **Entry point** — orchestrator ครบทั้ง pipeline (resumable) |
| `prep.sh` | Phase 1 — copy source ASCII + silence detect + ElevenLabs transcribe |
| `split.sh` | Phase 2 — slice video ตาม shorts.json + scaffold child jobs |
| `slice-transcript.py` | Helper — slice ElevenLabs JSON ตาม [start, end] + rebase timestamps |
| `apply-caption-offset.py` | Helper — shift caption timing -120ms (ใช้ใน Step 11 ของ v88-clip.sh) |

## Phase 3 (v88) ใช้ tool ภายนอก

`shipit.sh` loop เรียก [`tools/v88-clip.sh`](../v88-clip.sh) บนแต่ละ child job  
(v88-clip.sh เก็บไว้นอก folder นี้เพราะใช้กับ single-job v88 ทั่วไปได้ ไม่ใช่แค่ longform child)

## เอกสารเต็ม

- [LONGFORM_PLAYBOOK.md](../../templates/_shared/docs/LONGFORM_PLAYBOOK.md) — user playbook (commands + troubleshoot)
- [SUBAGENT_PROMPTS.md](../../templates/_shared/docs/SUBAGENT_PROMPTS.md) Section C — Shorts Finder prompt (load-bearing)
- [V88_PLAYBOOK.md](../../templates/_shared/docs/V88_PLAYBOOK.md) — 16-step pipeline reference

## Validated

2026-05-28 — pipeline ส่ง final.mp4 สมบูรณ์บน:
- `wealth-story-ep65` (8-min source → 3 clips)
- `next-humans-finance` (19-min source → 5 clips, ส่งแล้ว 3)
