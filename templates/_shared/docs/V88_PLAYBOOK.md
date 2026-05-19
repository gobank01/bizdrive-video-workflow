# V88 BIZDRIVE × ii23 — Portable Playbook

**Status:** v88 perfect checkpoint (locked 2026-05-19). Use this playbook to reproduce the pipeline on any new clip with any AI agent (Claude Code, Claude API, Cursor, Codex CLI, ChatGPT, etc.). Every step is explicit — no chat-context assumed.

**Final reference output:** [`../preview-v88/v88-video-div-burst-v2-final.mp4`](../preview-v88/v88-video-div-burst-v2-final.mp4) — 1080×1920, 30 fps, 103.59s, 3107 frames, BGM 5%, particle-burst captions aligned to ElevenLabs word boundaries with post-processed text.

---

## 1. What this pipeline produces

**Input:**
- `bottom.mp4` — face video, contains the master audio (speaker's voice)
- `top.mp4` — screen recording, MUST be muted in final
- `bg.png` — full-screen background image
- (optional) `assets/broll/index.json` — B-roll stock library
- (optional) `bgm-library/mixkit-stock-v50.json` — BGM stock

**Output:**
- `*-final.mp4` — 1080×1920 vertical, 30 fps, stacked video: bg + top frame (rectangle, top half) + bottom face (circle, bottom half), kinetic Thai captions with gold particle-burst on keywords, optional B-roll inserts in the top frame, optional BGM at 5%

**Edit policy (locked at v88):**
- Bottom audio is the master timeline. Top is muted visual only.
- Trim/dead-air cuts are parallel across top and bottom (same EDL).
- Lip-sync zero tolerance. Top/B-roll may xfade; bottom face may NOT xfade while visible.
- Edit-first architecture: ALL cuts happen before HyperFrames layout.

---

## 2. Required environment

```
Python   3.10+         (tested on 3.13.5)
ffmpeg   any modern    (tested on 7.1.1)
ffprobe  any modern    (tested on 7.1.1)
Node.js  18+           (for HyperFrames + B-roll scripts)
```

### Python packages

```bash
# User site-packages (no venv needed)
python3 -m pip install --user --upgrade pythainlp nlpo3 certifi
```

### Silero VAD venv (one-time, ~437 MB)

```bash
bash scripts/clean-cut/install_vad.sh
# Creates ~/.ii23/vad-env with silero-vad, torch, torchaudio, torchcodec, soundfile, numpy
```

If the VAD script fails with `torchcodec` import error after install, run:

```bash
~/.ii23/vad-env/bin/pip install --quiet torchcodec
```

### API keys — `.env` (gitignored)

Create `stacked-video/.env` (template at `.env.example`):

```
ELEVENLABS_API_KEY=sk_xxx     # required for v88 transcription
# PEXELS_API_KEY=...          # optional, for fresh B-roll download
# OPENROUTER_API_KEY=...      # optional, for AI B-roll generation
```

⚠️ **Never commit .env.** Already ignored via `.gitignore`. Rotate the key if it leaks into a chat or screenshot.

### Verify

```bash
npm run preflight
# JSON should report: ffmpeg/ffprobe/python3/silero_vad all "yes"
```

---

## 3. The 10-step pipeline (every command verbatim)

All commands assume CWD = `stacked-video/`. Replace `<JOB>` with a slug (e.g. `clip-2026-05-20`) and `<INPUT_DIR>` with the source media folder.

### Step 1 — Inspect source media

```bash
ffprobe -v error -show_entries format=duration,start_time:stream=codec_type,r_frame_rate -of json <INPUT_DIR>/bottom.mp4
ffprobe -v error -show_entries format=duration,start_time:stream=codec_type,r_frame_rate -of json <INPUT_DIR>/top.mp4
```

Confirm: top duration == bottom duration, both have 30 fps (or matching fps), bottom has 1+ audio stream.

### Step 2 — Transcribe with ElevenLabs Scribe v2 (3-output mode)

```bash
mkdir -p assets/<JOB>/v88-test
npm run transcribe:el -- <INPUT_DIR>/bottom.mp4 \
  --provider elevenlabs --lang th \
  --save-all assets/<JOB>/v88-test/ \
  --words-per-group 2
```

Output: `raw-elevenlabs.json` (keep forever — re-segmentable), `captions.json` (phrase-level), `words.json` (nlpo3-segmented), `meta.json`.

ElevenLabs returns `duration: null` — patch it from ffprobe:

```bash
python3 -c "
import json
p='assets/<JOB>/v88-test/raw-elevenlabs.json'
d=json.load(open(p)); d['duration']=<DURATION_FROM_FFPROBE>
json.dump(d, open(p,'w'), ensure_ascii=False, indent=2)
"
```

### Step 3 — Editorial subagent → rough-cut EDL

Spawn a general-purpose subagent (Task tool / Codex / second-pass LLM call) with the prompt in [`SUBAGENT_PROMPTS.md`](SUBAGENT_PROMPTS.md) Section A. Fill in the `{{...}}` slots:

- Raw transcript path
- Source media path
- Source duration (from ffprobe)
- Topic / context (one sentence — what's the clip about)
- Speaker register (formal / casual / hype)
- Target output duration (ceiling; AI will shrink if content is shorter)
- Output path → `assets/<JOB>/v88-test/edl-rough.json`

The subagent reads `scripts/clean-cut/references/editorial-rules.md` and produces a frame-snapped EDL with notes.

### Step 4 — Pad-bleed validation

```bash
npm run rough:cut:padbleed -- \
  assets/<JOB>/v88-test/edl-rough.json \
  assets/<JOB>/v88-test/raw-elevenlabs.json \
  -o assets/<JOB>/v88-test/edl-rough-safe.json
```

Print: `editorial decision: keep N words, drop M`. Trims any end-pad that would bleed into a dropped next-word (prevents "ขั้น ขั้น" repetition).

### Step 5 — Apply rough EDL → cleaned-rough.mp4

```bash
npm run apply:edits -- <INPUT_DIR>/bottom.mp4 assets/<JOB>/v88-test/edl-rough-safe.json -o assets/<JOB>/v88-test/cleaned-rough.mp4
```

### Step 6 — Silero VAD jump-cut on the post-rough audio

```bash
mkdir -p assets/<JOB>/v88-test/.tmp
ffmpeg -y -i assets/<JOB>/v88-test/cleaned-rough.mp4 -ac 1 -ar 16000 assets/<JOB>/v88-test/.tmp/post-rough.wav
$HOME/.ii23/vad-env/bin/python3 scripts/clean-cut/vad_detect.py \
  assets/<JOB>/v88-test/.tmp/post-rough.wav \
  --min-silence-ms 300 --pad-ms 200 \
  --output assets/<JOB>/v88-test/.tmp/speech.json
npm run jump:cut:edl -- assets/<JOB>/v88-test/.tmp/speech.json -o assets/<JOB>/v88-test/edl-jump.json
```

### Step 7 — Apply EDLs to BOTH top + bottom in parallel (lip-sync lock)

```bash
mkdir -p assets/<JOB>
# Top: rough → jump
npm run apply:edits -- <INPUT_DIR>/top.mp4 assets/<JOB>/v88-test/edl-rough-safe.json -o assets/<JOB>/top_rough.mp4
npm run apply:edits -- assets/<JOB>/top_rough.mp4 assets/<JOB>/v88-test/edl-jump.json -o assets/<JOB>/top_visual_master.mp4
# Bottom: rough → jump (cleaned-final is the bottom visual master)
npm run apply:edits -- assets/<JOB>/v88-test/cleaned-rough.mp4 assets/<JOB>/v88-test/edl-jump.json -o assets/<JOB>/bottom_visual_master.mp4
```

**Master proof** — `top` and `bottom` MUST have identical `nb_frames` + `duration`:

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,nb_frames -of csv=p=0 assets/<JOB>/top_visual_master.mp4
ffprobe -v error -show_entries format=duration:stream=codec_type,nb_frames -of csv=p=0 assets/<JOB>/bottom_visual_master.mp4
```

### Step 8 — Polish bottom audio

2-pass loudnorm chain (analyze → apply):

```bash
# Pass 1: analyze
ffmpeg -y -i assets/<JOB>/bottom_visual_master.mp4 -vn -ac 1 -ar 48000 \
  -af "highpass=f=80,lowpass=f=12000,afftdn=nf=-25,agate=threshold=-40dB:ratio=2:attack=20:release=200,acompressor=threshold=-18dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" \
  -f null - 2>&1 | grep -A 12 "Parsed_loudnorm" | tail -13
# Read measured_I / measured_TP / measured_LRA / measured_thresh / target_offset from the JSON, then plug into pass 2:

# Pass 2: apply with measured values + apad
ffmpeg -y -i assets/<JOB>/bottom_visual_master.mp4 -vn -ac 1 -ar 48000 \
  -af "highpass=f=80,lowpass=f=12000,afftdn=nf=-25,agate=threshold=-40dB:ratio=2:attack=20:release=200,acompressor=threshold=-18dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=<I>:measured_TP=<TP>:measured_LRA=<LRA>:measured_thresh=<THRESH>:offset=<OFFSET>:linear=true:print_format=summary,alimiter=limit=-1.5dB,apad=pad_dur=0.5" \
  -c:a pcm_s16le assets/<JOB>/speech_polished.wav
```

Verify: `-16 ± 2 LUFS`, true peak ≤ -1.5 dBTP. Polished WAV will be slightly longer than the video master (apad pads ~500ms) — mux step trims to video duration.

### Step 9 — Re-transcribe polished audio on edited timeline

```bash
mkdir -p assets/<JOB>/transcript
npm run transcribe:el -- assets/<JOB>/speech_polished.wav \
  --provider elevenlabs --lang th \
  --save-all assets/<JOB>/transcript/ \
  --words-per-group 2
```

This gives word timing aligned to the EDITED timeline (0 → ~duration), which is what captions need.

### Step 10 — Post-process subagent → caption-groups.json

Spawn a second subagent with the prompt in [`SUBAGENT_PROMPTS.md`](SUBAGENT_PROMPTS.md) Section B. Inputs:

- Raw transcript: `assets/<JOB>/transcript/raw-elevenlabs.json`
- Source audio: `assets/<JOB>/speech_polished.wav`
- Video duration (caption end cap)
- Topic / context
- Reference for gold-token taste

Output: `assets/<JOB>/transcript/caption-groups.json` with structure:

```json
{
  "duration": 103.561333,
  "language": "th",
  "groups": [
    { "start": 0.28, "end": 1.82, "tokens": [{"text":"...","gold":false}, ...] }
  ],
  "notes": [...]
}
```

---

## 4. Composition build & render

### Step 11 — Build v88 composition + burst captions

The HyperFrames composition is `index.html`. For a new job, EITHER:

**A. Edit `index.html` directly** — swap video paths, set `data-duration` to the new clip's duration. Or:

**B. Use the v87 template builder + burst script** (the path used for the locked v88 reference clip):

```bash
# (Only if you're starting from a v87-style composition)
# python3 scripts/build-v88-composition.py   # NOT generic — encodes v87→v88 shift; review before use

# Build burst captions from the post-processed JSON:
python3 scripts/build-burst-captions.py
```

`build-burst-captions.py` reads `assets/v88-video-div/transcript/caption-groups.json` (path is hardcoded — edit `GROUPS_JSON` constant in the script for a new job) and writes:

- `compositions/captions-burst.html` — particle-burst sub-composition
- `index.html` — replaces any inline subtitle lines with the sub-composition mount on track 3

### Step 12 — Lint + visual inspect

```bash
npm run check
npm run check:caption-gold
```

Both must pass with 0 errors. `timeline_track_too_dense` warning is gone since captions live in the sub-composition.

### Step 13 — Render visual-only

```bash
mkdir -p ../preview-<JOB>
npx --yes hyperframes@0.6.25 render \
  --output ../preview-<JOB>/<JOB>-visual.mp4 \
  --quality standard
```

Watch for the `sparse keyframes` warning — apply_edits.py re-encodes segments but uses `-c copy` at the concat step, so the final masters inherit segment GOP. The warning is cosmetic for our pipeline; if you see frame freezing at scrub time, re-encode masters with `-g 30 -keyint_min 30`.

### Step 14 — Mux polished speech + BGM 5%

```bash
# Mux speech
ffmpeg -y \
  -i ../preview-<JOB>/<JOB>-visual.mp4 \
  -i assets/<JOB>/speech_polished.wav \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k -ar 48000 \
  -t <DURATION> \
  -movflags +faststart \
  ../preview-<JOB>/<JOB>-no-bgm.mp4

# Select BGM (or pick manually from bgm-library/mixkit-stock-v50.json)
npm run select:bgm -- --title "..." --transcript assets/<JOB>/transcript/raw-elevenlabs.json

# Mix BGM at 5%
npm run mix:bgm -- \
  --voice ../preview-<JOB>/<JOB>-no-bgm.mp4 \
  --bgm assets/bgm/stock/mixkit/<PICKED-FILE>.mp3 \
  --output ../preview-<JOB>/<JOB>-final.mp4 \
  --gain-percent 5
```

### Step 15 — Final QA

```bash
# Frame lock (must match pre-BGM)
ffprobe -v error -show_entries format=duration,start_time:stream=codec_type,nb_frames -of csv=p=0 ../preview-<JOB>/<JOB>-final.mp4

# Silence >0.5s
ffmpeg -i ../preview-<JOB>/<JOB>-final.mp4 -af "silencedetect=noise=-30dB:d=0.5" -f null - 2>&1 | grep silence_

# Loudness
ffmpeg -i ../preview-<JOB>/<JOB>-final.mp4 -af "ebur128=peak=true" -f null - 2>&1 | grep -A 4 "Integrated loudness"

# 1-second timestamp QA sheet
npm run qa:timestamps -- --input ../preview-<JOB>/<JOB>-final.mp4 --output-dir reports/<JOB>/timestamps
```

Frame count after BGM mix MUST equal frame count before. Audio duration metadata may drift ±25ms — that's container overhead, not frame loss.

---

## 5. File map (every artifact, by Phase)

| Phase | Artifact | Path |
|-------|----------|------|
| 2 — Transcript | Raw ElevenLabs | `assets/<JOB>/v88-test/raw-elevenlabs.json` |
| 3 — EDL | Editorial rough cut | `assets/<JOB>/v88-test/edl-rough.json` |
| 4 — EDL | Pad-bleed validated | `assets/<JOB>/v88-test/edl-rough-safe.json` |
| 5 — MP4 | Post-rough cleaned bottom | `assets/<JOB>/v88-test/cleaned-rough.mp4` |
| 6 — EDL | Silero VAD jump | `assets/<JOB>/v88-test/edl-jump.json` |
| 7 — Masters | Top visual | `assets/<JOB>/top_visual_master.mp4` |
| 7 — Masters | Bottom visual | `assets/<JOB>/bottom_visual_master.mp4` |
| 8 — Audio | Polished speech | `assets/<JOB>/speech_polished.wav` |
| 9 — Transcript | Edited-timeline transcript | `assets/<JOB>/transcript/raw-elevenlabs.json` |
| 10 — Captions | Post-processed groups | `assets/<JOB>/transcript/caption-groups.json` |
| 11 — Composition | Burst captions | `compositions/captions-burst.html` |
| 13 — MP4 | Visual-only render | `../preview-<JOB>/<JOB>-visual.mp4` |
| 14 — MP4 | No-BGM mux | `../preview-<JOB>/<JOB>-no-bgm.mp4` |
| 14 — MP4 | **Final** | `../preview-<JOB>/<JOB>-final.mp4` ⭐ |
| 15 — QA | Timestamp sheet | `reports/<JOB>/timestamps/timestamp-qa-sheet.jpg` |

---

## 6. Porting to a different AI agent

The pipeline relies on AI in exactly 2 places: editorial subagent (Step 3) and post-process subagent (Step 10). Both are stateless LLM calls — drop the prompts from [`SUBAGENT_PROMPTS.md`](SUBAGENT_PROMPTS.md) into any agent (Claude API, OpenAI, Gemini, Codex CLI, Cursor compose, etc.) and it should produce equivalent output. Both prompts are self-contained: they reference local files but assume nothing about the chat context.

| AI agent | How to invoke |
|----------|--------------|
| Claude Code (this) | `Task` tool, subagent_type `general-purpose` |
| Claude API | One `messages.create` call with the prompt + file contents inlined |
| Codex CLI | `codex` with the prompt — preserve the file-write instruction |
| Cursor / Continue | Paste the prompt; provide file access to project root |
| ChatGPT (web) | Upload `raw-elevenlabs.json` + `editorial-rules.md`, paste prompt |

The Python and Node scripts have zero AI dependencies — they're deterministic FFmpeg/JSON tools.

---

## 7. Tolerances (what's "good enough")

| Check | Spec | Acceptable | Block |
|-------|------|-----------|-------|
| Lip sync | top frames == bottom frames | exact match | any drift |
| Silence >0.5s | 0 segments | ≤3 (from VAD pad_ms=200) | >5 |
| Loudness | -16 LUFS | -14 to -18 LUFS | <-22 or >-12 |
| True peak | ≤ -1.5 dBTP | ≤ -1.0 dBTP | > 0 (clipping) |
| Frame lock pre/post BGM | identical | nb_frames identical | nb_frames differ |
| Caption-gold spacing | `npm run check:caption-gold` pass | pass | any issue |
| HyperFrames lint | 0 errors | 0 errors, ≤1 warning | any error |
| Trim drift vs editorial EDL | 0 | ≤2 frames | >5 frames |

---

## 8. Known v88 imperfections (document, don't pretend they're fixed)

1. **Sparse keyframes warning on visual masters** — `apply_edits.py` concat uses `-c copy`, so per-segment GOP (≥8s) carries through. Cosmetic in our render but should re-encode with `-g 30 -keyint_min 30` if a downstream tool needs scrubbing.
2. **Loudness lands at -17.5 LUFS** (not -16) — 2-pass loudnorm has small drift with our chain. Acceptable for social media.
3. **BGM mix duration +21 ms** — audio container metadata adjusts, video frames unchanged.
4. **3-5 silences >0.5s in the polished WAV** — from Silero VAD's `pad_ms=200`. Reduce to `100` for tighter cuts at cost of clipping particle endings.
5. **Caption boundary on Thai sub-word splits** — when ElevenLabs returns a long word entry (e.g. `ยี่สิบปีสามสิบปี`), the post-process subagent splits it with char-proportional interpolation; expect ~300 ms timing drift on those tokens.
6. **Editorial subagent splits**, not joins. If the speaker had genuinely overlapping retakes, the agent may keep both. Inspect the EDL `notes[]` field.

---

## 9. Subagent prompts (the load-bearing prompts)

Both prompts live verbatim in [`SUBAGENT_PROMPTS.md`](SUBAGENT_PROMPTS.md). They are the difference between a usable pipeline and broken captions. Do NOT shorten them when porting — every clause is there because of a past failure.

---

## 10. Validating a port (golden test)

Run the pipeline against the locked reference clip:

```
Input:    /Users/gobank01/Documents/Video V3/video div/{top.mp4, bottom.mp4, bg.png}
Expected: /Users/gobank01/Documents/Video V3/preview-v88/v88-video-div-burst-v2-final.mp4
Tolerance:
  - duration ±50ms
  - frame count exact (3107)
  - caption group count ±5 of 48
  - gold token count 18-26 (target 22)
  - peak loudness within -14 to -18 LUFS
```

If your port matches these tolerances, the workflow is preserved. Iterate creative choices (caption style, BGM, B-roll) — but don't alter the EDL math or the master proof.
