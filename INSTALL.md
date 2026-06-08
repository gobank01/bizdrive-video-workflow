# Install — one-click installers

Goal: get this video pipeline running on student machines with the least
terminal work possible. Use the installer for the student's OS, then run the
matching checker.

---

## ⚡ Fastest path — the one-click installer (no WSL)

1. Download the repo as a ZIP from GitHub (green **Code → Download ZIP**) and
   unzip it — **or** open the folder a teacher handed you.
2. Open `tools\install\windows\` and **double-click `1-INSTALL.bat`**
   (then `2-CHECK.bat` afterwards to verify).
3. If a blue **"Windows protected your PC"** box appears, click
   **More info → Run anyway** (normal for any unsigned script).
4. Wait ~10–15 min while it downloads ~500 MB. If a Windows **"Do you want to
   allow this app…?"** (UAC) popup appears while installing a tool, click
   **Yes**.
5. When it finishes, open a **new** PowerShell/Terminal window and type:
   ```powershell
   cd ~\bizdrive-video-workflow
   claude
   ```
   Sign in, then paste your **ElevenLabs API key** when Claude asks
   (<https://elevenlabs.io/app/settings/api-keys>).

That's it. The `.bat` file only launches `tools/install/windows/setup.ps1`; the
PowerShell script does the real install. No WSL, no reboot, and no admin
PowerShell required. Some installers may still show a UAC **Yes** popup.

### What gets installed

| # | Item | Method | Purpose |
|---|------|--------|---------|
| 1 | Git + Git Bash | `winget` | clone repo and run bash scripts |
| 2 | ffmpeg / ffprobe | `winget` | cut, encode, inspect video |
| 3 | Python 3.12 + `python3` shim | `winget` + `~\.bizdrive\bin` | Thai NLP, VAD, transcription helpers |
| 4 | Node.js LTS | `winget` | run HyperFrames / npm tools |
| 5 | Claude Code | official `install.ps1` | student command interface |
| 6 | This repo | `git clone` / `git pull` | `~\bizdrive-video-workflow` |
| 7 | `pythainlp`, `nlpo3`, `certifi` | `pip` | Thai captions and HTTPS |
| 8 | Silero VAD env (`silero-vad`, `soundfile`, `numpy`, optional `torchcodec`) | `pip` venv | detect speech / silence |
| 9 | HyperFrames + skills (`npx hyperframes skills`) | `npx` | video renderer + Claude Code skills (restart Claude to load) |
| 10 | `.env` | asked up front | API keys (ElevenLabs + OpenRouter) |

> **Prefer to type one line instead of downloading?** Open PowerShell (normal,
> not admin) and paste:
> ```powershell
> irm https://raw.githubusercontent.com/gobank01/bizdrive-video-workflow/main/tools/install/windows/setup.ps1 | iex
> ```

### Requirements

- Windows 10 (2004+) or Windows 11 with **winget** (the built-in "App
  Installer"). Almost every modern PC has it. If the installer says winget is
  missing, install **App Installer** from the Microsoft Store
  (<https://apps.microsoft.com/detail/9nblggh4nns1>) and re-run.

### Just let Claude do it

If Claude Code is already installed, you don't even need the script — open
`claude` in the repo folder and say **"ติดตั้งให้หน่อย"** / **"install this on
Windows"**. Claude follows the Windows steps in
[CLAUDE.md](CLAUDE.md) and installs everything for you (it will ask you to click
any UAC popups, since it can't click those itself).

---

## Mac fastest path — double-click installer

1. Download the repo as a ZIP from GitHub and unzip it, or open the folder a
   teacher handed you.
2. Open `tools/install/mac/` and double-click `1-INSTALL.command`.
3. Paste the API keys when asked, then wait while it installs the tools.
4. Double-click `2-CHECK.command` to verify.

The Mac installer also installs Claude Code. If Homebrew is already installed,
it uses it. If Homebrew is not installed, it downloads user-level ffmpeg/ffprobe,
Node, and Python into `~/.bizdrive/bin` without asking for the macOS login password.

---

## Part 2 — Making videos

Every time you want to make a video:

1. Open **PowerShell** (or Windows Terminal), go to the repo:
   ```powershell
   cd ~\bizdrive-video-workflow
   ```
2. Type `claude`.
3. Tell it what you want, e.g.:
   > Make a vertical video from these two clips: a screen recording and my face
   > video. Use Template 01.

Git Bash comes with Git; Claude uses it for bash-based pipeline scripts when
needed. Claude follows the locked pipeline in
[`templates/_shared/docs/V88_PLAYBOOK.md`](templates/_shared/docs/V88_PLAYBOOK.md)
and hands you the finished `final.mp4`. Point it at your clips with normal
Windows paths (e.g. `C:\Users\You\Desktop\top.mp4`).

## If something breaks

Just tell Claude the error — it can re-run the installer, install missing
pieces, and diagnose live. If a single tool failed, you can also re-run:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\install\windows\setup.ps1
```
The installer is idempotent — safe to run again; it skips what's already there.

> **Note on Thai tokenizer (`nlpo3`):** it's a Rust wheel that occasionally
> won't build on Windows. If so, the installer automatically falls back to
> pythainlp's built-in tokenizer — captions still work, no action needed.

---

## (optional) Stop Claude from asking permission every time

If you edit with **Claude Code inside VS Code** and don't want to click "Allow"
on every command, run once from the repo folder:

```powershell
powershell -ExecutionPolicy Bypass -File tools\enable-claude-bypass.ps1
```

Then reload VS Code (`Ctrl+Shift+P` → **Reload Window**). It backs up your
settings first and only changes two keys.

> ⚠️ Bypass mode lets Claude run commands and edit files **without asking**. Use
> it only on your own trusted machine. (This repo also ships
> `.claude/settings.json` set to bypass, so once the repo is cloned Claude won't
> prompt inside it either.)

---

## Manual Mac / Linux setup

```bash
git clone https://github.com/gobank01/bizdrive-video-workflow.git
cd bizdrive-video-workflow
bash tools/setup.sh
```

Then add your keys to `templates/_shared/env/.env`. See
[ONBOARDING.md](ONBOARDING.md).

---

## Fallback — the old WSL path

The native installer above is preferred. Only use WSL if `winget` is unavailable
on a locked-down PC and you can't install App Installer. In an **admin**
PowerShell: `wsl --install`, reboot, open Ubuntu, then inside it run
`sudo apt-get update && sudo apt-get install -y curl git`,
`curl -fsSL https://claude.ai/install.sh | bash`, clone the repo, and
`bash tools/setup.sh`. This is the heavier route (Linux VM + reboot) and exists
only as a safety net.
