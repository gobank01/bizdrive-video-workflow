# Template 09 — Side-by-Side Two-Person (Vertical) with Particle-Burst Captions

**Created 2026-06-08 (v88).** Two talking-head cams placed **side by side**
(left + right rectangles) in a 1080×1920 frame — an interview / conversation /
2-cam podcast layout — with **BIZDRIVE particle-burst captions** (same word-pop
+ gold #FFD700 system as Template 01) centered **over the seam between the two
cams**. New side-by-side layout family; caption system identical to Template 01.

Pipeline contract is the same as Template 08 (`bottom.mp4` = audio master,
`top.mp4` = muted second cam), so the locked v88 16-step flow is unchanged —
only the composition geometry (left/right) and caption position differ.

## When to use

- TWO cams of a **2-person interview / conversation / podcast** recorded with one
  combined audio track (room/interview mic) on `bottom.mp4`
- `top.mp4` = the second person's cam (video only — it is muted in the composition)
- Output target is 1080×1920 vertical (TikTok / Reels / IG Story / FB Reels / YouTube Shorts)
- Speaker(s) Thai (or Thai/English mixed); content references numbers, brands, AI tools
- You want the punchy particle-burst caption look (Template 01 colors)

## When NOT to use

- Single talking head → use Template 01/02/04/05
- Screen recording + face → use Template 06 (corner-cam) or Template 08 (top/bottom split)
- Karaoke word-sweep caption look → use Template 04/05/08
- **Separate per-speaker mics that need a two-track mixdown** → out of scope; this
  template assumes ONE combined audio track on `bottom.mp4`
- 16:9 horizontal / 1:1 square → not this template

## What this template produces

```
Output:  1080×1920 vertical MP4, 30 fps, H.264 / AAC
Layout:  bg.png full-frame → LEFT cam (rounded rectangle) + RIGHT cam (rounded rectangle), side by side → particle-burst captions centered over the seam → B-roll inserts cover the LEFT cam
Captions: particle-burst word-pop, Thai-Latin mixed, gold #FFD700 for numbers/brands
Audio:   bottom.mp4 combined audio (top muted), polished -16 LUFS target, BGM 5% optional
```

Reference render: none locked yet (new template — validate on a real 2-cam job).

## How to start a new clip with this template

```bash
# From repo root:
bash tools/new-job.sh 09 my-clip-slug

# Drop your source files:
#   jobs/YYYY-MM-DD-my-clip-slug/input/bottom.mp4   (cam B = RIGHT, carries the combined audio = master)
#   jobs/YYYY-MM-DD-my-clip-slug/input/top.mp4      (cam A = LEFT, video only / muted)
#   jobs/YYYY-MM-DD-my-clip-slug/input/bg.png

# Then run the locked pipeline (pauses at Steps 3 + 10 for subagents):
bash tools/v88-clip.sh jobs/YYYY-MM-DD-my-clip-slug
```

> Note (same caveat as T01/T05/T08, see memory `v88-clip-top-master-bug`):
> v88-clip.sh applies the EDLs to `bottom.mp4`; the second cam `top.mp4` must be
> brought onto the same edited timeline (`top_visual_master.mp4`) — run
> `apply:edits` for top in parallel so left/right stay frame-locked.

## Pipeline summary (see V88_PLAYBOOK.md for details)

```
1. Inspect input media (ffprobe)
2. Transcribe bottom.mp4 with ElevenLabs Scribe v2
3. Editorial subagent → edl-rough.json            (SUBAGENT_PROMPTS.md Section A)
4. Pad-bleed validation
5. Apply rough EDL → cleaned-rough.mp4
6. Silero VAD jump-cut → edl-jump.json
7. Apply EDLs to top + bottom in parallel (lip-sync lock)
8. Polish bottom audio (2-pass loudnorm chain)
9. Re-transcribe polished audio on edited timeline
10. Post-process subagent → caption-groups.json   (SUBAGENT_PROMPTS.md Section B)
11. Build composition: set-duration.py <dur> → build-burst-captions.py (reads caption-groups.json + duration; caption position hardcoded at bottom 910 = centered over seam) → (optional) add-broll.py
12. Lint + caption-gold check (npm run check, check:caption-gold)
13. HyperFrames render → visual.mp4
14. Mux speech + BGM 5% → final.mp4
15. Final QA (frame lock, silence, loudness)
16. Build thumbnail → output/finals/<clip>.png + embed cover
```

## Files in this template

```
manifest.json                  machine-readable spec (output dims, caption rules, golden test)
README.md / DESIGN.md          this file / colors-fonts-position details
index.html                     composition source-of-truth (side-by-side geometry, generic per-job paths)
hyperframes.json / meta.json   HyperFrames registry config / project metadata
package.json                   npm scripts (lint, render, build, mux, BGM)
compositions/
  captions-burst.html          particle-burst sub-composition (regenerated per job by build-burst-captions.py)
  components/                   reference caption blocks from `npx hyperframes add`
scripts/
  set-duration.py              set composition duration across index.html (run per job)
  build-burst-captions.py      caption-groups.json → captions-burst.html (particle-burst; index.html mounts it)
  add-broll.py                 insert B-roll <video> after #topVideo (lands in the LEFT frame)
  generate-openrouter-broll.js AI B-roll generation (seedance-1-5-pro default)
  build-thumbnail.py           Step 16 thumbnail + cover embed
  (other v87-era js scripts)   BGM, QA, finalize scripts
assets/bg.png                  default background
prompts/                       BIZDRIVE editorial + gold-token subagent defaults
```

## Golden test

No locked golden reference yet (new template, 2026-06-08). After the first real
2-cam render, lock it here and fill `manifest.json reference.goldenTest`. The
preview bar to clear before locking:

```bash
cd ../../jobs/<a-real-2cam-job>/workspace
npm run check          # must: 0 errors, 0 layout issues; captions centered at bottom 360
```
