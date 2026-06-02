# Template 05 — Post-Process Subagent Slot Defaults

Fill these into [`templates/_shared/docs/SUBAGENT_PROMPTS.md`](../../_shared/docs/SUBAGENT_PROMPTS.md) Section B.

Template 05 uses the **caption-highlight (BIZDRIVE Karaoke)** system —
`captions-highlight.html`, built by `scripts/build-highlight-captions.py`. The
`caption-groups.json` schema is the SAME one every template uses; only the
renderer differs, so a clip can be re-cut to Template 01 (particle-burst) from
the identical caption-groups.json without re-running this subagent.

```text
Topic (default):
  คลิป BIZDRIVE ของพี่แบงค์ — talking-head + screen recording, ภาษาไทย,
  direct-response สไตล์เจ้าของธุรกิจ, อาจมี loanword ไทย-อังกฤษผสม

Gold token policy:
  HIGH priority (always gold):
    - Numbers, monetary figures, durations, percentages
    - Brand/tech names (AI, ChatGPT, Claude, Cursor, Template, Workflow, brand terms)
    - Headline keywords ของหัวข้อคลิปนั้น
  MEDIUM (gold when emphasized):
    - Spelled-out numbers (แสน, ล้าน, ครึ่ง)
    - Payoff words (ฟรี, ประหยัด, กำไร, เร็วขึ้น)
  LOW (rarely gold):
    - Generic verbs / connectives / adjectives
  Target ratio: ~1:3 to 1:5 gold-to-white
  Gold tokens render as a GOLD box (vs red for normal) — keep them meaningful.

Text fix priorities (post-process pass 1):
  1. Transliterated loanwords → Latin (จีพียู→GPU, เอไอ→AI, เคิร์เซอร์→Cursor)
  2. Spoken numbers → digits where it improves caption scannability
  3. Proper Thai abbreviations (สหรัฐ → สหรัฐฯ)
  4. Drop heavy hesitation fillers (เนี่ย, อ่า, ก็คือ when pure filler)
  5. Keep particles ครับ/นะ/ค่ะ; don't paraphrase — match what was said

Caption density (karaoke):
  - ≤32 visible Thai characters per group
  - 1-3 tokens per group (each token = one karaoke box that sweeps)
  - Break at particle/conjunction boundaries for long phrases
  - No sub-0.4s lonely groups — merge a tiny token into a neighbour

Caption position note:
  bottom: 360px — sits in the band below the bottom face circle (stacked
  layout). build-highlight-captions.py is invoked with arg 4 = 360 for this
  template (Template 04 uses 330 because it is full-screen).
```
