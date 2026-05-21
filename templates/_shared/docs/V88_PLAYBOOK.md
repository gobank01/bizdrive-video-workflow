# V88 BIZDRIVE — Portable Playbook

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
# NOTE: alimiter MUST have level=disabled — its default level=enabled
# auto-normalises the peak back to 0 dBFS and clips the WAV. See MISTAKES.md #7.
ffmpeg -y -i assets/<JOB>/bottom_visual_master.mp4 -vn -ac 1 -ar 48000 \
  -af "highpass=f=80,lowpass=f=12000,afftdn=nf=-25,agate=threshold=-40dB:ratio=2:attack=20:release=200,acompressor=threshold=-18dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=<I>:measured_TP=<TP>:measured_LRA=<LRA>:measured_thresh=<THRESH>:offset=<OFFSET>:linear=true:print_format=summary,alimiter=limit=-1.5dB:level=disabled,apad=pad_dur=0.5" \
  -c:a pcm_s16le assets/<JOB>/speech_polished.wav

# Verify the result: astats "Peak level dB" MUST be <= -1.0 (not 0.0).
ffmpeg -nostats -i assets/<JOB>/speech_polished.wav -af "astats=metadata=1" -f null - 2>&1 | grep "Peak level dB" | head -1
ffmpeg -nostats -i assets/<JOB>/speech_polished.wav -af "ebur128=peak=true" -f null - 2>&1 | grep -A 14 "Summary:" | grep -E "I:|Peak:"

# With level=disabled the linear loudnorm is true-peak-limited and often lands
# ~-19 LUFS (below the -18 floor). If so, run ONE corrective 2-pass dynamic
# loudnorm on the WAV — analyze, then apply with the measured values:
#   ffmpeg -nostats -i speech_polished.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null -
#   ffmpeg -y -i speech_polished.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=<I>:measured_TP=<TP>:measured_LRA=<LRA>:measured_thresh=<THRESH>:offset=<OFFSET>:print_format=summary,alimiter=limit=-1.5dB:level=disabled" -ar 48000 -c:a pcm_s16le speech_polished.wav
# It lands ~-17.5 LUFS / TP -1.5. loudnorm cannot reach -16 — the TP -1.5
# ceiling caps it, and -17.x is the genuine ceiling for this content.
```

Verify: `-16 ± 2 LUFS` (expect ~-17.5; the TP ceiling caps it there), true peak ≤ -1.5 dBTP, **sample peak ≤ -1.0 dBFS (no clipping)**. Polished WAV will be slightly longer than the video master (apad pads ~500ms) — mux step trims to video duration.

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

### Step 11 — Build composition + burst captions

The workspace `index.html` is copied from Template 01 and already uses
**generic per-job paths** — no path-fixing needed:

- `assets/input/bg.png`
- `assets/intermediates/top_visual_master.mp4`
- `assets/intermediates/bottom_visual_master.mp4`
- `assets/intermediates/broll/broll-NN.mp4`

The job workspace's `assets/` symlinks resolve these automatically. The only
per-job edits are duration, captions, and B-roll — handled by three scripts:

```bash
# 1. Set the composition duration (rewrites all 7 duration spots in index.html)
python3 scripts/set-duration.py <DURATION>      # e.g. 92.748632

# 2. Build the burst caption sub-composition from caption-groups.json
python3 scripts/build-burst-captions.py
#    reads assets/intermediates/transcript/caption-groups.json
#    writes compositions/captions-burst.html + mounts it on track 3 (z-index 10)

# 3. (optional) Insert B-roll — only after B-roll clips exist in
#    assets/intermediates/broll/. Pass each clip's start time:
python3 scripts/add-broll.py 15 35 55 75
```

`set-duration.py` auto-detects the current duration from `#root` and replaces
every occurrence (root, background, topVideo ×2, bottomVideo, captions mount,
the JS `compositionDuration`) — preventing the duration-mismatch bug.

`add-broll.py` enforces the v88 B-roll rules (3s each, ≥6s spacing, must fit
the composition) and is re-runnable (replaces any prior B-roll block).

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

### Step 14 — Final audio: polished speech + BGM + context SFX

The final audio mux is **one script** — `scripts/mix-sfx.py` — driven by a
per-job `assets/intermediates/sfx-plan.json`.

**SFX rule (v88) — every clip gets sound effects, kept sparse:**

- **At most 5 SFX per clip.** Hard cap.
- Roughly **1 SFX per 12s** of final video — fewer for clips under 60s.
- SFX starts **≥ 4s apart** and inside `[0, duration]`.
- **Every SFX is context-matched** to the beat it lands on — a whoosh on a
  topic turn, a `ding` on a CTA / follow-card, a `punch` on a punchline, a
  `riser` before a reveal, `cash-register` on a money beat, etc.
- Pick from the shared library: `templates/_shared/sfx/sfx-library.json`
  (13 SFX, categorised). In a job workspace it is symlinked at `assets/sfx/`.

```bash
# 1. Pick BGM (unchanged — or pick manually from bgm-library/mixkit-stock-v50.json)
npm run select:bgm -- --title "..." --transcript assets/<JOB>/transcript/raw-elevenlabs.json

# 2. Write assets/intermediates/sfx-plan.json — context-matched, <= 5 SFX:
#    {
#      "duration": <DURATION>,
#      "visual": "../output/finals/visual.mp4",
#      "speech": "assets/intermediates/speech_polished.wav",
#      "bgm": "assets/bgm/stock/mixkit/<PICKED-FILE>.mp3",
#      "bgmGainPercent": 6,
#      "sfx": [
#        { "file": "whoosh-soft", "at": 0.1,  "note": "opening hook" },
#        { "file": "ding",        "at": 60.9, "note": "follow-card slide-in" }
#      ]
#    }

# 3. Mix the final audio (enforces the SFX rule, auto-levels each SFX, limits the sum)
python3 scripts/mix-sfx.py
#    -> ../output/finals/no-bgm.mp4   speech only (frame-lock QA reference)
#    -> ../output/finals/final.mp4    speech + BGM + SFX  (the deliverable)
```

`mix-sfx.py` rejects a plan that breaks the SFX rule (>5, clumped, out of
range), auto-normalises each SFX to a consistent accent level (target -5 dBFS
peak), sums the mix (`amix normalize=0`) and runs `alimiter` so it never clips.

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

### Step 16 — Thumbnail + cover embed (MANDATORY)

**Every clip ships a thumbnail — this step is NOT optional.** Whenever a clip is
edited, it gets a default thumbnail (BG + a big 3-line headline; the BIZDRIVE
logo and the "ให้ AI ทำงานแทนคุณ" bottom strip are already baked into `bg.png`),
and that thumbnail is embedded into the clip as cover art. Template-agnostic —
the same `scripts/build-thumbnail.py` ships in all templates (01-05).

```bash
# Run from the job workspace, AFTER Step 14 (final mux). Args: <main> <hero> <sub>
python3 scripts/build-thumbnail.py "<main line>" "<hero line>" "<sub line>"
# e.g.
python3 scripts/build-thumbnail.py "AI มี" "3 ระดับ" "คุณใช้อยู่ระดับไหน?"
```

- **main** — white top line. **hero** — big gold-gradient line, keep it short
  (a number / brand / 2-3 words — it is the eye-catcher). **sub** — soft-blue
  bottom line. Each line auto-fits to width.
- The PNG is built with `hyperframes snapshot` (one frame — no video render).
- **Output is named after the clip, NOT "final":**
  - `output/finals/<clip>.png` — the thumbnail (1080×1920)
  - `output/finals/<clip>.mp4` — the deliverable clip with the thumbnail
    embedded as cover art (`attached_pic`); `final.mp4` is replaced by it.
  - `<clip>` = the job id from `manifest.json` (e.g. `2026-05-21-ai-3-levels`).
- A re-snapshottable `thumbnail/` project + `thumbnail/thumbnail.json` (the 3
  lines on record) are left in the workspace (gitignored).

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
| 13 — MP4 | Visual-only render | `output/finals/visual.mp4` |
| 14 — Plan | SFX plan (≤5, context-matched) | `assets/intermediates/sfx-plan.json` |
| 14 — MP4 | No-BGM mux | `output/finals/no-bgm.mp4` |
| 14 — MP4 | Final mux (speech + BGM + SFX) — superseded by Step 16 | `output/finals/final.mp4` |
| 15 — QA | Timestamp sheet | `reports/<JOB>/timestamps/timestamp-qa-sheet.jpg` |
| 16 — Thumbnail | Default thumbnail (BG + headline) | `output/finals/<clip>.png` ⭐ |
| 16 — MP4 | **Deliverable clip** (final + embedded cover art) | `output/finals/<clip>.mp4` ⭐ |

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
2. **Loudness lands at -17.5 LUFS** (not -16) — the `TP=-1.5` true-peak ceiling caps how loud the polished WAV can get; -17.x is the genuine ceiling, not drift. Acceptable for social media. (Step 8 now uses `alimiter=...:level=disabled` + a corrective loudnorm pass — see MISTAKES.md #7.)
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
