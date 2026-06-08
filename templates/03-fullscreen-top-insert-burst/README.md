# Template 03 — Full-screen Vertical with Top Insert

Created 2026-05-20. A single talking-head video fills the whole 1080×1920
vertical frame; B-roll plays inside a floating 16:9 rounded insert card over
the upper third — the face video stays visible around the card. Kinetic
particle-burst Thai captions on top.

## When to use

- You have ONE video — a talking head / piece-to-camera — and you want B-roll
  shown **alongside** the speaker, not replacing them.
- Output target is 1080×1920 vertical (TikTok / Reels / Shorts / FB Reels).
- The classic reaction / commentary look: speaker full-screen, the thing
  they're talking about in a card above their head.

## When NOT to use

- You want B-roll to take over the whole frame → use **Template 02**
  (full-screen B-roll).
- There's a screen recording to show in a fixed top frame the whole clip →
  use **Template 01** (stacked: screen on top, face circle on bottom).
- Horizontal or square format → Template 04+ (not built yet).

## What it produces

```
Output:  1080×1920 vertical MP4, 30 fps, H.264 / AAC
Layout:  bg.png (fallback) → bottom video full-screen → floating 16:9 top-insert B-roll → captions
Captions: kinetic particle-burst, Thai-Latin mixed, gold tokens for numbers/brands
Audio:   bottom audio (the only video), polished -16 LUFS target, BGM 5% optional
```

## How it differs from Template 01 / 02

| | Template 01 | Template 02 | Template 03 |
|--|-------------|-------------|-------------|
| Source videos | top.mp4 + bottom.mp4 | bottom.mp4 only | **bottom.mp4 only** |
| Layout | screen frame + face circle | face video full-screen | **face full-screen + floating top insert** |
| B-roll | 3s inside the top frame (16:9) | full-screen (9:16) | **floating 16:9 card, upper third** |
| Face during B-roll | hidden (top frame) | covered by B-roll | **stays visible around the card** |
| Pipeline Step 7 | trim top + bottom | trim bottom only | **trim bottom only** |
| Captions | particle-burst (shared) | particle-burst (shared) | particle-burst (shared, identical) |

Everything else — transcribe, editorial subagent, Silero VAD, audio polish,
post-process subagent, BGM, QA — is the same v88 pipeline.

## How to start a new clip

```bash
# 1. Put ONE video + bg in raw-media/ (no top.mp4 needed)
mkdir "raw-media/$(date +%Y-%m-%d)-my-clip"
#    bottom.mp4  = the talking head (master audio)
#    bg.png      = fallback background

# 2. Scaffold
bash tools/new-job.sh 03 my-clip --raw $(date +%Y-%m-%d)-my-clip

# 3. Follow V88_PLAYBOOK.md — but Step 7 trims bottom only (no top)
```

## Step 11 (composition build) — three scripts

```bash
python3 scripts/set-duration.py <DURATION>     # set composition duration
python3 scripts/build-burst-captions.py        # captions from caption-groups.json
python3 scripts/add-broll.py 12 32 52 70       # floating top-insert B-roll cards
```

`add-broll.py` here inserts B-roll as **floating 16:9 insert cards**
(class `top-insert broll-frame`, after `#bottomVideo`) — each pops in over the
upper third while the face stays visible around it.
`generate-broll.js` generates clips at **16:9** (landscape) to fill the card.

## Files

```
manifest.json    machine-readable spec
README.md        this file
frame.md        full-screen + top-insert layout / colors / motion
index.html       composition source-of-truth (generic per-job paths)
hyperframes.json / meta.json / package.json
compositions/    captions-burst.html is generated per job; components/ = reference block
scripts/
  set-duration.py        set composition duration
  build-burst-captions.py  caption-groups.json → captions-burst.html (shared with T01/T02)
  add-broll.py           insert floating 16:9 top-insert B-roll cards
  generate-broll.js      AI B-roll generation at 16:9 (edit prompts per job)
assets/bg.png    default fallback background
prompts/         subagent slot defaults
reference/       golden test (populated after the first job)
```
