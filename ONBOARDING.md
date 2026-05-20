# Onboarding — BIZDRIVE Video Workflow

You've received this repo to develop it further. This guide takes you from a
fresh clone to your first rendered video. ~30 minutes including installs.

The repo turns two synced clips (a screen recording + a talking-head face
video) into a polished 1080×1920 vertical video — AI auto-trims the rough cut,
generates kinetic Thai captions, inserts AI B-roll, and mixes BGM.

---

## 1. Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.10+ | `brew install python` / `apt-get install python3` |
| Node.js | 18+ | `brew install node` / `apt-get install nodejs` |
| ffmpeg + ffprobe | any modern | `brew install ffmpeg` / `apt-get install ffmpeg` |
| git | any | — |

You also need (paid, your own accounts):

- **ElevenLabs** API key — Thai speech-to-text. ~$0.024 per 100s clip. Required.
- **OpenRouter** API key — AI B-roll generation. ~$0.02 per clip. Optional (skip if no B-roll).

---

## 2. Fork & clone

This repo is `gobank01/bizdrive-video-workflow`. To develop independently:

1. **Fork** it on GitHub (your own copy, separate from the original).
2. Clone your fork:

```bash
git clone https://github.com/<your-username>/bizdrive-video-workflow.git
cd bizdrive-video-workflow
```

---

## 3. One-command setup

```bash
bash tools/setup.sh
```

This installs Python deps (pythainlp, nlpo3, certifi), the Silero VAD venv
(~437 MB into `~/.ii23/vad-env`), and creates the `.env` file.

Then add your API keys:

```bash
open templates/_shared/env/.env     # or edit in any editor
```

```
ELEVENLABS_API_KEY=sk_your_key_here
OPENROUTER_API_KEY=sk-or-v1-your_key_here   # optional, for B-roll
```

⚠️ `.env` is gitignored — your keys never get committed. Keep it that way.

---

## 4. Verify with the golden test (optional but recommended)

The maintainer can give you a **sample pack** (`sample-pack-v88.zip`) — the v88
reference clip's raw footage + expected output. It is NOT in the repo (too large).

```bash
# Unzip the sample pack into raw-media/
unzip sample-pack-v88.zip -d raw-media/

# Scaffold a job from it
bash tools/new-job.sh 01 golden-test --raw 2026-04-23-bizdrive-stock-promo

# Run the pipeline (see V88_PLAYBOOK.md) and compare your final.mp4 to the
# reference. Tolerances are in templates/01-stacked-vertical-burst/manifest.json
# under reference.goldenTest.
```

If your output lands within tolerance, your environment is correct.

---

## 5. Your first real job

```bash
# 1. Put your clip's raw files in raw-media/
mkdir "raw-media/$(date +%Y-%m-%d)-my-clip"
#    drop top.mp4 (screen), bottom.mp4 (face), bg.png (background) into it

# 2. Scaffold the job
bash tools/new-job.sh 01 my-clip --raw $(date +%Y-%m-%d)-my-clip

# 3. Run the 15-step pipeline
open templates/_shared/docs/V88_PLAYBOOK.md
```

Steps 3 and 10 spawn an AI subagent — prompts are in
`templates/_shared/docs/SUBAGENT_PROMPTS.md` (Section A = editorial rough cut,
Section B = caption post-process). They work with any capable AI agent.

---

## 6. Repo map (where things live)

```
templates/
  _shared/          infra used by every template
    docs/           V88_PLAYBOOK.md, SUBAGENT_PROMPTS.md, WORKFLOW.md, MISTAKES.md, ...
    scripts/        transcribe (ElevenLabs) + clean-cut (Silero VAD) tools
    references/     editorial-rules.md, post-process-protocol.md
    env/            .env (your keys, gitignored) + .env.example
  01-stacked-vertical-burst/   the locked v88 pattern (Template 01)
  _starter/         skeleton for building a new template
jobs/               one folder per video produced
tools/              setup.sh, new-job.sh, new-template.sh
raw-media/          source clips (gitignored — bring your own)
```

**Read in this order:**
1. `templates/_shared/docs/V88_PLAYBOOK.md` — the 15-step pipeline
2. `templates/_shared/docs/SUBAGENT_PROMPTS.md` — the AI prompts
3. `templates/_shared/docs/MISTAKES.md` — past incidents + fixes
4. `templates/01-stacked-vertical-burst/README.md` — Template 01 specifics

---

## 7. Things to know before you change code

- **Subagent prompts are load-bearing.** Don't rewrite `SUBAGENT_PROMPTS.md`
  Sections A/B — only fill the `{{...}}` slots. Every clause is there because
  of a past failure (see MISTAKES.md).
- **Bottom audio is the master timeline.** Top is muted. Trims are always
  parallel across top + bottom (same EDL) — this preserves lip sync.
- **Edit-first.** All cuts happen before HyperFrames layout.
- **A new structural pattern = a new template** (`tools/new-template.sh`), not
  an edit to Template 01. Template 01 is the locked v88 baseline.
- The dangling symlinks under existing `jobs/*/` point to gitignored media —
  that's expected; those are the maintainer's past runs. Your new jobs are
  self-contained.

---

## 8. Cost & expectations per clip

```
ElevenLabs STT     ~$0.024   (2 calls — raw + edited timeline)
Editorial subagent ~$0.30-0.60   (one Claude-Opus-class call)
Post-process subagent ~$0.30-0.60
B-roll (optional)  ~$0.08    (4 clips × seedance-1-5-pro)
Render time        ~3 min per render (2 renders typical)
End-to-end         ~15 min for a clean 90-second clip
```

---

## 9. Getting unstuck

- `npm run preflight` (from a workspace) — checks the environment
- `templates/_shared/docs/MISTAKES.md` — known failure modes + fixes
- `templates/_shared/docs/V88_PLAYBOOK.md` section 8 — known imperfections
- Golden test (section 4 above) — confirms your environment matches the reference
