# Install — Windows (for non-technical users)

Goal: get this video pipeline running on a Windows PC, with **Claude Code doing
almost all the work**. You only do a tiny one-time bootstrap; after that, Claude
installs everything else and makes your videos.

> **Why a bootstrap at all?** Claude Code can install Python, Node, ffmpeg, this
> repo, and run the whole pipeline for you — but *something* has to install
> Claude Code first, and on Windows that needs WSL (a Linux environment inside
> Windows). Claude can't install the thing it runs inside. So the 3 steps below
> are the unavoidable minimum; everything after is automatic.

---

## Part 1 — One-time bootstrap (do this once, ~15 min, mostly waiting)

### Step 1 — Install WSL (the only "Run as administrator" moment)

1. Click **Start**, type `powershell`.
2. **Right-click → "Run as administrator".**
3. Paste this one line and press Enter:
   ```powershell
   wsl --install
   ```
4. **Reboot** when it asks.

That is the last time you ever need PowerShell or administrator. ✅

> Older Windows? `wsl --install` works on Windows 10 (version 2004+) and
> Windows 11. If it says the command isn't found, run Windows Update first.

### Step 2 — Open Ubuntu (normal window, no admin)

After the reboot an **Ubuntu** window opens by itself and asks you to pick a
username and password. Type anything you'll remember (the password won't show as
you type — that's normal). From now on you use **this Ubuntu window**, not
PowerShell.

### Step 3 — Install Claude Code

In the Ubuntu window, first make sure the basic tools exist (a fresh Ubuntu may
not have `curl` or `git` yet), then install Claude Code:

```bash
sudo apt-get update && sudo apt-get install -y curl git
curl -fsSL https://claude.ai/install.sh | bash
```

Then start it:

```bash
claude
```

If you get `claude: command not found`, the installer added it to your PATH but
this window hasn't picked it up yet — just **close the Ubuntu window and open it
again**, then type `claude`. (Per Claude's official FAQ, a new shell session
loads the updated PATH.)

Sign in when prompted. **You're done with the manual part.** 🎉

---

## Part 2 — Let Claude do the rest (automatic)

With Claude Code running, paste this single prompt:

```
Clone https://github.com/gobank01/bizdrive-video-workflow into my home folder,
cd into it, and run `bash tools/setup.sh` to install everything. If anything is
missing (Python, Node, ffmpeg) install it for me. Then ask me for my ElevenLabs
API key and put it in templates/_shared/env/.env. When it's ready, tell me how to
make my first video.
```

Claude will:
- clone the repo,
- run `tools/setup.sh` (auto-installs Python, Node, ffmpeg, the Thai NLP libs,
  and the Silero voice-detection engine — ~437 MB, one-time),
- create the `.env` file and ask you for your **ElevenLabs API key**
  (get one at <https://elevenlabs.io/app/settings/api-keys>),
- (optional) ask for an **OpenRouter key** if you want AI B-roll
  (<https://openrouter.ai/keys>).

---

## Part 3 — Making videos (forever after)

Every time you want to make a video:

1. Open the **Ubuntu** app (no admin, no PowerShell).
2. Type `claude`.
3. Tell it what you want, e.g.:
   > Make a vertical video from these two clips: a screen recording and my face
   > video. Use Template 01.

Claude follows the locked pipeline in
[`templates/_shared/docs/V88_PLAYBOOK.md`](templates/_shared/docs/V88_PLAYBOOK.md)
and hands you the finished `final.mp4`.

---

## Getting files in and out of WSL

Your Windows files are visible from Ubuntu under `/mnt/c/...`. Example: your
Desktop is `/mnt/c/Users/<YourName>/Desktop`. Tell Claude the path to your clips
and where you want the finished video — it handles the rest.

## If something breaks

Just tell Claude the error — it can re-run `bash tools/setup.sh`, install missing
pieces, and diagnose problems live. That's the whole point of the agent-driven
setup: you don't debug, Claude does.

---

## Mac / Linux users

Skip all of the above. Just:

```bash
git clone https://github.com/gobank01/bizdrive-video-workflow.git
cd bizdrive-video-workflow
bash tools/setup.sh
```

Then add your keys to `templates/_shared/env/.env`. See
[ONBOARDING.md](ONBOARDING.md).
