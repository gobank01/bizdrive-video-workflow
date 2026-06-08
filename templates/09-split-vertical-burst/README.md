# Template 09 — Split Vertical (Screen + Person) with Particle-Burst Captions

**Created 2026-06-08 (v88).** Clean top/bottom split — top frame is the screen
recording (top.mp4), bottom frame is the **person as a full-width rectangle**
(bottom.mp4) — with **BIZDRIVE particle-burst captions** (same word-pop + gold
#FFD700 system as Template 01) centered **over the seam**.

The **particle-burst sibling of Template 08**: identical split layout, only the
caption renderer differs (T08 = karaoke word-sweep, T09 = particle-burst) — the
same relationship as Template 01 ↔ 05.

## When to use

- Speaker has TWO clips: a screen recording (top) and a face/webcam (bottom) — already in sync
- You want the punchy particle-burst caption look (gold #FFD700) instead of the karaoke box sweep (Template 08)
- Output target is 1080×1920 vertical (TikTok / Reels / IG Story / FB Reels / YouTube Shorts)
- Speaker is Thai (or Thai/English mixed); content references numbers, brands, AI tools

## When NOT to use

- Karaoke word-sweep caption look → use Template 08 (same layout, karaoke)
- Circle face bottom → use Template 01 (burst) / Template 05 (karaoke)
- Single full-screen talking head (no screen) → use Template 02 / 04
- Screen recording with the face as a small corner-cam → use Template 06
- 16:9 horizontal / 1:1 square → not this template

## What this template produces

```
Output:  1080×1920 vertical MP4, 30 fps, H.264 / AAC
Layout:  bg.png full-frame → top frame (screen, rounded rectangle) + bottom frame (person, rectangle) → particle-burst captions centered over the seam → B-roll inserts cover the TOP (screen) frame
Captions: particle-burst word-pop, Thai-Latin mixed, gold #FFD700 for numbers/brands
Audio:   bottom.mp4 audio only (top/screen muted), polished -16 LUFS target, BGM 5% optional
```

Reference render: none locked yet (new template). Validated end-to-end on a
reused clip (Claude Code ยากไหม): lint 0 errors / 0 layout issues, final.mp4
-16.4 LUFS.

## How to start a new clip with this template

```bash
# From repo root:
bash tools/new-job.sh 09 my-clip-slug

# Drop your source files:
#   jobs/YYYY-MM-DD-my-clip-slug/input/top.mp4      (screen recording = top frame)
#   jobs/YYYY-MM-DD-my-clip-slug/input/bottom.mp4   (person = bottom frame, audio master)
#   jobs/YYYY-MM-DD-my-clip-slug/input/bg.png

# Then run the locked pipeline (pauses at Steps 3 + 10 for subagents):
bash tools/v88-clip.sh jobs/YYYY-MM-DD-my-clip-slug
```

> Note (same caveat as T01/T05/T08, see memory `v88-clip-top-master-bug`):
> v88-clip.sh applies the EDLs to `bottom.mp4`; the screen `top.mp4` must be
> brought onto the same edited timeline (`top_visual_master.mp4`) — run
> `apply:edits` for top in parallel so screen + person stay frame-locked.

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
11. Build composition: set-duration.py <dur> → build-burst-captions.py (caption position bottom 910 = centered over seam, hardcoded) → (optional) add-broll.py
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
index.html                     composition source-of-truth (split top/bottom geometry, generic per-job paths)
hyperframes.json / meta.json   HyperFrames registry config / project metadata
package.json                   npm scripts (lint, render, build, mux, BGM)
compositions/
  captions-burst.html          particle-burst sub-composition (regenerated per job by build-burst-captions.py)
  components/                   reference caption blocks from `npx hyperframes add`
scripts/
  set-duration.py              set composition duration across index.html (run per job)
  build-burst-captions.py      caption-groups.json → captions-burst.html (particle-burst; caption bottom 910 hardcoded)
  add-broll.py                 insert B-roll <video> after #topVideo (lands in the TOP/screen frame)
  generate-openrouter-broll.js AI B-roll generation (seedance-1-5-pro default)
  build-thumbnail.py           Step 16 thumbnail + cover embed
  (other v87-era js scripts)   BGM, QA, finalize scripts
assets/bg.png                  default background
prompts/                       BIZDRIVE editorial + gold-token subagent defaults
```

## Golden test

No locked golden reference yet (new template, 2026-06-08). After the first
purpose-built render, lock it here and fill `manifest.json reference.goldenTest`.
Bar to clear before locking:

```bash
cd ../../jobs/<a-real-job>/workspace
npm run check          # must: 0 errors, 0 layout issues; captions centered over seam (bottom 910)
```
