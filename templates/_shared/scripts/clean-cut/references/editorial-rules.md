# Editorial rules — full ruleset for the LLM editorial pass

The subagent reads this file before producing an EDL from the formatted transcript. The rules are organized by what to cut, what to keep, and how to handle edge cases. Most of these come from comparing automated edits against user-corrected versions on real recordings, so each rule has a "why" tied to a real failure mode.

## Core principle

The final edit should read as if the speaker said everything correctly on the first try. The viewer should never realize there were retakes. Every cut should be invisible — if a cut feels like a "cut", it's wrong.

## Table of contents

1. [What to cut](#1-what-to-cut)
2. [What to keep](#2-what-to-keep)
3. [Padding and boundaries](#3-padding-and-boundaries)
4. [Language-specific rules](#4-language-specific-rules)
5. [The final 20% rule](#5-the-final-20-rule)
6. [Quality bar](#6-quality-bar)
7. [Examples](#7-examples)

---

## 1. What to cut

### Repeated takes — last take wins

When the speaker repeats the same line or phrase multiple times (a retake), keep ONLY the last complete take. Earlier attempts are always cut.

**Spotting retakes:** consecutive lines starting with the same few words.

```
[00:08.16 - 00:12.34] First of all, one of the biggest changes—
[00:12.50 - 00:15.20] First of all, one of the—
[00:15.40 - 00:21.10] First of all, one of the biggest changes is...
```

→ keep only the third take. Cut the first two.

**Same-idea restatements within ~30s** — apply "last take wins" not just to immediately consecutive lines but within a 30-second window. Speakers often try a take, move on, then come back and re-state the same idea. The later restatement wins.

**Multiple attempts with significant gaps** — if the speaker attempts the same example three times across the recording with gaps between them, identify ALL attempts and keep only the final most complete one. Cut everything in between.

### False starts

A line ending with `—` or that trails off mid-thought and restarts is almost always a false start. Keep the completed retake that follows.

```
[00:42.00 - 00:43.10] So the model—
[00:43.30 - 00:48.50] So the model card explains how this works.
```

→ cut the first line entirely.

**Exception: rescued micro-segments.** If a false start contains a useful phrase that the clean retake omits, extract that phrase as a 1-2 second micro-segment and place it before the clean retake.

```
[00:42.00 - 00:43.10] So the model system card—
[00:43.30 - 00:46.50] So the model explains how this works.
```

→ rescue "model system card" from the false start (as a 1.3s micro-segment), then concatenate with the clean retake.

### Standalone fillers

Drop standalone filler words used as hesitations (not part of natural speech). Filler vocabulary is language-specific:

- **English:** `uh`, `um`, `er`, `like` (when used as filler, not comparison), `you know`, `I mean` (when restarting a thought)
- **Thai:** `เออ`, `อ่ะ` (filler), `แบบ` (when used as hesitation, not "like X"), `คือว่า`, `จริงๆแล้ว`, `ก็คือ` (filler usage)
- **Mixed:** the same words behave the same way regardless of code-switching context.

**Note for Thai:** particles like `ครับ`, `นะ`, `ค่ะ` are NOT fillers — they're sentence-ending particles. Keep them. Same for `แต่`, `ก็`, `และ` as conjunctions.

### Mid-sentence stumbles

Surgically remove stumbles by ending the segment before the stumble and starting a new segment after the correction.

```
[00:50.00 - 00:55.00] The system struggles to solve like new and— problems that haven't been seen before.
```

→ cut "struggles to solve like new and—" by splitting the segment:
- Segment A: "The system" (00:50.00 - 00:50.80)
- Segment B: "problems that haven't been seen before." (00:53.10 - 00:55.00)

The cut works better than the stumble in the final video. Don't keep stumbles just because splitting feels awkward.

### Dead air between takes

Long silence between takes is removed. The final video should flow continuously from one kept segment to the next.

### Internal silences within a segment

A kept segment with a 500ms+ internal pause (breath, hesitation, dead air) gets split into two segments with the silence removed. `refine_edl.py` runs after the editorial pass and catches most of these via silence detection — but the editorial pass should also pre-emptively split obvious cases when reading the transcript.

Review every segment >5 seconds and look for gaps in the transcript timestamps. Even short segments can contain splittable pauses.

### Non-speech tags

Remove every `[MUSIC]`, `[NOISE]`, `[APPLAUSE]`, etc. entirely. They're transcription artifacts, not content.

### Redundant meta-commentary

If a segment explicitly narrates a point the video is already making through examples, it's redundant. Cut it.

```
"The whole point of this video is showing how to shift your mindset
 from HOW to WHAT."
```

→ if the rest of the video already demonstrates this through examples, the meta-commentary is redundant. Show, don't tell.

---

## 2. What to keep

### Short emotional beats

1-3 second emotional reactions or transitions like "And honestly, I get really surprised" are NOT filler. They humanize the content and bridge sections. Keep unless they're stammered or repeated.

### Particles and natural conjunctions

In Thai casual register, sentence-ending particles (`ครับ`, `นะ`, `ค่ะ`, `จ้า`) and conjunctions used naturally (`แต่`, `ก็`, `และ`, `หรือ`) are part of how people speak. Keep them. Only drop when they're CLEARLY hesitation fillers.

### Speaker's intended pacing

The speaker may use deliberate short pauses for emphasis. Don't auto-cut every silence — read the surrounding text. A 700ms pause before a punchline is intentional pacing, not dead air.

### Code-switched loanwords with their context

Mixed Thai+English: keep loanwords with their Thai context. `GPU ได้`, `ใช้ Cursor`, `Claude เขียนโค้ด` are coherent units. Don't cut the Thai connector to "tighten" the English brand.

---

## 3. Padding and boundaries

### Padding defaults

- **Start padding:** ~200ms before each segment start. STT timestamps mark when a word becomes recognizable, which is ~200-300ms after the speaker actually begins the sound. Without padding, the start of each cut sounds clipped.
- **End padding:** ~200ms after each segment end. Same logic in reverse — end timestamps are usually slightly tight.

Field-tested: 400ms was too much (user trimmed most starts back); 100ms was too little (clipped onsets). 200ms is the sweet spot.

### Merging close segments

When two kept segments are within 300ms of each other, merge them into one segment. Avoids micro-glitches in the final cut. `refine_edl.py` does this automatically with `--merge-gap-ms 100`, but the editorial pass should also pre-emptively merge obvious cases.

### When merging takes precedence over splitting

If you're tempted to split a segment at an internal pause but the resulting fragments would be < 500ms each, don't split — the segments are too short to be useful. `refine_edl.py` drops anything under `--min-segment-ms 500` after splitting; do the same in the editorial pass.

---

## 4. Language-specific rules

### Thai

**Filler words to drop:**
- `เออ` — hesitation marker, almost always filler
- `อ่ะ` — when used at start of sentence as hesitation (vs as sentence-ending particle, which is fine)
- `แบบ` — when used as "uhh, like..." filler (vs comparing, which is content)
- `คือว่า` — restart marker, drop if followed by a real take
- `อืม`, `อืมม` — thinking sound, drop unless used for emphasis

**Particles to KEEP (these are not fillers):**
- `ครับ`, `ค่ะ`, `จ้า`, `นะ` — sentence-ending politeness/particles
- `แต่`, `ก็`, `และ`, `หรือ`, `ที่`, `เพราะ`, `ถ้า` — conjunctions
- `เลย`, `ไง` — emphasis particles when used naturally

**Word boundaries:** Thai has no spaces between words. STT may segment oddly. The editorial pass works at phrase level, not word level — don't try to count Thai words for cut decisions.

**Take boundaries:** Thai retakes often start with `เอ่อ`, `โอเค`, `เอาใหม่`, `อันนี้คือ` — those are the speaker resetting. The phrase that follows is usually a fresh take.

### English

**Filler words to drop:**
- `uh`, `um`, `er` — always filler
- `like` — drop when used as filler ("it's like, really cool"), keep when used as comparison ("it's like a chair")
- `you know` — drop when used as filler ("you know, the thing is..."), keep when speaker is checking comprehension
- `I mean` — drop when used to restart a thought, keep when used for clarification

**Stumble patterns:** `s-s-something`, `the the the`, `and-and-and`. Cut all but one instance.

**Take boundaries:** English retakes often start with `Okay so`, `Let me try that again`, `Right so`. Fresh take usually follows.

### Mixed

Apply both rule sets. Code-switching itself is not a problem — only flag when the switch coincides with a stumble or restart.

---

## 5. The final 20% rule

Apply EXTRA scrutiny to the final 20% of a recording. Speaker fatigue produces the most retakes there.

For conclusion sections specifically: identify the single cleanest statement of each point. Speakers in conclusions tend to restart their summary 3-4 times trying to nail the closing line. Pick the cleanest one and cut everything else.

For openings: pick ONE definitive take. Never combine material from two different opening attempts — the result reads as choppy.

---

## 6. Quality bar

Before saving the EDL, self-check against these. If any fail, fix and re-emit.

- [ ] Total kept duration is 30-50% of original for typical raw recordings with retakes. If you're keeping >70% on a raw recording, you probably missed retakes.
- [ ] No segment shorter than 500ms (likely a mistake — or a rescued micro-segment, in which case note it).
- [ ] No gap < 50ms between consecutive segments (merge them instead).
- [ ] No segment longer than 5 seconds without checking for internal pauses to split.
- [ ] Segments are chronological and non-overlapping.
- [ ] `notes[]` documents every retake group dropped, every micro-segment rescued, every stumble surgically removed. Empty notes on a raw recording is suspicious.
- [ ] Final 20% reviewed twice (once for content, once for restart density).
- [ ] Opening picks ONE take, not a combination.

---

## 7. Examples

### Example 1: simple retake

**Transcript:**
```
[00:08.16 - 00:12.34] Okay, so we have a lot of Cloud Code updates to go over—
[00:12.50 - 00:18.90] Okay, so we have a whole bunch of Cloud Code updates to go over today.
```

**EDL:**
```json
{"segments": [{"start_ms": 12300, "end_ms": 19100}]}
```

200ms start padding (12500 → 12300), 200ms end padding (18900 → 19100). First take cut as a false start (ends with `—`).

`notes[]`:
- "Cut take 1 ([8.16-12.34]) as false start ending with '—'. Kept take 2 ([12.50-18.90]) as the completed version."

### Example 2: rescued micro-segment

**Transcript:**
```
[01:42.00 - 01:43.10] So the model system card—
[01:43.30 - 01:46.50] So the model explains how this works.
```

**EDL:**
```json
{"segments": [
  {"start_ms": 102100, "end_ms": 103300},
  {"start_ms": 103100, "end_ms": 106700}
]}
```

`notes[]`:
- "Rescued 'model system card' from take 1 ([1:42.00-1:43.10]) as a 1.3s micro-segment because take 2 ([1:43.30]) said only 'model'. Concatenation order: micro-segment first, then take 2."

### Example 3: Thai with filler drop

**Transcript:**
```
[00:05.00 - 00:08.50] เออ ก็คือว่า เริ่มจาก หลักการพื้นฐาน
[00:08.50 - 00:12.20] หลักการพื้นฐานของ AI คือ การเรียนรู้จากข้อมูล
```

**Decision:**
- Take 1 starts with `เออ ก็คือว่า` — both fillers. Drop them.
- Take 1 then says `เริ่มจาก หลักการพื้นฐาน` — incomplete thought.
- Take 2 says `หลักการพื้นฐานของ AI คือ การเรียนรู้จากข้อมูล` — complete.
- Take 2 wins. Cut take 1 entirely.

**EDL:**
```json
{"segments": [{"start_ms": 8300, "end_ms": 12400}]}
```

`notes[]`:
- "Cut take 1 ([5.00-8.50]) — opens with fillers `เออ ก็คือว่า`, then trails into incomplete thought. Take 2 says the same idea cleanly."

### Example 4: stumble surgery

**Transcript:**
```
[00:50.00 - 00:55.00] The system struggles to solve like new and— problems that haven't been seen before.
```

**EDL:**
```json
{"segments": [
  {"start_ms": 49800, "end_ms": 50600},
  {"start_ms": 53000, "end_ms": 55200}
]}
```

`notes[]`:
- "Surgically removed stumble 'struggles to solve like new and—' by splitting the segment. Kept 'The system' (start) and 'problems that haven't been seen before' (end). Reconcatenation should sound like a single sentence."
