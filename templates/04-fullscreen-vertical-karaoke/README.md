# Template 04 — Full-screen Vertical with Karaoke Highlight Captions

Created 2026-05-21. A single talking-head video fills the whole 1080×1920
vertical frame; B-roll cutaways also fill the frame. Captions use the
**BIZDRIVE Karaoke** style — a coloured box sweeps word-by-word in sync with
the speech (red for normal words, gold for brand / number / tech tokens).

Structurally identical to Template 02 — the only difference is the caption
system (karaoke box sweep instead of particle burst).

## When to use

- You have ONE video — a talking head / piece-to-camera.
- Output target is 1080×1920 vertical (TikTok / Reels / Shorts).
- You want the punchy, CapCut-style **karaoke** caption look — every word
  highlighted on beat — rather than the calmer particle-burst.

## When NOT to use

- You want the premium gold-text + particle-burst look → **Template 02**
  (same layout, different caption system).
- There's a screen recording to show alongside the face → **Template 01**.
- B-roll should sit in a floating top card, not full-screen → **Template 03**.

## What it produces

```
Output:  1080×1920 vertical MP4, 30 fps, H.264 / AAC
Layout:  bg.png (fallback) → bottom video full-screen → full-screen B-roll → scrim → captions
Captions: BIZDRIVE Karaoke — word-by-word box sweep, red box / gold box (numbers+brands)
Audio:   bottom audio, polished -16 LUFS target, BGM 5% optional
```

## Caption system

Generated per job by `scripts/build-highlight-captions.py` from the standard
`caption-groups.json` (same schema every template uses). It:

- tokenises Thai (`pythainlp`, `longest` engine), merges to ~9-16 char phrase tokens
- packs tokens into kinetic groups (≤3 tokens, ≤32 chars)
- marks gold tokens (`token.gold`) → gold box; the rest → red box
- white text, flipping to dark `#1c1206` while a gold box is active (contrast)

See [DESIGN.md](DESIGN.md) for the full caption spec.

## How to start a new clip

```bash
# 1. Put ONE video + bg in raw-media/ (no top.mp4 needed)
mkdir "raw-media/$(date +%Y-%m-%d)-my-clip"
#    bottom.mp4  = the talking head (master audio)
#    bg.png      = fallback background (optional — template ships a default)

# 2. Scaffold
bash tools/new-job.sh 04 my-clip --raw $(date +%Y-%m-%d)-my-clip

# 3. Follow V88_PLAYBOOK.md — Step 7 trims bottom only (no top)
```

## Step 11 (composition build)

```bash
python3 scripts/set-duration.py <DURATION>
python3 scripts/build-highlight-captions.py \
    assets/intermediates/transcript/caption-groups.json \
    compositions/captions-highlight.html <DURATION> 330
python3 scripts/add-broll.py 12 32 52 70      # optional, full-screen 9:16 B-roll
```

Everything else — transcribe, editorial subagent, Silero VAD, audio polish,
post-process subagent, BGM, QA — is the same v88 pipeline as Templates 01-03.

## Reference job

`jobs/2026-05-20-arm/` — Anthropic "Mythos" AI tech-news story.
1080×1920, 105.55s, 3166 frames, 65 caption groups, 18 gold tokens,
0 errors / 0 warnings on lint, WCAG AA pass.

## Files

```
manifest.json    machine-readable spec
README.md        this file
DESIGN.md        karaoke caption / layout / colors / motion
index.html       composition source-of-truth (generic per-job paths)
hyperframes.json / meta.json / package.json
compositions/    captions-highlight.html is generated per job;
                 components/caption-highlight.html = reference component
scripts/
  set-duration.py             set composition duration
  build-highlight-captions.py caption-groups.json → captions-highlight.html
  add-broll.py                insert full-screen B-roll elements
  generate-broll.js           AI B-roll generation at 9:16
  mix-sfx.py                  optional context-matched SFX
assets/bg.png    default fallback background
prompts/         subagent slot defaults
```
