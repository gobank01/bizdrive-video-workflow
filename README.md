# Video V3 — BIZDRIVE Video Template System

Multi-template HyperFrames video production. Each template is a reusable pattern (aspect ratio, layout, caption style). Each job is one rendered video.

**Status:** Template 01 locked at v88 (PERFECT CHECKPOINT, 2026-05-19).

> **New here / received this repo to develop further?** Read **[ONBOARDING.md](ONBOARDING.md)** first — it walks you from a fresh clone to your first rendered video.

## 🚀 Fresh setup (clone → ready)

```bash
git clone https://github.com/<your-username>/bizdrive-video-workflow.git
cd bizdrive-video-workflow
bash tools/setup.sh                       # installs deps + Silero VAD + .env
# then edit templates/_shared/env/.env — add your ElevenLabs + OpenRouter keys
```

Then follow [ONBOARDING.md](ONBOARDING.md). Optional: ask the maintainer for
`sample-pack-v88.zip` to run the golden test.

---

## 📁 Repo layout

```
Video V3/
├── templates/                          เก็บ pattern ทั้งหมด
│   ├── README.md                       ตารางเปรียบเทียบ templates
│   ├── _shared/                        infra ใช้ร่วมทุก template
│   │   ├── scripts/                    transcribe (ElevenLabs) + clean-cut (Silero VAD)
│   │   ├── docs/                       V88_PLAYBOOK + SUBAGENT_PROMPTS + WORKFLOW + etc.
│   │   ├── prompts/                    canonical editorial + post-process prompts
│   │   ├── references/                 editorial-rules + post-process-protocol
│   │   ├── bgm-library/                BGM stock JSON
│   │   ├── bgm/                        BGM mp3 files
│   │   ├── broll/                      B-roll stock library
│   │   ├── schemas/                    JSON schemas
│   │   ├── brand-kit/                  logos, fonts, brand colors
│   │   └── env/                        .env (gitignored) + .env.example
│   │
│   ├── 01-stacked-vertical-burst/      ⭐ Template 1: v88 stacked vertical + burst captions
│   │   ├── README.md                   เมื่อไหร่ใช้, output spec
│   │   ├── manifest.json               machine-readable spec
│   │   ├── DESIGN.md                   colors/fonts/position
│   │   ├── index.html                  composition source-of-truth
│   │   ├── compositions/               sub-compositions (captions-burst.html)
│   │   ├── scripts/                    per-template build scripts
│   │   ├── assets/                     template default assets (bg.png)
│   │   ├── prompts/                    template-specific subagent slot defaults
│   │   ├── backups/                    previous composition versions
│   │   └── reference/                  golden test (input + expected output + tolerances)
│   │
│   └── _starter/                       skeleton ใช้สร้าง template ใหม่
│
├── jobs/                               งานจริงรายคลิป
│   └── 2026-05-19-bizdrive-video-div/  v88 reference job
│       ├── manifest.json               { template, source, date }
│       ├── input/                      source media (or symlinks to /video div/)
│       ├── intermediates/              raw transcript, EDLs, visual masters, polished WAV
│       ├── output/finals/              final.mp4 + visual.mp4 + no-bgm.mp4
│       └── workspace/                  HyperFrames project — render happens here
│           ├── index.html              copy of template-01 index
│           ├── compositions/           copy of template-01 compositions
│           ├── scripts/                template scripts + symlinks to _shared
│           ├── assets/                 symlinks: v87-video-div, v88-video-div, broll, bgm
│           ├── bgm-library/            symlink to _shared
│           └── package.json
│
├── tools/                              repo-wide CLI
│   ├── new-job.sh                      สร้าง job ใหม่จาก template
│   └── new-template.sh                 สร้าง template ใหม่จาก _starter
│
├── archive/                            v80/v87 historical artifacts (preserved)
├── robot/                              (unrelated; user's other work)
├── video/  video div/  video2/         original source media folders
└── test 2/                             original test materials
```

---

## 🚀 Quick start

### Render the v88 reference job (golden test)

```bash
cd "jobs/2026-05-19-bizdrive-video-div/workspace"
npm run check                # lint + validate + inspect
npm run render               # render visual-only
# Then mux speech + BGM following templates/_shared/docs/V88_PLAYBOOK.md Step 14
```

### Start a new clip with Template 01

```bash
# Scaffold
bash tools/new-job.sh 01 my-slug
# Creates jobs/YYYY-MM-DD-my-slug/ with workspace ready

# Drop input files into jobs/YYYY-MM-DD-my-slug/input/{top.mp4, bottom.mp4, bg.png}
# Then follow templates/_shared/docs/V88_PLAYBOOK.md Steps 1-15
```

### Create a new template (pattern 02+)

```bash
bash tools/new-template.sh 02 horizontal-talking-head
# Clones templates/_starter/ → templates/02-horizontal-talking-head/
# Customize manifest.json, index.html, DESIGN.md before first job
```

---

## 🤖 Porting to a different AI agent

The pipeline is stateless. Two AI-driven steps:

1. **Editorial subagent** (rough cut) — see `templates/_shared/docs/SUBAGENT_PROMPTS.md` Section A
2. **Post-process subagent** (caption text fix + grouping) — Section B

Drop those prompts verbatim into any agent (Claude API, Codex CLI, Cursor, GPT, Gemini). Everything else is deterministic Python/ffmpeg/Node.

---

## 📦 v88 Reference output

```
jobs/2026-05-19-bizdrive-video-div/output/finals/final.mp4
  1080×1920, 30 fps, 103.587s, 3107 frames
  AI auto-trimmed start 24.70s, end 130.27s (false start + outro music auto-dropped)
  48 burst caption groups, 22 gold particle bursts + 66 white
  Mixkit-1167 Close Up BGM at 5%, frame-lock preserved
  0 errors / 0 warnings on npm run check
```

---

## 📚 Required reading (in order)

1. `templates/_shared/docs/V88_PLAYBOOK.md` — 15-step pipeline
2. `templates/_shared/docs/SUBAGENT_PROMPTS.md` — verbatim AI prompts
3. `templates/_shared/docs/WORKFLOW.md` — full BIZDRIVE workflow
4. `templates/_shared/docs/MISTAKES.md` — past incidents + fixes (v67-v88)
5. `templates/01-stacked-vertical-burst/README.md` — Template 01 specifics

---

## 🔐 Security

`.env` is gitignored at `templates/_shared/env/.env`. Never commit secrets.
The ELEVENLABS_API_KEY currently in .env was exposed during the v88 session — rotate before sharing this repo.
