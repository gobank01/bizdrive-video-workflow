# Template 01 — Post-Process Subagent Slot Defaults

Fill these into [`templates/_shared/docs/SUBAGENT_PROMPTS.md`](../../_shared/docs/SUBAGENT_PROMPTS.md) Section B when the clip uses Template 01.

```text
Topic (default):
  คลิป BIZDRIVE ของพี่แบงค์ — direct-response เจ้าของธุรกิจ พูดเรื่องการลงทุน /
  AI / passive income / S&P 500 / ปันผล / กองทุน / หุ้นอเมริกา

Gold token policy for Template 01:

  HIGH priority (always gold):
    - Numbers: 100,000 / 1,000,000 / 20-30 / 55 / etc.
    - Monetary: บาท ที่ตามหลังตัวเลข
    - Durations: ปีละ / เดือนละ / ปีนึง / X ปี
    - Brand/tech: AI / GPU / ChatGPT / Claude / Cursor / NVIDIA / OpenAI / Anthropic
    - Tickers: S&P 500 / NASDAQ / SET / NVDA / AAPL

  MEDIUM priority (gold when emphasized):
    - "ฟรี" / "ฟรีๆ"
    - Spelled-out numbers in Thai: แสน / หลายล้าน / ล้าน
    - Headline outcomes: ปันผล / กำไร / ปีละ X บาท

  LOW priority (rarely gold):
    - Generic verbs and connectives
    - คำสอนทั่วไป
    - Adjectives ที่ไม่ specific

Target ratio: ~1:3 to 1:5 gold-to-white tokens
Reference v88: 22 gold / 66 white = 1:3 ratio (slightly higher than average; OK for finance content)

Text fix priorities (post-process pass 1):
  1. Transliterated loanwords → Latin: จีพียู→GPU, เอไอ→AI, เคิร์เซอร์→Cursor, etc.
  2. Spoken numbers → digits: หนึ่งแสน→100,000, ยี่สิบปีสามสิบปี→20-30 ปี, ห้าสิบห้า→55
  3. หุ้นสหรัฐ → หุ้นสหรัฐฯ (proper Thai abbreviation)
  4. Drop เนี่ย / fillers when overused
  5. Keep ครับ/นะ/เลย particles
  6. Don't paraphrase — caption must match what was actually said

BIZDRIVE-specific spellings to watch:
  - prompt (keep Latin, never "พรอมป์ต์")
  - AI (keep Latin)
  - S&P 500 (keep as 2 tokens; gold both)
  - ChatGPT / Claude / Cursor (keep Latin)

Caption density:
  - ≤22 Thai characters per group (renderer wraps if longer but tight cues feel kinetic)
  - 1-3 tokens per group typical
  - Break at particle/conjunction boundaries (ครับ/นะ/และ/แต่/ที่/เพราะ/แล้ว) for long phrases
```
