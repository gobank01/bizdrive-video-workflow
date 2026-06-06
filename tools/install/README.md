# tools/install/ — one-click installers

Everything a student needs to set up the project, split by OS. Two files each:
**1 = install, 2 = check.** Double-click them in order.

```
tools/install/
├─ windows/
│  ├─ 1-INSTALL.bat   ← double-click first. Asks for your ElevenLabs +
│  │                     OpenRouter keys, then installs Git, ffmpeg, Python,
│  │                     Node, Claude Code, the repo, Thai NLP + Silero VAD.
│  │                     No WSL, no reboot. (wraps setup.ps1)
│  ├─ 2-CHECK.bat     ← double-click after. Green/red list of every tool +
│  │                     whether your API keys are saved. (wraps check.ps1)
│  ├─ setup.ps1       ← the real installer (PowerShell). Don't double-click
│  │                     directly — Windows opens .ps1 in Notepad.
│  └─ check.ps1       ← the real checker.
└─ mac/
   ├─ 1-INSTALL.command  ← double-click first. Runs tools/setup.sh, asks for
   │                        your API keys, and installs Claude Code. If Homebrew
   │                        exists, it uses Homebrew. If not, it downloads
   │                        user-level tools into ~/.bizdrive/bin so a fresh Mac can
   │                        finish without a password prompt.
   └─ 2-CHECK.command    ← double-click after. Same green/red check as Windows.
```

## Which engine each one drives

- **Windows** → `setup.ps1` / `check.ps1` are self-contained (they install via
  `winget` + `pip`, clone the repo into `~/bizdrive-video-workflow`, and write
  `.env`). The VAD venv python on Windows is `…/.bizdrive/vad-env/Scripts/python.exe`.
- **Mac/Linux** → the `.command` files are thin wrappers around the canonical
  **`tools/setup.sh`**. macOS uses existing Homebrew when present, otherwise
  no-brew user-level binaries in `~/.bizdrive/bin`; Linux uses apt/dnf + pip. Both
  also try to install Claude Code. The VAD venv python is
  `…/.bizdrive/vad-env/bin/python3`.

Both paths also run `npx hyperframes skills` — this warms the pinned
`hyperframes@0.6.25` (so the first video render doesn't pause to download it) and
installs the HyperFrames skill family into `~/.claude/skills/` for Claude Code.
The user should restart Claude Code once after setup so the skills load.

Both paths end the same way: all tools installed, HyperFrames + skills ready,
`.env` filled with the user's keys, ready for `claude`.

## API keys

Both installers ask for the keys **up front** and write them into
`templates/_shared/env/.env`:

- `ELEVENLABS_API_KEY` — **required** (Thai speech-to-text).
- `OPENROUTER_API_KEY` — for AI B-roll (asked, optional to paste).

When `tools/setup.sh` is run by an agent (Claude) with no terminal, it can't
prompt — it leaves `.env` blank and Claude asks for the keys instead.

## Letting Claude install instead

If Claude Code is already installed, a student can skip these files and just say
**"ติดตั้งให้หน่อย" / "install this"**. Claude follows the OS-specific steps in
the repo's [CLAUDE.md](../../CLAUDE.md). It still can't click Windows UAC popups
or fill any OS password prompt if one appears — it will tell the user to do
those.
