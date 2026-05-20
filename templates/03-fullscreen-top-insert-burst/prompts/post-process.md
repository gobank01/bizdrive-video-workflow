# Template 03 — Post-Process Subagent Slot Defaults

Fill these into [`templates/_shared/docs/SUBAGENT_PROMPTS.md`](../../_shared/docs/SUBAGENT_PROMPTS.md) Section B.

The caption post-process is identical to Template 01 / 02 — same particle-burst
caption system, same `captions-burst.html` sub-composition. Only the slot
values change per clip.

```text
Topic (default):
  คลิป BIZDRIVE — talking-head เต็มจอ อธิบายหัวข้อเดียว (ปรับตามคลิปจริง)

Gold token policy:
  HIGH priority (always gold):
    - Numbers, monetary figures, durations, percentages
    - Brand/tech names (AI, ChatGPT, Claude, brand-specific terms)
    - Headline keywords ของหัวข้อคลิปนั้น
  MEDIUM (gold when emphasized):
    - Spelled-out numbers (แสน, ล้าน, ครึ่ง)
    - Payoff words (ฟรี, ประหยัด, กำไร, เร็วขึ้น)
  LOW (rarely gold):
    - Generic verbs / connectives / adjectives
  Target ratio: ~1:3 to 1:4 gold-to-white

Text fix priorities (post-process pass 1):
  1. Transliterated loanwords → Latin
  2. Spoken numbers → digits where it improves caption scannability
  3. Proper Thai abbreviations (สหรัฐ → สหรัฐฯ)
  4. Drop heavy hesitation fillers (เนี่ย, อ่า, ก็คือ when pure filler)
  5. Keep particles ครับ/นะ/ค่ะ; don't paraphrase — match what was said

Caption density:
  - ≤22 Thai characters per group
  - 1-3 tokens per group
  - Break at particle/conjunction boundaries for long phrases

Caption position note:
  bottom: 360px (lower third). On a full-screen face the captions sit over the
  chest area — fine, and clear of the upper-third B-roll insert card. The build
  script's SUB_TEMPLATE is shared with Template 01 / 02.
```
