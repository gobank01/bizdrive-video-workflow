# Template 08 — Stacked Vertical with Weight-Shift Captions

Created 2026-06-01. BIZDRIVE-style vertical talking-head: the top frame holds a
screen recording, the bottom circle holds the face. Captions use the
**Weight-Shift** style — minimal typography where the font-weight travels
word-by-word: the currently-spoken word shifts to **bold (700)** + a slight
scale, the rest stay **light (300)**; gold tokens keep a persistent gold colour
so keywords always pop.

Structurally identical to **Template 05** — two differences: the caption system
(word-by-word weight travel instead of karaoke box sweep) and the default
background (the **EV Car** brand bg, `assets/bg.png`).

Adapted from the HyperFrames catalog component
[`caption-weight-shift`](https://hyperframes.heygen.com/catalog/components/caption-weight-shift)
(`npx hyperframes add caption-weight-shift`) — ported from 1920×1080 /
Montserrat / lowercase-English to 1080×1920 / IBM Plex Sans Thai, and from
line-level to word-level weight travel so it syncs to our per-word timing.

## When to use

- You have TWO videos — a screen recording (`top.mp4`) + a face cam (`bottom.mp4`).
- Output target is 1080×1920 vertical (TikTok / Reels / Shorts).
- You want the **clean, premium typographic** look — emphasis carried by font
  weight rather than coloured boxes — instead of karaoke (T05) or burst (T01).

## When NOT to use

- You want the punchy CapCut-style **karaoke box sweep** → **Template 05**.
- You want the gold-text **particle-burst** look → **Template 01**.
- There's only ONE video (no screen recording) → Template 02 / 04.

## What it produces

```
Output:  1080×1920 vertical MP4, 30 fps, H.264 / AAC
Layout:  bg.png (EV Car) → top frame (screen recording) → bottom circle (face)
         → B-roll inserts in the top frame → weight-shift captions
Captions: Weight-Shift — word-by-word font-weight travel (300 ↔ 700), gold tokens gold
Audio:   bottom audio, polished -16 LUFS target, BGM 5% + context SFX
```

## Caption system

Generated per job by `scripts/build-weightshift-captions.py` from the standard
`caption-groups.json` (same schema every template uses). It:

- reads the post-processed caption groups (group `start`/`end` + token text + `gold`)
- interpolates per-word timing inside each group by character weight
- renders every word light (300); at each word's `start` it tweens to bold
  (700) + scale 1.08, then settles back to 300 as the next word takes over
- gold tokens (`token.gold`) render in a persistent gold colour (`#f4c20f`)
  with a soft glow — no box

The same `caption-groups.json` feeds Templates 01 (burst), 05 (karaoke) and 08
(weight-shift) — switching templates does not require re-running the
post-process subagent.

See [DESIGN.md](DESIGN.md) for the full caption spec.

## How to start a new clip

```bash
# 1. Put the two source videos + bg in raw-media/
mkdir "raw-media/$(date +%Y-%m-%d)-my-clip"
#    top.mp4     = screen recording
#    bottom.mp4  = the face cam (master audio)
#    bg.png      = background (optional — template ships the EV Car default)

# 2. Scaffold
bash tools/new-job.sh 08 my-clip --raw $(date +%Y-%m-%d)-my-clip

# 3. Follow V88_PLAYBOOK.md
```

## Step 11 (composition build)

```bash
python3 scripts/set-duration.py <DURATION>
python3 scripts/build-weightshift-captions.py \
    assets/intermediates/transcript/caption-groups.json \
    compositions/captions-weightshift.html <DURATION> 360
python3 scripts/add-broll.py 15 35 55 75      # optional, B-roll in the top frame
```

`360` is the caption `bottom` offset — places the captions in the band below
the bottom face circle.

Everything else — transcribe, editorial subagent, Silero VAD, audio polish,
post-process subagent, BGM, SFX, QA — is the same v88 pipeline as Templates 01-07.

## Reference job

(none yet — the first job built on Template 08 becomes the reference.)

## Files

```
manifest.json    machine-readable spec
README.md        this file
DESIGN.md        weight-shift caption / stacked layout / colors / motion
index.html       composition source-of-truth (generic per-job paths)
hyperframes.json / meta.json / package.json
compositions/    captions-weightshift.html is generated per job;
                 components/caption-weight-shift.html = reference component (catalog)
scripts/
  set-duration.py              set composition duration
  build-weightshift-captions.py caption-groups.json → captions-weightshift.html
  build-highlight-captions.py  (kept from T05 — unused by this template)
  add-broll.py                 insert B-roll elements in the top frame
  mix-sfx.py                   context-matched SFX mix
  + shared v88 pipeline scripts (select-bgm, checks, reports …)
assets/bg.png    default background (EV Car brand)
prompts/         subagent slot defaults (editorial = stacked; post-process = captions)
```
