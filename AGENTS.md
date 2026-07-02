# AGENTS.md — BIZDRIVE Video V3

Rules for any AI agent (Claude Code, Codex, Cursor, …) working in this repo.
**This is the project rule book — read it before editing anything.**

## What this repo is

A BIZDRIVE short-video production pipeline. Source talking-head clips become
1080×1920 vertical videos with Thai kinetic captions, B-roll, BGM/SFX and a
thumbnail. The pipeline is the **v88 locked workflow** — 16 steps, documented in
`templates/_shared/docs/V88_PLAYBOOK.md`. There are 11 templates under
`templates/NN-*/`; per-clip work happens in `jobs/YYYY-MM-DD-<slug>/`.

---

## RULE 1 — The Template Manager stays in sync, always

`tools/template-manager.html` is a **standalone** display tool: a beginner picks
a template, toggles which features to run, and copies a **Job Spec** to hand to
an AI. It carries an *embedded* copy of every template's feature surface, so it
can be opened by double-click with no server.

That embedded copy must never go stale.

> **Whenever a `templates/**/manifest.json` is added or changed — or
> `templates/_shared/manager-ui.json` is edited — regenerate the manager:**
>
> ```bash
> python3 tools/build-manager.py
> ```

- `tools/new-template.sh` runs this **automatically** when scaffolding a new
  template — that path is covered.
- If you hand-edit a manifest's `features[]` (add/rename/remove a feature),
  **you must run `build-manager.py` yourself.** A stale `template-manager.html`
  is a bug.

The manager is **fully data-driven** — it hard-codes no template, feature,
section, layout or caption. Sources of truth:

| Source | Drives |
|--------|--------|
| `templates/NN-*/manifest.json` → `features[]` | the on/off toggle surface |
| `templates/_shared/manager-ui.json` | section / layout / caption labels |

Never edit `template-manager.html` by hand to add a template or feature — edit
the manifest / `manager-ui.json` and run the generator. (The only hand-editable
part is the `layoutSvg()` icon for a brand-new layout family, which is purely
cosmetic and optional.)

## RULE 2 — Honor the Job Spec

If a job carries a **Job Spec** (a `bizdrive-job-spec` JSON block, or
`jobs/<job>/job-spec.json`), it is the work order. Read it first
(V88_PLAYBOOK **Step 0**). A feature with `"on": false` means **skip** the
pipeline step(s) it owns — do not run them "to be safe". Format, schema and the
full feature→step gating table: `templates/_shared/docs/JOB_SPEC.md`.

## RULE 3 — Don't redesign the locked pipeline

The v88 16-step order is locked. The three subagent prompts in
`SUBAGENT_PROMPTS.md` (A editorial, B captions, C shorts finder) are
load-bearing — only fill the `{{...}}` slots, never rewrite them. See
`templates/_shared/docs/V88_PLAYBOOK.md` and `MISTAKES.md`.

## RULE 4 — A new *style* is a feature toggle, not a new template

Add a template only for a **structurally different** video (new aspect ratio,
new layout, new caption rendering). Color / BGM / feature on-off variations are
**Job Spec toggles**, not templates.

- New template: `bash tools/new-template.sh <NN> <slug>` → fill its
  `manifest.json` including the `features[]` block → the generator re-syncs the
  manager (see RULE 1).
- New feature: add it to the relevant manifest's `features[]` **and** a gating
  row in `JOB_SPEC.md` §3, then run `python3 tools/build-manager.py`.

**Every template MUST have a `frame.md` (its "frame spec").** This is the
design-system source of truth an agent reads BEFORE composing a clip — fixed
tokens (aspect, color, type, layout, motion, audio), so the agent fills only the
words from the script and never guesses scale or color. The name follows
HeyGen HyperFrames' `frame.md` convention (a design system inverted for the
camera); ours is **per-template** and lives next to its `manifest.json`.

- Use the canonical section schema in
  [`templates/_starter/frame.md`](_starter/frame.md). Keep the same headings, in
  the same order, for every template.
- `new-template.sh` copies the starter, so a new template gets `frame.md`
  automatically — **fill every section before the template's first job.**
- When you create or change a template's look, update its `frame.md` in the
  **same edit**. A template without a filled `frame.md` is incomplete.
- **The upstream HyperFrames skills do NOT read our `frame.md`** — they look for
  a `design.md` / `DESIGN.md` (the google-labs-code spec). Don't rely on the
  skill to auto-load `frame.md`; when composing for a template, read its
  `frame.md` yourself and treat it as the design source of truth.

## RULE 5 — Thumbnail is default-on

Every job builds and embeds a thumbnail (V88 **Step 16**) — unless a Job Spec
explicitly sets `thumbnail: 0`.

---

## Key docs

| File | What |
|------|------|
| `templates/_shared/docs/V88_PLAYBOOK.md` | the 16-step pipeline (verbatim commands) |
| `templates/_shared/docs/LONGFORM_PLAYBOOK.md` | longform → shorts user playbook (1 long video → N delivered shorts) |
| `templates/_shared/docs/JOB_SPEC.md` | Job Spec format + feature→step gating table |
| `templates/_shared/docs/SUBAGENT_PROMPTS.md` | the 3 load-bearing AI prompts (editorial, captions, shorts finder) |
| `tools/install/` | **One-click installers** for students, by OS: `windows/` (`1-INSTALL.bat`, `2-CHECK.bat` → `setup.ps1`/`check.ps1`, native no-WSL) and `mac/` (`1-INSTALL.command`, `2-CHECK.command` → wrap `tools/setup.sh`). Both ask for API keys up front. See `tools/install/README.md` |
| `tools/setup.sh` | canonical macOS/Linux install engine (Homebrew/apt + pip); the Windows `setup.ps1` is its native-Windows counterpart |
| `tools/01-longform-shorts/` | **Tool 01 — Longform → Shorts**: prep + Shorts Finder + split + helpers (see its README) |
| `tools/01-longform-shorts/shipit.sh <staging-or-source>` | one-command orchestrator: prep → Shorts Finder → split → v88-clip × N (resumable) |
| `tools/02-rough-cut/` | **Tool 02 — Rough Cut**: single raw clip → one finished rough cut (condense, no caption/template); see its README + `docs/adr/0001-2` |
| `tools/02-rough-cut/roughcut.sh <raw.mp4> [slug] [--target <sec>] [--context "..."]` | one-command: transcribe → editorial (invisible + water cuts; content cuts in `--target`) → VAD jump-cut → loudnorm → `staging/roughcut/<date>-<slug>/rough-cut.mp4` (pauses once at Step 3) |
| `tools/v88-clip.sh <job-dir>` | run all 16 v88 steps mechanically for ONE child job (pauses at Steps 3 + 10 for subagent) |
| `templates/_shared/docs/MISTAKES.md` | incident log — read before debugging |
| `templates/README.md` | the 11 templates + when to add one |
| `tools/template-manager.html` | the Job Spec builder (open in a browser) |
| `tools/03-deprompter/` | **Tool 03 — Deprompter**: remove the prompter's voice from repeat-after recordings (ElevenLabs diarize; see its README) |
| `tools/04-serial-drama/` | **Tool 04 — Serial Drama**: 30s AI short-drama series (seedance t2v + VO; see its README) |
| `tools/clean-job.sh <job-dir>` | strip a finished job to `<job>.mp4` + `<job>.png` only (keep-only-finals rule; auto-run as v88-clip Step 17) |
| `tools/inbox-sync.py` / `tools/inbox-dashboard.py` | sync the "ออกจาก Studio" inbox status to the online dashboard (bizdrive-social-poster.vercel.app/inbox.html) |
