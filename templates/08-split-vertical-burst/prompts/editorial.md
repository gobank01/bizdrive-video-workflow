# Template 01 — Editorial Subagent Slot Defaults

Fill these into [`templates/_shared/docs/SUBAGENT_PROMPTS.md`](../../_shared/docs/SUBAGENT_PROMPTS.md) Section A when the clip uses Template 01 and has no clip-specific overrides.

```text
Topic / context (default):
  คลิป BIZDRIVE ของพี่แบงค์ — talking-head + screen recording, ภาษาไทย,
  enseigne direct-response สไตล์เจ้าของธุรกิจ, อาจมี loanwords ไทย-อังกฤษผสม
  (เช่น AI, GPU, prompt, S&P 500), ตัวเลขเรื่องเงิน/เวลา/ผลตอบแทน

Speaker register (default): casual hype
  - ใช้คำว่า "โห", "บอกเลย", "สุดๆ", "นะครับ" บ่อย
  - ลำดับ phrase สั้น + เร่งจังหวะ
  - การพูดมีจังหวะ pause/restart เมื่อเริ่ม hook

Target output duration (default ceiling): ~105s
  - ถ้าผู้ใช้ระบุ target อื่น ใช้ตามผู้ใช้
  - ห้ามยืดเกิน 120s เว้นแต่ผู้ใช้ override

Special opening pattern to look for:
  - พี่แบงค์ชอบลองเปิด hook 1 ครั้ง → silence/reset 3-7s → restart ด้วย wording ที่ดีกว่า
  - editorial subagent ต้องตัดความพยายามแรก + silent reset ออก เก็บแค่ restart ที่ smooth
  - hook ที่เก็บมักจะเปิดด้วย "มีเงินใช้..." / "ปีละ..." / "ผมจะบอกว่า..." / "พี่แบงค์..."

Filler vocabulary (ตัดเป็น standalone):
  เออ, อ่ะ, อืม, แบบ (เมื่อใช้เป็น hesitation)
  - particles ครับ/นะ/ค่ะ + conjunctions แต่/ก็/และ/หรือ KEEP เสมอ

Non-speech tags ที่ต้องตัด:
  [เสียงแจ้งเตือน], [เสียงดนตรี], [MUSIC], [APPLAUSE], [NOISE]
```
