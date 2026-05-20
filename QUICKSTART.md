# Quickstart

From GitHub to a rendered video. One page. (Full detail: [ONBOARDING.md](ONBOARDING.md) → [V88_PLAYBOOK.md](templates/_shared/docs/V88_PLAYBOOK.md))

## What it does

Two synced clips (screen recording + talking-head face) → one 1080×1920
vertical video: AI auto-trims the rough cut, generates kinetic Thai captions,
inserts AI B-roll, mixes BGM.

## 0. Prerequisites

`python3` 3.10+ · `node` 18+ · `ffmpeg` + `ffprobe` · `git`
Plus your own API keys: **ElevenLabs** (required), **OpenRouter** (optional, B-roll).

## 1. Clone & set up — once

```bash
git clone https://github.com/gobank01/bizdrive-video-workflow.git
cd bizdrive-video-workflow
bash tools/setup.sh                      # deps + Silero VAD + .env  (~5-10 min)
```

Add keys to `templates/_shared/env/.env`:

```
ELEVENLABS_API_KEY=sk_...                # elevenlabs.io/app/settings/api-keys
OPENROUTER_API_KEY=sk-or-v1-...          # openrouter.ai/keys  (only for B-roll)
```

## 2. Add a clip

```bash
mkdir "raw-media/$(date +%Y-%m-%d)-my-clip"
# drop 3 files in, named exactly:
#   top.mp4     screen recording (muted in final)
#   bottom.mp4  face video (the master audio)
#   bg.png      background image
```

`top.mp4` and `bottom.mp4` must be the same length — recorded in sync.

## 3. Scaffold the job

```bash
bash tools/new-job.sh 01 my-clip --raw $(date +%Y-%m-%d)-my-clip
```

## 4. Run the pipeline

**Easiest — Claude Code:** open the repo, say `ตัดต่อ my-clip`. It runs all 15 steps.

**Manual / other agent:** follow [V88_PLAYBOOK.md](templates/_shared/docs/V88_PLAYBOOK.md)
Steps 1-15. The two AI steps (3 = rough cut, 10 = captions) use the prompts in
[SUBAGENT_PROMPTS.md](templates/_shared/docs/SUBAGENT_PROMPTS.md) — fill the
`{{...}}` slots, hand to any capable AI agent.

The 15 steps in brief:

| # | Step | How |
| - | ---- | --- |
| 1 | inspect media | `ffprobe` |
| 2 | transcribe (ElevenLabs) | `transcribe.py` |
| 3 | **editorial rough cut** | AI subagent — prompt A |
| 4-7 | pad-bleed → VAD → trim top+bottom | scripts |
| 8-9 | polish audio → re-transcribe | ffmpeg + `transcribe.py` |
| 10 | **caption text fix + grouping** | AI subagent — prompt B |
| 11 | build composition | `set-duration.py`, `build-burst-captions.py`, `add-broll.py` |
| 12 | lint | `npm run check` |
| 13 | render | `npx hyperframes render` |
| 14 | B-roll gen + mux speech + BGM 5% | scripts + ffmpeg |
| 15 | final QA | ffprobe + `qa:timestamps` |

## 5. Result

```
jobs/<date>-my-clip/output/finals/final.mp4
```

## Verify your setup (optional)

Ask the maintainer for `sample-pack-v88.zip`, unzip into `raw-media/`, run the
pipeline on it, and compare your output's ffprobe numbers to
`templates/01-stacked-vertical-burst/manifest.json` → `reference.goldenTest`
(≈103.5s, 3107 frames, 48±5 caption groups, -14 to -18 LUFS).

## Cost & time per clip

ElevenLabs ~$0.024 · 2 subagent calls ~$0.6-1.2 · B-roll ~$0.08 · ~15 min total.

## Rules that matter

- Bottom audio is the master timeline; top is muted. Trims are parallel.
- Don't rewrite the subagent prompts — fill the slots only.
- A structurally different video = a new template, not an edit to Template 01.
- Never commit `.env` or large media (both gitignored).

More: [README.md](README.md) · [ONBOARDING.md](ONBOARDING.md) · [CONTRIBUTING.md](CONTRIBUTING.md)
