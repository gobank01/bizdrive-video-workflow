# Templates

Reusable HyperFrames patterns. Each template solves a specific shape of video.

> 📸 **[CATALOG.md](CATALOG.md) — visual index with a thumbnail of every template.**
> Regenerate it with `bash tools/build-catalog.sh` after adding or changing a template.

## Comparison

| #  | Template                    | Aspect       | Use case                                          | Caption style         | Status            |
| -- | --------------------------- | ------------ | ------------------------------------------------- | --------------------- | ----------------- |
| 01 | stacked-vertical-burst      | 1080×1920    | talking-head + screen recording + B-roll (stacked) | particle burst + gold | ⭐ **locked v88** |
| 02 | fullscreen-vertical-burst   | 1080×1920    | single talking-head full-screen + full-screen B-roll | particle burst + gold | ✅ ready (2026-05-20) |
| 03 | fullscreen-top-insert-burst | 1080×1920    | single talking-head full-screen + B-roll in a floating 16:9 top insert | particle burst + gold | ✅ ready (2026-05-20) |
| 04 | fullscreen-vertical-karaoke | 1080×1920    | single talking-head full-screen + full-screen B-roll | **karaoke** highlight (red/gold box sweep) | ✅ ready (2026-05-21) |
| 05 | stacked-vertical-karaoke    | 1080×1920    | talking-head + screen recording + B-roll (stacked) | **karaoke** highlight (red/gold box sweep) | ✅ ready (2026-05-21) |
| 06 | screencast-corner-cam       | 1080×1920    | full-screen screen recording + face as a corner-cam + full-screen B-roll | particle burst + gold | ✅ ready (2026-05-21) |
| 07 | fullscreen-horizontal-karaoke | **1920×1080** | **YouTube long-form** talking-head + full-screen B-roll (~1 per 2 min) | **karaoke** highlight (red/gold box sweep) | ✅ ready (2026-05-22) |
| 08 | split-vertical-burst        | 1080×1920    | top/bottom split — screen (top) + person as full-width rectangle (bottom) | **karaoke** highlight, centered over seam | ✅ ready (2026-06-08) |
| 09 | split-vertical-burst        | 1080×1920    | top/bottom split — screen (top) + person as full-width rectangle (bottom) | particle burst + gold, centered over seam | ✅ ready (2026-06-08) |
| 10 | multimode-vertical-sweep    | 1080×1920    | single face that **cuts** between full-screen and split-top (B-roll on top half, face on bottom) | **blue word-sweep** (white→blue, no box, centered) | ✅ ready · locked (2026-06-25) |
| 11 | stacked-vertical-weightshift | 1080×1920    | talking-head + screen recording + B-roll (stacked, = T05 layout) | **weight-shift** word emphasis | ✅ ready (2026-06-01, renumbered from a parallel "08") |
| _starter_ | _skeleton_           | -            | copy via `tools/new-template.sh` for a new pattern | -                     | template          |

### Which to pick

Two axes: **layout** (do you have a screen recording?) and **caption style**
(premium particle-burst vs punchy karaoke).

- **Template 01** — TWO videos: screen recording AND face cam. Screen in the top
  frame, face in the bottom circle. **Particle-burst** captions.
- **Template 02** — ONE video: just the talking head, full-screen; B-roll
  cutaways also full-screen. **Particle-burst** captions (premium feel).
- **Template 03** — ONE video, full-screen. B-roll plays in a floating 16:9 card
  over the upper third — face stays visible around it (reaction / commentary look).
- **Template 04** — same full-screen layout as Template 02, but **karaoke**
  captions: a coloured box sweeps word-by-word (red for normal, gold for
  numbers/brands). Punchy, CapCut-style.
- **Template 05** — same stacked layout as Template 01 (screen + face), but
  **karaoke** captions instead of particle-burst.
- **Template 06** — TWO videos (screen + face), but the screen recording fills
  the whole frame and the face is a small **corner-cam** that stays on screen
  the entire clip. **Particle-burst** captions. For vertical / phone-screen
  screencasts (use Template 01 for 16:9 desktop captures).
- **Template 07** — first **16:9 horizontal** template (1920×1080), built for
  **YouTube long-form** cuts. Full-screen talking-head + full-screen B-roll +
  **karaoke** captions. B-roll is long-form cadence (≥120s spacing, 4s each,
  ~1 per 2 minutes) instead of the 9:16 sparse-4/60s rule. Thumbnail default OFF
  (use a separate 1280×720 YouTube cover).
- **Template 08** — TWO videos in a clean top/bottom **split**: screen recording
  on top, person as a full-width **rectangle** (no circle) on the bottom.
  **Karaoke** captions centered over the seam.
- **Template 09** — **same split layout as Template 08** (screen on top, person
  rectangle on bottom), but **particle-burst** captions (gold #FFD700, Template 01
  colors) centered over the seam, instead of karaoke. The burst↔karaoke pair, like
  01 ↔ 05. (Note: Template 08's folder is named `…-burst` but it is the *karaoke*
  one — historical mislabel; T09 is the actual particle-burst split.)
- **Template 11** — same stacked layout as Template 05, but captions use
  **weight-shift** typography: the active word becomes bold while the rest stay
  light. Cleaner and more premium than karaoke. (Authored upstream as a parallel
  "Template 08"; renumbered to 11 at merge because 08 was already the split
  karaoke in production.)

- **Template 10** — one full-screen face that **cuts between two display
  states** within a single clip: full-screen, and **split-top** (B-roll/screen
  fills the top half, face drops to a full-bleed bottom rectangle). The mode is
  chosen per B-roll insert, so the locked v88 pipeline is unchanged (single face =
  audio master). Captions are a clean **blue word-sweep** — every word white, the
  spoken word pops to blue, no box / no particles, centered over the seam. Built
  from the Top1% / อาจารย์อริน reference look. **Locked 2026-06-25** — full
  production playbook in [10-multimode-vertical-sweep/RECIPE.md](10-multimode-vertical-sweep/RECIPE.md)
  (out-of-studio slides+face → 3-beat clip; face-first framing; OpenRouter AI inserts).

> **Same layout, different captions:** 01 ↔ 05 (stacked circle) · 08 ↔ 09
> (split screen+person) · 02 ↔ 04 (full-screen).
> Particle-burst = premium/calm; karaoke box sweep = punchy/viral.
> The `caption-groups.json` is identical for both — only the Step 11 build script
> differs (`build-burst-captions.py` vs `build-highlight-captions.py`).

## When to add a new template

Add a template when you need a **structurally different** video — different aspect ratio, different layout (PiP vs stacked vs full-screen), different caption rendering approach. Don't add templates for color/font/BGM swaps — those are variations within a template.

Examples that warrant new templates:

- 1920×1080 horizontal talking-head with side caption strip
- 1080×1080 square quote card with no video, only text + bg
- 9:16 full-screen kinetic typography (no talking head)
- Split-screen interview (two people, side-by-side or stacked) — not yet built

Examples that do NOT need new templates:

- Different brand color / font (use HyperFrames variables inside Template 01)
- Different BGM (swap `--bgm` flag in mix:bgm)
- Different B-roll selections (B-roll picks per job)

## Creating a new template

```bash
bash tools/new-template.sh 02 horizontal-talking-head
# Customize templates/02-horizontal-talking-head/:
#   - manifest.json  (aspect, fps, caption style, gold rule, features[])
#   - index.html     (composition layout)
#   - frame.md      (colors, fonts, position)
#   - prompts/       (subagent slot defaults specific to this template)
```

`new-template.sh` runs `tools/build-manager.py` automatically, so the new
template appears in the Template Manager (`tools/template-manager.html`) right
away. **After you edit the new `manifest.json` — especially its `features[]`
block — re-run `python3 tools/build-manager.py`** so the manager picks up the
real values. This sync is a project rule; see [AGENTS.md](../AGENTS.md) RULE 1.

## Shared infrastructure (`_shared/`)

Every template inherits these. Do NOT duplicate per-template:

- `scripts/transcribe/` — ElevenLabs Scribe v2 + nlpo3 word-segmentation
- `scripts/clean-cut/` — Silero VAD + editorial pad-bleed
- `docs/V88_PLAYBOOK.md` — 16-step pipeline (+ Step 17 cleanup in `tools/v88-clip.sh`)
- `docs/SUBAGENT_PROMPTS.md` — verbatim editorial + post-process prompts
- `docs/MISTAKES.md` — incidents log shared across all templates
- `references/editorial-rules.md` — editorial subagent rules
- `references/post-process-protocol.md` — caption text-fix rules
- `bgm-library/` + `bgm/` — BGM stock JSON + mp3 files
- `broll/` — B-roll stock library
- `env/.env` — API keys (gitignored)
