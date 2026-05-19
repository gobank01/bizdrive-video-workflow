# Job Notes — 2026-05-19 BIZDRIVE Video Div

## What this job is

The v88 PERFECT CHECKPOINT reference clip. First job rendered with Template 01 (stacked-vertical-burst) using the full ii23-edit-kit pipeline (ElevenLabs Scribe v2 + editorial subagent + Silero VAD + post-process subagent + particle-burst captions).

## Workspace

`workspace/` is a HyperFrames project that renders this job. It has:

- `index.html` — Template 01 composition pointing to this job's intermediates via symlink
- `compositions/captions-burst.html` — 48 burst caption groups generated from `intermediates/v88-video-div/transcript/caption-groups.json`
- `assets/v87-video-div/` → symlink to `../intermediates/v87-video-div/` (bg.png + v87 reference masters)
- `assets/v88-video-div/` → symlink to `../intermediates/v88-video-div/` (visual masters, polished WAV, transcripts)
- `assets/broll/` → symlink to `../../../templates/_shared/broll/` (5 reused Pexels clips)
- `assets/bgm/` → symlink to `../../../templates/_shared/bgm/` (Mixkit-1167)
- `.env` → symlink to `templates/_shared/env/.env`

## Why two transcripts in intermediates/

- `v87-video-div/v88-test/raw-elevenlabs.json` — transcript of ORIGINAL 130.517 s untrimmed bottom audio (used by Step 3 editorial subagent)
- `v88-video-div/transcript/raw-elevenlabs.json` — transcript of POLISHED edited 103.6 s bottom audio (used by Step 10 post-process subagent)

The first one drives the rough cut decision; the second one drives caption timing.

## Decisions specific to this job

1. **Trim start**: editorial subagent picked 24.70 s (NOT 24.00 s the user originally hinted in v87). Reason: false-start ended at 17.88, silent reset until 24.90, true speech starts at 24.90 → 200 ms head pad → 24.70.

2. **B-roll**: Reused v87's 5 Pexels selections unchanged (no PEXELS_API_KEY in .env at render time). Positions in v88 timeline are v87 positions + 0.28 s shift (head pad delta). This is "good enough" since underlying meaning hasn't moved.

3. **Caption density**: 48 groups for 103 s = ~2.15 s/group average. Denser than v87's 29 groups (~3.6 s/group). The denser version came from the post-process subagent splitting longer ElevenLabs phrase entries into 2-3 token reads.

4. **Loudness landed at -17.5 LUFS** (target -16). Acceptable. The slight under-target is from the 2-pass loudnorm chain's interaction with `apad`.

## Don't change this job

This is the LOCKED REFERENCE. If you want to iterate captions / BGM / B-roll, start a new job:

```bash
bash tools/new-job.sh 01 my-iteration-slug
# copies template, sets up workspace
```

Or experiment in a clone:

```bash
cp -r jobs/2026-05-19-bizdrive-video-div jobs/2026-05-19-bizdrive-experiment-A
```
