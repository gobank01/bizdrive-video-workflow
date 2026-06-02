# CLAUDE.md — BIZDRIVE Video V3

**Read [AGENTS.md](AGENTS.md) first — it is the project rule book.** It defines
the Template Manager sync rule, the Job Spec rule, the locked v88 pipeline, and
when to add a template. Every rule there applies to Claude Code.

## First-run setup (auto-install)

If a user asks you to "install", "set up", or "get this working" — or if a
pipeline command fails because `ffmpeg`, `python3`, `node`, or the Silero VAD
venv is missing — run the one setup script. It is OS-aware and **auto-installs**
missing system tools (macOS via Homebrew, Linux/WSL via apt/dnf):

```bash
bash tools/setup.sh
```

Then create the API-key file and ask the user for their keys (never invent them):

```
templates/_shared/env/.env
  ELEVENLABS_API_KEY=...        # required — https://elevenlabs.io/app/settings/api-keys
  OPENROUTER_API_KEY=...        # optional, B-roll — https://openrouter.ai/keys
```

Windows users run inside **WSL/Ubuntu** (the human bootstrap is in
[INSTALL.md](INSTALL.md)); from your side WSL is just Linux, so `tools/setup.sh`
works unchanged. If `setup.sh` reports a tool it could not auto-install, install
it for the user with the platform's package manager, then re-run the script —
don't make the user do it by hand.

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
