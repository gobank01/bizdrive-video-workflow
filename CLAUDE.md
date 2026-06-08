# CLAUDE.md — BIZDRIVE Video V3

**Read [AGENTS.md](AGENTS.md) first — it is the project rule book.** It defines
the Template Manager sync rule, the Job Spec rule, the locked v88 pipeline, and
when to add a template. Every rule there applies to Claude Code.

## First-run setup — "install" / "setup" means do ALL of this, end to end

When the user says anything like **"install"**, **"setup"**, **"set this up"**,
**"ติดตั้ง"**, **"get this working"**, **"clone this project"** — or when a
pipeline command fails because a tool is missing — run the WHOLE sequence below
without stopping between steps. Do not hand intermediate commands back to the
user; you run them. Finish only when the project is fully ready to make a video.

**Step 0 — Get the repo (if not already here).** Students open an empty folder
(e.g. `all-ai/`) in VS Code and ask Claude to clone the project. If the current
directory is not already this repo (no `CLAUDE.md`/`tools/setup.sh` present),
clone it and `cd` in:

```bash
git clone https://github.com/gobank01/bizdrive-video-workflow.git
cd bizdrive-video-workflow
```

If `git` is missing, install it first (macOS `brew install git`; Windows
`winget install Git.Git`). Then continue with Step 1 from inside the repo.

**Step 1 — Run the installer for the current OS.** Detect the platform first
(`uname -s`; on native Windows the Bash tool reports `MINGW*`/`MSYS*`, and
`$OS` is `Windows_NT`). Then:

- **macOS / Linux / WSL** — run the bash installer. It auto-installs ffmpeg,
  python3 (+pip+venv), Node 18+, the Thai NLP libs, and the Silero VAD venv
  (~437 MB):

  ```bash
  bash tools/setup.sh
  ```

  If it reports a tool it could not auto-install, install it yourself with the
  platform's package manager (macOS `brew`, Linux/WSL `sudo apt-get`/`dnf`),
  then re-run. Never make the user install by hand.

- **Native Windows (NO WSL)** — run the PowerShell installer instead. It uses
  `winget` to install Git + Git Bash, ffmpeg, Python, Node, plus the Thai NLP
  libs and the Silero VAD venv, all natively — no WSL, no reboot. It also asks
  for the user's API keys up front and writes them to `.env`:

  ```bash
  powershell -NoProfile -ExecutionPolicy Bypass -File tools/install/windows/setup.ps1
  ```

  (Students can also just double-click `tools/install/windows/1-INSTALL.bat`,
  then `2-CHECK.bat` to verify.)
  Some `winget` installs raise a Windows UAC prompt — you cannot click it for
  the user, so tell them to click **Yes** if it appears. If `winget` is missing,
  have them install "App Installer" from the Microsoft Store, then re-run. If
  `nlpo3` (a Rust wheel) fails on Windows, the installer falls back to
  pythainlp's built-in tokenizer automatically — that is fine, continue.

> The Silero VAD venv python differs by OS: `~/.bizdrive/vad-env/bin/python3` on
> macOS/Linux, `~/.bizdrive/vad-env/Scripts/python.exe` on native Windows. The
> mechanical runners already pick the right one — don't hardcode either. The
> Windows installer also creates a `python3` shim at `~/.bizdrive/bin` because the
> repo scripts use `python3`.

**Step 2 — API keys — YOU must ask, because the script can't.** When YOU (Claude)
run `setup.sh`, there is no terminal, so the script prints "No terminal detected"
and leaves `.env` blank — it does NOT prompt. So after setup, check `.env`; if
`ELEVENLABS_API_KEY=` (or `OPENROUTER_API_KEY=`) is empty, ask the user in chat
for the value (never invent one) and write it into
`templates/_shared/env/.env`:

```
ELEVENLABS_API_KEY=...     # required  — https://elevenlabs.io/app/settings/api-keys
OPENROUTER_API_KEY=...     # for B-roll — https://openrouter.ai/keys
```

Trim whitespace from a pasted key before saving. If the user only has the
ElevenLabs key, that is enough to start — leave OpenRouter blank and skip B-roll
later. (When a student double-clicks the installer instead, the script itself
prompts for the keys, so this step is already done.)

**Step 3 — Verify the environment is actually ready.** Run preflight and confirm
every check is "yes":

```bash
bash templates/_shared/scripts/clean-cut/preflight.sh
```

It prints JSON for `ffmpeg`, `ffprobe`, `python3`, `silero_vad`. If any is "no",
go back to Step 1 for that piece — don't proceed.

On native Windows this runs through Git Bash (installed in Step 1), so the same
`bash …/preflight.sh` works. If Git Bash is somehow unavailable, verify by hand
instead: `ffmpeg -version`, `python --version`, and
`~/.bizdrive/vad-env/Scripts/python.exe -c "from silero_vad import load_silero_vad"`.

**Step 4 — Report ready + tell the user the next move.** When preflight is clean
and the ElevenLabs key is in `.env`, tell the user setup is complete and how to
start their first clip, e.g.:

> ติดตั้งครบแล้ว ✅ ปิด-เปิด Claude Code ใหม่ 1 ครั้ง (เพื่อโหลด HyperFrames
> skills) แล้ววางคลิปของคุณ (top.mp4 = จอ, bottom.mp4 = หน้า, bg.png) แล้วบอกผม
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

- **Skills:** the installers run `npx hyperframes skills`, so the `hyperframes`
  family (composition authoring, captions, TTS, render CLI) is installed for
  Claude Code — restart the session once after setup to load them. The skill
  table is in `templates/_shared/docs/CLAUDE.md`. Note: clip production via the 8
  templates runs through `tools/v88-clip.sh` directly and does NOT require any
  skill; skills matter when authoring/editing HyperFrames compositions.
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
- **Every template has a `frame.md` (AGENTS.md RULE 4).** It is the per-template
  design/frame spec an agent reads before composing — aspect, colors, type,
  layout, motion, audio. When you create a template (`new-template.sh` copies
  `templates/_starter/frame.md`) or change its look, fill/update `frame.md` in
  the same edit, keeping the starter's section schema. A template without a
  filled `frame.md` is incomplete.
- Per-clip work lives in `jobs/YYYY-MM-DD-<slug>/`; scaffold with
  `bash tools/new-job.sh <NN> <slug> --raw <raw-slug>`.

## Quick map

- `templates/NN-*/` — the 8 locked templates; each `manifest.json` has a
  `features[]` block (the Template Manager's toggle surface)
- `templates/_shared/` — pipeline scripts, docs, schemas, BGM/SFX/B-roll, and
  `manager-ui.json` (UI labels)
- `tools/` — `new-job.sh`, `new-template.sh`, `build-manager.py`,
  `build-catalog.sh`, `template-manager.html`
- `jobs/` — per-clip work orders, intermediates and renders
