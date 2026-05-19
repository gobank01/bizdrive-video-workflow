# v88 Subagent Prompts (verbatim)

Two AI-driven steps in the v88 pipeline. Both prompts are reproduced here EXACTLY as used to generate the locked reference clip. When porting, fill in the `{{...}}` slots — do not rewrite the body.

Both prompts assume:

- The subagent has filesystem read/write access to the project root
- The subagent will be evaluated on whether its output JSON validates and unblocks the downstream Python/Node steps
- The subagent does NOT see the chat history that produced these prompts

Tested AI agents: Claude Opus / Sonnet via Anthropic API and Claude Code Task tool. Other capable agents (GPT-4-class+, Gemini Pro+, Codex) should work — verify on the reference clip before relying on them for new work.

---

## Section A — Editorial Subagent (Step 3 of the playbook)

**Purpose:** Take a raw ElevenLabs transcript on the original (untrimmed) timeline and produce a frame-snapped EDL: which segments to keep, where to start, where to end, where false starts are.

**Input files the subagent must be able to read:**
- The raw ElevenLabs JSON (provide absolute path)
- The source media MP4 (for spot-checking)
- `scripts/clean-cut/references/editorial-rules.md` (provide absolute path)

**Output:** `edl-rough.json` at the absolute path you specify in the prompt.

### Prompt

```
You are doing a rough cut on a raw recording for the BIZDRIVE stacked-video workflow (v88, ii23-edit-kit integration).

## Inputs

- **Raw transcript (ElevenLabs Scribe v2, Thai)**: {{ABS_PATH_RAW_JSON}}
- **Source media** (raw, untrimmed): {{ABS_PATH_SOURCE_MP4}}
- **Source duration**: {{DURATION_SECONDS}}s (from ffprobe — note: raw.json.duration may be null; assume the ffprobe value is authoritative)
- **Topic / context**: {{ONE_SENTENCE_TOPIC_IN_TARGET_LANGUAGE}}
- **Speaker register**: {{formal | casual | hype | casual hype}}
- **Target language**: th
- **Target output duration**: ceiling ~{{CEILING_SECONDS}}s — treat as ceiling, not target. If meaningful content is shorter, that's fine.
- **Output**: {{ABS_PATH_EDL_ROUGH_JSON}}

## Read the editorial rules FIRST

Before producing the EDL, read this file end-to-end:
{{ABS_PATH_EDITORIAL_RULES_MD}}

The rules govern: last-take-wins, false starts, standalone fillers, mid-sentence stumbles, dead air, internal silences, padding, language-specific Thai filler vocab, the final-20% rule, and quality bar.

## Specific guidance for the clip

Looking at raw.json.words[], inspect the opening 30 seconds carefully. False-start patterns (a short attempt followed by silence then a restart) appear as:

  - 1-2 short word entries
  - then a 3-7 second silent gap
  - then a longer, more confident take

Apply editorial-rules.md "False starts" and "Last take wins": drop the failed attempt + the silent reset gap, keep the restart with ~200 ms head pad.

Also drop:
- Any leading non-speech tag like `[เสียงแจ้งเตือน]`, `[MUSIC]`, `[APPLAUSE]`, `[NOISE]`
- Any trailing non-speech tag like `[เสียงดนตรี]`, `[END]`

Scan the rest for: mid-sentence stumbles, repeated phrases, filler `เออ/อ่ะ/แบบ` (when used as hesitation), redundant meta-commentary. Note that Thai particles `ครับ/นะ/ค่ะ` and conjunctions `แต่/ก็/และ/หรือ` are KEPT.

For the final 20% (last ~20% of the clip), apply EXTRA scrutiny per editorial-rules.md "final-20%" rule — speakers fatigue and ramble there.

## Hard requirements

1. Every spoken segment that's kept must come from `raw.json.words[]` timing — don't invent timestamps.
2. `start_ms` and `end_ms` are integers (multiply seconds by 1000, round).
3. Segments must be chronological, non-overlapping.
4. Pad head ~200ms, tail 50-100ms — but NEVER let end_ms reach into the start of a DROPPED next word (pad-bleed will run after you, but be conservative).
5. Output strict JSON to the path above:

```json
{
  "segments": [{"start_ms": int, "end_ms": int}, ...],
  "language": "th",
  "register": "{{speaker_register}}",
  "kept_seconds": float,
  "original_seconds": {{DURATION_SECONDS}},
  "notes": [
    "Per-decision log: each cut or kept segment with one-line reason — false start, last-take-wins, filler drop, etc."
  ]
}
```

## After writing the file, report back (under 250 words)

1. The proposed trim_start_s and trim_end_s (decimal seconds).
2. How many segments survived, and total kept_seconds.
3. The 3-5 most impactful cuts (timestamp + reason).
4. Anything ambiguous you flagged but kept (low-confidence keeps).
5. Whether you saw any take-repeats in the body of the clip (not just the opening).
6. Whether the kept content reads as a complete coherent message.

Do not run pad-bleed yourself — that's a separate downstream step. Just produce {{edl-rough.json}} and the summary.
```

### Expected output shape

```json
{
  "segments": [
    {"start_ms": 24700, "end_ms": 101450},
    {"start_ms": 101550, "end_ms": 130270}
  ],
  "language": "th",
  "register": "casual hype",
  "kept_seconds": 105.47,
  "original_seconds": 130.517,
  "notes": [
    "Dropped 0.10-7.66s: non-speech tag [เสียงแจ้งเตือน] (notification SFX, not content).",
    "Dropped 7.78-13.58s 'ปันผลปีละ' and 13.68-17.88s 'มีเงินใช้เดือนละ': FALSE START — speaker attempted the hook then abandoned it.",
    "Dropped 17.88-24.90s: 7-second silent reset gap between the abandoned attempt and the real take.",
    "..."
  ]
}
```

### Validating the output

- Every segment's `start_ms < end_ms`
- Segments are chronological and non-overlapping
- `kept_seconds = sum((end - start) / 1000)` matches reality
- `notes[]` has ≥ 1 entry per dropped region
- Run `npm run rough:cut:padbleed` next — if it reports `end-pad bleed issues found`, the subagent was too aggressive on tail pad; rerun with stricter tail guidance

---

## Section B — Post-process / Caption Subagent (Step 10 of the playbook)

**Purpose:** Take a transcript on the EDITED timeline and produce caption groups with text-fix (Latin loanwords, digits for numbers, brand spelling) and per-token gold annotations for particle-burst highlight.

**Input files the subagent must be able to read:**
- The raw ElevenLabs JSON of the polished audio (provide absolute path)
- The polished WAV (for spot-checking)
- `scripts/transcribe/references/post-process-protocol.md` (provide absolute path)

**Output:** `caption-groups.json` at the absolute path you specify in the prompt.

### Prompt

```
You are doing post-process #1 (text fix) AND caption segmentation for the BIZDRIVE stacked-video v88 pipeline.

## Goal

Take the ElevenLabs Scribe v2 raw transcript and produce a clean, BIZDRIVE-style caption groups JSON where every caption matches what's actually spoken, with timing taken from the real ElevenLabs word boundaries (not interpolated/shifted).

## Inputs

- **Raw transcript (v88 edited timeline, polished audio):** {{ABS_PATH_RAW_EDITED_TIMELINE_JSON}}
- **Source audio:** {{ABS_PATH_POLISHED_WAV}}
- **Video duration (caption end must fit here):** {{DURATION_SECONDS}}s
- **Post-process protocol:** {{ABS_PATH_POST_PROCESS_PROTOCOL_MD}} — read end-to-end before writing.
- **Topic:** {{ONE_TO_TWO_SENTENCE_TOPIC_IN_TARGET_LANGUAGE}}
- **Reference for highlight style (do NOT copy text — only learn what kinds of tokens deserve gold):** {{OPTIONAL_PRIOR_GOLD_TASTE}}

## Output

Write to: {{ABS_PATH_CAPTION_GROUPS_JSON}}

Schema:

```json
{
  "duration": {{DURATION_SECONDS}},
  "language": "th",
  "source_provider": "elevenlabs",
  "post_processed_at": "<ISO 8601>",
  "groups": [
    {
      "start": <float, seconds from raw word>,
      "end":   <float, seconds — at most the next group's start, capped to duration>,
      "tokens": [
        {"text": "ปีละ",     "gold": false},
        {"text": "100,000",  "gold": true},
        {"text": "บาท",      "gold": true}
      ]
    },
    ...
  ],
  "notes": [
    "one line per non-trivial decision: text fix, regroup, gold pick, ambiguous spelling"
  ]
}
```

Rules:

1. **Source the timing from raw.words[].** Find each token's `start` and `end` in the raw transcript; never invent timestamps. When you merge words, group's `start` = first word's start; group's `end` = last word's end (extended up to the next group's start minus a 50-100 ms safety gap).
2. **Caption sizing:** Each group should read in ~1-3 seconds and display roughly 1-3 tokens at a glance. Aim for ≤22 visible Thai characters per group when rendered (the renderer wraps if too long, but tight cues feel kinetic). Never split mid-word.
3. **Particle/conjunction-aware split.** Prefer breaks at ครับ / นะ / แต่ / ก็ / และ / ที่ / หรือ / เพราะ / แล้ว boundaries when a phrase is long.
4. **Text fix (post-process #1):**
   - Transliterated loanwords → Latin: e.g. จีพียู→GPU, เอไอ→AI, เคิร์เซอร์→Cursor, คล็อด→Claude, เอ็นวิเดีย→NVIDIA, โอเพ่นเอไอ→OpenAI. The raw may already have `AI`, `prompt`, `S&P 500` in Latin — confirm they stay Latin.
   - Numbers in speech → digits where it improves caption scannability: "หนึ่งแสน"→"100,000" (and pair with "บาท"); "ยี่สิบปีสามสิบปี"→"20-30 ปี"; "หลายล้านบาท"→"หลายล้าน บาท" or "หลายล้าน".
   - "หุ้นสหรัฐ" → "หุ้นสหรัฐฯ" (proper Thai abbreviation).
   - Drop standalone fillers (เออ / อ่ะ / อืม) if any appear. Keep particles: ครับ, นะ, ค่ะ.
   - Light tightening of spoken-only words like "เนี่ย", "นะครับเนี่ย" → keep the message and one natural particle (e.g. "นะครับ"). Don't paraphrase aggressively — every caption must reflect what was actually said.
5. **Gold token policy:** mark `gold: true` on tokens that are numbers, monetary figures, durations, brand/tech names, and the headline tickers (S&P 500, AI). Avoid marking generic words gold. A 1:4 gold-to-white ratio is the ballpark — don't drastically over- or under-shoot.
6. **No empty groups, no overlapping groups, chronological order.**
7. **Every spoken word in raw.text must be represented across some group** (either kept as a token or compressed into a neighbouring token with a `notes[]` entry).
8. **The last group's `end` ≤ {{DURATION_SECONDS}}.** If raw word end exceeds this, clip to duration.

## After writing the file, report back (under 300 words)

1. Number of groups produced + number of gold tokens.
2. The 5 most impactful text fixes (raw → fixed).
3. Any merged/split decisions that changed group counts vs the natural raw word grouping.
4. Anything ambiguous you flagged (with timestamp + reason).
5. The first 3 groups (timestamps + tokens + gold) so I can sanity check the format.

Do not modify the raw transcript file. Write only {{caption-groups.json}} and return the summary.
```

### Expected output shape

```json
{
  "duration": 103.561333,
  "language": "th",
  "source_provider": "elevenlabs",
  "post_processed_at": "2026-05-19T22:55:00",
  "groups": [
    {
      "start": 1.86,
      "end": 3.4,
      "tokens": [
        { "text": "ปีละ", "gold": false },
        { "text": "100,000", "gold": true },
        { "text": "บาท", "gold": true }
      ]
    }
  ],
  "notes": [
    "Replaced spoken 'หนึ่งแสนบาท' with '100,000 บาท' — first numeric headline.",
    "Marked 'AI' gold every occurrence (5x).",
    "..."
  ]
}
```

### Validating the output

- `python3 scripts/build-burst-captions.py` runs without error (reads this JSON)
- Run sanity check:
  ```bash
  python3 -c "
  import json
  d = json.load(open('assets/<JOB>/transcript/caption-groups.json'))
  g = d['groups']
  print('groups:', len(g))
  print('gold:', sum(1 for x in g for t in x['tokens'] if t.get('gold')))
  print('overlaps:', sum(1 for i in range(1,len(g)) if g[i]['start'] < g[i-1]['end']))
  print('last end:', g[-1]['end'], '<=', d['duration'])
  "
  ```
- Acceptable: `overlaps == 0`, `last_end ≤ duration`, gold count ratio 1:3 to 1:5

---

## Section C — Why these prompts have to be long

Both prompts feel verbose, but every clause is load-bearing:

| Clause | Why it's there |
|--------|----------------|
| "Read editorial-rules.md FIRST" | Skipping this produces generic cuts that don't respect last-take-wins or Thai particles. |
| "Don't invent timestamps" | Without this, agents will round/snap and lose precision. |
| "Pad head ~200 ms, tail 50-100 ms" | Smaller numbers cut into words; larger numbers bleed into dropped takes. This is the empirical sweet spot. |
| "Pad-bleed will run after you, but be conservative" | Agents otherwise pad maximally on the assumption pad-bleed will fix it. Output then fails pad-bleed too often. |
| "Restore Latin for loanwords (with examples)" | Agents otherwise transliterate AI / GPU consistently — wrong for Thai audience reading Latin brands. |
| "Particles ครับ/นะ/ค่ะ are KEPT" | Without this, agents drop them as if they were English fillers. |
| "Notes per non-trivial decision" | Notes are the audit trail when the next human asks "why did you drop X?". |
| "Aim for ≤22 visible Thai characters" | Without a cap, agents produce 60-char captions that wrap and look broken. |
| "Every spoken word must be represented" | Without this, agents silently drop words they couldn't fit. |

When porting the workflow, treat both prompts as immutable. Tune the `{{...}}` slots, not the surrounding rules.
