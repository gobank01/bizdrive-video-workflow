# CLAUDE.md — BIZDRIVE Video V3

**Read [AGENTS.md](AGENTS.md) first — it is the project rule book.** It defines
the Template Manager sync rule, the Job Spec rule, the locked v88 pipeline, and
when to add a template. Every rule there applies to Claude Code.

## Claude Code specifics

- **Skills:** invoke `bizdrive-video` for editing/producing clips, and the
  `hyperframes` family for HyperFrames composition authoring. The HyperFrames
  skill table is in `templates/_shared/docs/CLAUDE.md`.
- **Template Manager sync (AGENTS.md RULE 1) is mechanical — never skip it.**
  After any Edit/Write to a `templates/**/manifest.json` or to
  `templates/_shared/manager-ui.json`, run:
  ```bash
  python3 tools/build-manager.py
  ```
  `tools/new-template.sh` already does this for new templates. For hand-edits to
  an existing manifest, run it yourself. If you want it enforced automatically,
  it can be wired as a `PostToolUse` hook in `.claude/settings.json` (matcher
  `Edit|Write|MultiEdit`).
- Per-clip work lives in `jobs/YYYY-MM-DD-<slug>/`; scaffold with
  `bash tools/new-job.sh <NN> <slug> --raw <raw-slug>`.

## Quick map

- `templates/NN-*/` — the 5 locked templates; each `manifest.json` has a
  `features[]` block (the Template Manager's toggle surface)
- `templates/_shared/` — pipeline scripts, docs, schemas, BGM/SFX/B-roll, and
  `manager-ui.json` (UI labels)
- `tools/` — `new-job.sh`, `new-template.sh`, `build-manager.py`,
  `build-catalog.sh`, `template-manager.html`
- `jobs/` — per-clip work orders, intermediates and renders
