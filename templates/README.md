# Templates

Reusable HyperFrames patterns. Each template solves a specific shape of video.

## Comparison

| #  | Template                    | Aspect       | Use case                                   | Caption style       | Status        |
| -- | --------------------------- | ------------ | ------------------------------------------ | ------------------- | ------------- |
| 01 | stacked-vertical-burst      | 1080×1920    | BIZDRIVE talking-head + screen + B-roll    | particle burst + gold | ⭐ **locked v88** |
| 02 | _starter_                   | -            | (skeleton for new templates)               | -                   | template       |

## When to add a new template

Add a template when you need a **structurally different** video — different aspect ratio, different layout (PiP vs stacked vs full-screen), different caption rendering approach. Don't add templates for color/font/BGM swaps — those are variations within a template.

Examples that warrant new templates:

- 1920×1080 horizontal talking-head with side caption strip
- 1080×1080 square quote card with no video, only text + bg
- 9:16 full-screen kinetic typography (no talking head)
- Split-screen interview (two faces stacked)

Examples that do NOT need new templates:

- Different brand color / font (use HyperFrames variables inside Template 01)
- Different BGM (swap `--bgm` flag in mix:bgm)
- Different B-roll selections (B-roll picks per job)

## Creating a new template

```bash
bash tools/new-template.sh 02 horizontal-talking-head
# Customize templates/02-horizontal-talking-head/:
#   - manifest.json  (aspect, fps, caption style, gold rule)
#   - index.html     (composition layout)
#   - DESIGN.md      (colors, fonts, position)
#   - prompts/       (subagent slot defaults specific to this template)
```

## Shared infrastructure (`_shared/`)

Every template inherits these. Do NOT duplicate per-template:

- `scripts/transcribe/` — ElevenLabs Scribe v2 + nlpo3 word-segmentation
- `scripts/clean-cut/` — Silero VAD + editorial pad-bleed
- `docs/V88_PLAYBOOK.md` — 15-step pipeline
- `docs/SUBAGENT_PROMPTS.md` — verbatim editorial + post-process prompts
- `docs/MISTAKES.md` — incidents log shared across all templates
- `references/editorial-rules.md` — editorial subagent rules
- `references/post-process-protocol.md` — caption text-fix rules
- `bgm-library/` + `bgm/` — BGM stock JSON + mp3 files
- `broll/` — B-roll stock library
- `env/.env` — API keys (gitignored)
