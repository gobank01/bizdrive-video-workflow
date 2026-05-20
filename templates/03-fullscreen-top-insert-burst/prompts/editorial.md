# Template 03 — Editorial Subagent Slot Defaults

Fill these into [`templates/_shared/docs/SUBAGENT_PROMPTS.md`](../../_shared/docs/SUBAGENT_PROMPTS.md) Section A.

The editorial rough cut is identical to Template 01 / 02 — it operates on the
bottom (talking-head) audio. Template 03 has no top.mp4 to trim in parallel;
the EDL still drives the single video.

```text
Topic / context (default):
  คลิป BIZDRIVE — talking-head เต็มจอ, ภาษาไทย, สไตล์เจ้าของธุรกิจ/ผู้เชี่ยวชาญ
  อธิบายเรื่องเดียวจบ ไม่มี screen recording ประกอบ

Speaker register (default): casual hype
  - "โห", "บอกเลย", "นะครับ", จังหวะพูดเร็ว
  - มัก pause/reset ตอนเปิด hook

Target output duration (default ceiling): ~90s

Special opening pattern to look for:
  - Pre-roll recording-test chatter ("อันนี้อัดแล้วนะครับ", "ลองดูครับ", "ไป")
  - False start: ลอง hook → silence/reset → restart
  - editorial subagent ต้องตัด pre-roll + false start, เริ่มที่ content จริง

Filler vocabulary (ตัดเป็น standalone):
  เออ, อ่ะ, อืม, แบบ (hesitation), ก็คือ (filler usage)
  - particles ครับ/นะ/ค่ะ + conjunctions แต่/ก็/และ/หรือ KEEP เสมอ

Non-speech tags ที่ต้องตัด:
  [เสียงแจ้งเตือน], [เสียงดนตรี], [เสียงคลิกเมาส์], [MUSIC], [APPLAUSE], [NOISE]
```
