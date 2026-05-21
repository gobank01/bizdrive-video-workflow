# Template 05 — Stacked Vertical with Karaoke Highlight Captions

Created 2026-05-21. BIZDRIVE-style vertical talking-head: the top frame holds a
screen recording, the bottom circle holds the face. Captions use the
**BIZDRIVE Karaoke** style — a coloured box sweeps word-by-word in sync with
the speech (red for normal words, gold for brand / number / tech tokens).

Structurally identical to **Template 01** — the only difference is the caption
system (karaoke box sweep instead of particle burst).

## When to use

- You have TWO videos — a screen recording (`top.mp4`) + a face cam (`bottom.mp4`).
- Output target is 1080×1920 vertical (TikTok / Reels / Shorts).
- You want the punchy, CapCut-style **karaoke** caption look — every word
  highlighted on beat — rather than the calmer particle-burst.

## When NOT to use

- You want the premium gold-text + particle-burst look → **Template 01**
  (same stacked layout, different caption system).
- There's only ONE video (no screen recording) → **Template 04** (full-screen
  + karaoke) or **Template 02** (full-screen + particle-burst).
- B-roll should sit in a floating top card over a full-screen face → **Template 03**.

## What it produces

```
Output:  1080×1920 vertical MP4, 30 fps, H.264 / AAC
Layout:  bg.png → top frame (screen recording) → bottom circle (face)
         → B-roll inserts in the top frame → karaoke captions
Captions: BIZDRIVE Karaoke — word-by-word box sweep, red box / gold box (numbers+brands)
Audio:   bottom audio, polished -16 LUFS target, BGM 5% + context SFX
```

## Caption system

Generated per job by `scripts/build-highlight-captions.py` from the standard
`caption-groups.json` (same schema every template uses). It:

- reads the post-processed caption groups (group `start`/`end` + token text + `gold`)
- interpolates per-word timing inside each group by character weight
- marks gold tokens (`token.gold`) → gold box; the rest → red box
- white text, flipping to dark `#1c1206` while a gold box is active (WCAG contrast)

The same `caption-groups.json` feeds both Template 01 (particle-burst) and
Template 05 (karaoke) — switching templates does not require re-running the
post-process subagent.

See [DESIGN.md](DESIGN.md) for the full caption spec.

## How to start a new clip

```bash
# 1. Put the two source videos + bg in raw-media/
mkdir "raw-media/$(date +%Y-%m-%d)-my-clip"
#    top.mp4     = screen recording
#    bottom.mp4  = the face cam (master audio)
#    bg.png      = background (optional — template ships a default)

# 2. Scaffold
bash tools/new-job.sh 05 my-clip --raw $(date +%Y-%m-%d)-my-clip

# 3. Follow V88_PLAYBOOK.md
```

## Step 11 (composition build)

```bash
python3 scripts/set-duration.py <DURATION>
python3 scripts/build-highlight-captions.py \
    assets/intermediates/transcript/caption-groups.json \
    compositions/captions-highlight.html <DURATION> 360
python3 scripts/add-broll.py 15 35 55 75      # optional, B-roll in the top frame
```

`360` is the caption `bottom` offset — places the karaoke captions in the band
below the bottom face circle (Template 04 uses `330` because it is full-screen).

Everything else — transcribe, editorial subagent, Silero VAD, audio polish,
post-process subagent, BGM, SFX, QA — is the same v88 pipeline as Templates 01-04.

## Reference job

(none yet — the first job built on Template 05 becomes the reference.)

## Files

```
manifest.json    machine-readable spec
README.md        this file
DESIGN.md        karaoke caption / stacked layout / colors / motion
index.html       composition source-of-truth (generic per-job paths)
hyperframes.json / meta.json / package.json
compositions/    captions-highlight.html is generated per job;
                 components/caption-highlight.html = reference component
scripts/
  set-duration.py             set composition duration
  build-highlight-captions.py caption-groups.json → captions-highlight.html
  add-broll.py                insert B-roll elements in the top frame
  mix-sfx.py                  context-matched SFX mix
  + shared v88 pipeline scripts (select-bgm, checks, reports …)
assets/bg.png    default background
prompts/         subagent slot defaults (editorial = stacked; post-process = karaoke)
```
