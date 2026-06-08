# Template 01 — Stacked Vertical with Particle-Burst Captions

**Locked at v88 (2026-05-19).** Source-of-truth for the BIZDRIVE vertical talking-head pattern.

## When to use

- Speaker has TWO clips: a screen recording (top) and a face/webcam (bottom) — already in sync
- Output target is 1080×1920 vertical (TikTok / Reels / IG Story / FB Reels / YouTube Shorts)
- Speaker is Thai (or Thai/English mixed); content references numbers, brands, AI tools
- You want AI to auto-decide rough cut + caption placement

## When NOT to use

- Single-shot horizontal footage → use Template 02 (when built)
- Square format → use Template 03 (when built)
- No talking head; pure kinetic text → use Template 04 (when built)
- Live broadcast / multi-cam interview → not yet templated

## What this template produces

```
Output:  1080×1920 vertical MP4, 30 fps, H.264 / AAC
Layout:  bg.png full-frame → top frame (rounded rectangle, top half) + bottom circle (face) → captions above bottom → B-roll inserts replace top frame contents
Captions: kinetic particle-burst, Thai-Latin mixed, gold tokens for numbers/brands
Audio:   bottom audio only (top muted), polished -16 LUFS target, BGM 5% optional
```

Reference render: `../../jobs/2026-05-19-bizdrive-video-div/output/finals/final.mp4`

## How to start a new clip with this template

```bash
# From repo root:
bash tools/new-job.sh 01 my-clip-slug

# This scaffolds: jobs/YYYY-MM-DD-my-clip-slug/{input,intermediates,output,workspace}
# Workspace has copies of index.html + compositions + scripts + symlinks to intermediates/.

# Drop your source files:
#   jobs/YYYY-MM-DD-my-clip-slug/input/top.mp4
#   jobs/YYYY-MM-DD-my-clip-slug/input/bottom.mp4
#   jobs/YYYY-MM-DD-my-clip-slug/input/bg.png

# Follow the 15-step pipeline:
#   open ../_shared/docs/V88_PLAYBOOK.md
```

## Pipeline summary (see V88_PLAYBOOK.md for details)

```
1. Inspect input media (ffprobe)
2. Transcribe bottom.mp4 with ElevenLabs Scribe v2 (--save-all 3-output mode)
3. Spawn editorial subagent → edl-rough.json   (SUBAGENT_PROMPTS.md Section A)
4. Pad-bleed validation                         (npm run rough:cut:padbleed)
5. Apply rough EDL → cleaned-rough.mp4         (npm run apply:edits)
6. Silero VAD jump-cut → edl-jump.json
7. Apply EDLs to top + bottom in parallel (lip-sync lock)
8. Polish bottom audio (2-pass loudnorm chain)
9. Re-transcribe polished audio on edited timeline
10. Spawn post-process subagent → caption-groups.json  (SUBAGENT_PROMPTS.md Section B)
11. Build composition: set-duration.py <dur> → build-burst-captions.py → (optional) add-broll.py
12. Lint + caption-gold check (npm run check, check:caption-gold)
13. HyperFrames render → visual.mp4
14. Mux speech + BGM 5% → final.mp4
15. Final QA (frame lock, silence, loudness, timestamp sheet)
16. Build thumbnail: build-thumbnail.py "<main>" "<hero>" "<sub>" → output/finals/thumbnail.png
```

The workspace `index.html` already uses generic per-job paths (`assets/input/`,
`assets/intermediates/`), so no path-fixing is needed for a new job. Only
duration / captions / B-roll are per-job — Step 11's three scripts handle them.

## Files in this template

```
manifest.json                  machine-readable spec (output dims, caption rules, golden test)
README.md                      this file
frame.md                      colors / fonts / position details
index.html                     composition source-of-truth (generic per-job paths, no inline B-roll)
hyperframes.json               HyperFrames registry config
meta.json                      project metadata
package.json                   npm scripts (lint, render, build, mux, BGM)
compositions/
  captions-burst.html          particle-burst caption sub-composition (regenerated per job from caption-groups.json)
  components/
    caption-particle-burst.html  original block from `npx hyperframes add` (reference)
scripts/
  set-duration.py              set composition duration across index.html (run per job)
  build-burst-captions.py      caption-groups.json → captions-burst.html + mount on track 3
  add-broll.py                 insert B-roll <video> elements at given start times
  generate-openrouter-broll.js AI B-roll generation (seedance-1-5-pro default)
  build-v88-composition.py     v87 → v88 timing/source swap (one-time migration; legacy)
  (other v87-era js scripts)   BGM, QA, finalize scripts
assets/
  bg.png                       default background (symlink to V2 bg.png)
backups/
  index.v87.html               v87 composition (pre-v88)
  index.v88-pre-burst.html     v88 composition before particle-burst captions
reference/
  input/                       golden test input (link to v88 reference job)
  output/                      golden test output (link to v88 reference job final)
prompts/
  editorial.md                 BIZDRIVE-specific editorial subagent defaults
  post-process.md              BIZDRIVE-specific gold-token taste
```

## Golden test

To verify this template's pipeline against the v88 reference:

```bash
cd ../../jobs/2026-05-19-bizdrive-video-div/workspace
npm run check          # must: 0 errors, 0 warnings, 10 text elements pass WCAG AA
npm run render         # must produce ~3107 frames @ 30fps, 1080×1920
```

The locked final at `jobs/2026-05-19-bizdrive-video-div/output/finals/final.mp4` is the reference.

Tolerances (from manifest.json `reference.goldenTest`):

- duration: ±50 ms
- frame count: exact (3107)
- caption groups: ±5 of 48
- gold tokens: 18-26 (target 22)
- loudness: -14 to -18 LUFS
