# CLAUDE.md — BIZDRIVE Video V3

**Read [AGENTS.md](AGENTS.md) first — it is the project rule book.** It defines
the Template Manager sync rule, the Job Spec rule, the locked v88 pipeline, and
when to add a template. Every rule there applies to Claude Code.

## First-run setup — "install" / "setup" means do ALL of this, end to end

When the user says anything like **"install"**, **"setup"**, **"set this up"**,
**"ติดตั้ง"**, **"get this working"** — or when a pipeline command fails because a
tool is missing — run the WHOLE sequence below without stopping between steps.
Do not hand intermediate commands back to the user; you run them. The same flow
works on macOS and Linux/WSL (Windows users are inside WSL — treat it as Linux).
Finish only when the project is fully ready to make a video.

**Step 1 — Run the OS-aware installer.** It auto-installs ffmpeg, python3 (+pip
+venv), Node 18+, the Thai NLP libs, and the Silero VAD venv (~437 MB):

```bash
bash tools/setup.sh
```

If it reports a tool it could not auto-install, install that tool yourself with
the platform's package manager (macOS `brew`, Linux/WSL `sudo apt-get`/`dnf`),
then re-run `bash tools/setup.sh`. Never make the user install by hand.

**Step 2 — API keys.** `setup.sh` creates `templates/_shared/env/.env` from the
example. Open it and ask the user to paste their keys (never invent them):

```
ELEVENLABS_API_KEY=...     # required  — https://elevenlabs.io/app/settings/api-keys
OPENROUTER_API_KEY=...     # optional (B-roll) — https://openrouter.ai/keys
```

If the user only has the ElevenLabs key, that is enough to start — leave
OpenRouter blank and skip B-roll later.

**Step 3 — Verify the environment is actually ready.** Run preflight and confirm
every check is "yes":

```bash
bash templates/_shared/scripts/clean-cut/preflight.sh
```

It prints JSON for `ffmpeg`, `ffprobe`, `python3`, `silero_vad`. If any is "no",
go back to Step 1 for that piece — don't proceed.

**Step 4 — Report ready + tell the user the next move.** When preflight is clean
and the ElevenLabs key is in `.env`, tell the user setup is complete and how to
start their first clip, e.g.:

> ติดตั้งครบแล้ว ✅ วางคลิปของคุณ (top.mp4 = จอ, bottom.mp4 = หน้า, bg.png) แล้วบอกผม
> ว่า "ตัดต่อคลิปนี้ ใช้ Template 01" — ผมจะรันไปป์ไลน์ v88 ให้

The 16-step production pipeline itself lives in
[`templates/_shared/docs/V88_PLAYBOOK.md`](templates/_shared/docs/V88_PLAYBOOK.md);
follow it when the user asks to edit a clip — that is a separate task from setup.

> **Permission popups:** this repo ships `.claude/settings.json` with
> `defaultMode: bypassPermissions`, so inside this project you can run the setup
> commands without prompting. If the user is on the VS Code extension and wants
> no prompts machine-wide (before the repo is even cloned), point them at
> `tools/enable-claude-bypass.ps1` (Windows) / `tools/enable-claude-bypass.sh`
> (mac/Linux). See [INSTALL.md](INSTALL.md).

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
