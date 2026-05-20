# Template 02 — Full-screen Vertical with Particle-Burst Captions

Created 2026-05-20. A single talking-head video fills the whole 1080×1920
vertical frame; B-roll cutaways also fill the frame. Kinetic particle-burst
Thai captions on top.

## When to use

- You have ONE video — a talking head / piece-to-camera — and no screen
  recording to show.
- Output target is 1080×1920 vertical (TikTok / Reels / Shorts / FB Reels).
- You want the speaker full-screen with B-roll cutaways covering the frame.

## When NOT to use

- There's a screen recording to show alongside the face → use **Template 01**
  (stacked: screen on top, face circle on bottom).
- Horizontal or square format → Template 03+ (not built yet).

## What it produces

```
Output:  1080×1920 vertical MP4, 30 fps, H.264 / AAC
Layout:  bg.png (fallback) → bottom video full-screen → full-screen B-roll inserts → captions
Captions: kinetic particle-burst, Thai-Latin mixed, gold tokens for numbers/brands
Audio:   bottom audio (the only video), polished -16 LUFS target, BGM 5% optional
```

## How it differs from Template 01

| | Template 01 | Template 02 |
|--|-------------|-------------|
| Source videos | top.mp4 + bottom.mp4 | **bottom.mp4 only** |
| Layout | screen frame + face circle | **face video full-screen** |
| B-roll | 3s inside the top frame (16:9) | **full-screen (9:16)** |
| Pipeline Step 7 | trim top + bottom in parallel | **trim bottom only** |
| Captions | particle-burst (shared) | particle-burst (shared, identical) |

Everything else — transcribe, editorial subagent, Silero VAD, audio polish,
post-process subagent, BGM, QA — is the same v88 pipeline.

## How to start a new clip

```bash
# 1. Put ONE video + bg in raw-media/ (no top.mp4 needed)
mkdir "raw-media/$(date +%Y-%m-%d)-my-clip"
#    bottom.mp4  = the talking head (master audio)
#    bg.png      = fallback background

# 2. Scaffold
bash tools/new-job.sh 02 my-clip --raw $(date +%Y-%m-%d)-my-clip

# 3. Follow V88_PLAYBOOK.md — but Step 7 trims bottom only (no top)
```

## Step 11 (composition build) — three scripts

```bash
python3 scripts/set-duration.py <DURATION>     # set composition duration
python3 scripts/build-burst-captions.py        # captions from caption-groups.json
python3 scripts/add-broll.py 12 32 52 70       # full-screen B-roll inserts
```

`add-broll.py` here inserts B-roll as **full-screen** `.broll-frame` elements
(class `fullscreen-media broll-frame`, after `#bottomVideo`).
`generate-broll.js` generates clips at **9:16** (portrait) so they fill the frame.

## Files

```
manifest.json    machine-readable spec
README.md        this file
DESIGN.md        full-screen layout / colors / motion
index.html       composition source-of-truth (generic per-job paths)
hyperframes.json / meta.json / package.json
compositions/    captions-burst.html is generated per job; components/ = reference block
scripts/
  set-duration.py        set composition duration
  build-burst-captions.py  caption-groups.json → captions-burst.html (shared with T01)
  add-broll.py           insert FULL-SCREEN B-roll elements
  generate-broll.js      AI B-roll generation at 9:16 (edit prompts per job)
assets/bg.png    default fallback background
prompts/         subagent slot defaults
reference/       golden test (populated after the first job)
```
