# setup.ps1 — BIZDRIVE Video, native Windows install (NO WSL).
#
# Installs everything the pipeline needs directly on Windows:
#   Git, ffmpeg, Python, Node.js, Claude Code, the repo, and all deps
#   (pythainlp, nlpo3, certifi + the Silero VAD venv with torch).
#
# No WSL. No reboot. No admin shell. Just run it and wait.
#
# Run via the double-click wrapper (1-INSTALL.bat) or directly:
#   powershell -ExecutionPolicy Bypass -File tools\install\windows\setup.ps1

$ErrorActionPreference = "Stop"
$RepoUrl   = "https://github.com/gobank01/bizdrive-video-workflow"
$VadEnv    = Join-Path $HOME ".bizdrive\vad-env"
$BinDir    = Join-Path $HOME ".bizdrive\bin"

function Section($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Ok($t)      { Write-Host "  [ok] $t"   -ForegroundColor Green }
function Info($t)    { Write-Host "  - $t" }
function Warn($t)    { Write-Host "  [!] $t"    -ForegroundColor Yellow }

function Have($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

# Refresh PATH in the CURRENT session so tools installed this run are usable
# immediately (winget updates the registry, not our live process env).
function Refresh-Path {
  $machine = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
  $user    = [System.Environment]::GetEnvironmentVariable("Path", "User")
  $env:Path = "$machine;$user"
}

function Add-UserPath($dir) {
  $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
  $parts = @()
  if ($userPath) { $parts = $userPath -split ";" | Where-Object { $_ -ne "" } }
  if ($parts -notcontains $dir) {
    $newPath = if ($userPath) { "$userPath;$dir" } else { $dir }
    [System.Environment]::SetEnvironmentVariable("Path", $newPath, "User")
  }
  if (($env:Path -split ";") -notcontains $dir) { $env:Path = "$env:Path;$dir" }
}

# Install a package via winget if its command isn't already present.
function Ensure($cmd, $wingetId, $label) {
  if (Have $cmd) { Ok "$label already installed"; return }
  Info "installing $label ..."
  winget install --id $wingetId -e --accept-source-agreements --accept-package-agreements --silent | Out-Null
  Refresh-Path
  if (Have $cmd) { Ok "$label installed" }
  else { Warn "$label installed but '$cmd' not on PATH yet — a new terminal may be needed" }
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BIZDRIVE Video — Windows installer (no WSL)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# --- 0. winget present? It ships with modern Win10/11. ---
Section "Checking Windows package manager (winget)"
if (-not (Have "winget")) {
  Warn "winget not found. Install 'App Installer' from the Microsoft Store, then re-run."
  Write-Host "    https://apps.microsoft.com/detail/9nblggh4nns1"
  Read-Host "Press Enter to exit"
  exit 1
}
Ok "winget available"

# --- 0.5 Ask for API keys UP FRONT so the long install runs unattended. ---
# We collect them now and write .env at the end. ElevenLabs is required (STT);
# OpenRouter is for AI B-roll. Both are requested for the class.
Section "Your API keys (paste them now — install runs while you wait)"

# Skip asking for a key that's already filled in an existing .env (re-runs).
$existingEnv = Join-Path (Join-Path $HOME "bizdrive-video-workflow") "templates\_shared\env\.env"
$haveEl = $false; $haveOr = $false
if (Test-Path $existingEnv) {
  $t = Get-Content $existingEnv -Raw
  $haveEl = ($t -match "(?m)^\s*ELEVENLABS_API_KEY=\S")
  $haveOr = ($t -match "(?m)^\s*OPENROUTER_API_KEY=\S")
}

$ElevenKey = $null; $OpenRouterKey = $null
if ($haveEl -and $haveOr) {
  Ok "API keys already in .env — not asking again"
} else {
  Write-Host "  ElevenLabs (required)  : https://elevenlabs.io/app/settings/api-keys"
  Write-Host "  OpenRouter (for B-roll): https://openrouter.ai/keys"
  Write-Host ""
  if (-not $haveEl) {
    $ElevenKey = (Read-Host "  Paste your ElevenLabs API key").Trim()
    while ([string]::IsNullOrWhiteSpace($ElevenKey)) {
      Warn "ElevenLabs key is required to make videos."
      $ElevenKey = (Read-Host "  Paste your ElevenLabs API key").Trim()
    }
  }
  if (-not $haveOr) {
    $OpenRouterKey = (Read-Host "  Paste your OpenRouter API key (press Enter to skip)").Trim()
  }
  Ok "keys captured — they'll be saved to .env"
}

# --- 1. System tools ---
Section "Installing system tools"
Ensure "git"     "Git.Git"                 "Git"
Ensure "ffmpeg"  "Gyan.FFmpeg"             "ffmpeg"
Ensure "python"  "Python.Python.3.12"      "Python 3.12"
Ensure "node"    "OpenJS.NodeJS.LTS"       "Node.js LTS"
Refresh-Path

# Resolve a python launcher that is >= 3.10. A machine may already have an old
# python on PATH; winget just installed 3.12, so prefer the version-pinned
# launcher. Try `py -3.13 … -3.10`, then `py -3`, then bare python — and verify
# each reports >= 3.10 before accepting it.
function PyVersionOK($exe, $verArg) {
  try {
    $out = & $exe $verArg "-c" "import sys; print(1 if sys.version_info >= (3,10) else 0)" 2>$null
    return ($out -eq "1")
  } catch { return $false }
}
$Py = $null; $PyArgs = @()
if (Have "py") {
  foreach ($v in @("-3.13","-3.12","-3.11","-3.10","-3")) {
    if (PyVersionOK "py" $v) { $Py = "py"; $PyArgs = @($v); break }
  }
}
if (-not $Py -and (Have "python")) {
  if (& python -c "import sys; print(1 if sys.version_info >= (3,10) else 0)" 2>$null) { $Py = "python"; $PyArgs = @() }
}
if (-not $Py) { Warn "Python 3.10+ not on PATH — open a NEW terminal and re-run, or install Python 3.12."; Read-Host "Press Enter to exit"; exit 1 }
# Helper to invoke the resolved python with its launcher args.
function Pyrun { & $Py @PyArgs @args }
Ok ("Python " + (Pyrun "--version") + " via '$Py $($PyArgs -join ' ')'")

Section "Preparing Python command"
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
$PythonShim = Join-Path $BinDir "python3"
$PythonCmdShim = Join-Path $BinDir "python3.cmd"
# Bake the SAME interpreter we validated (>=3.10) into the shims, so the
# pipeline's `python3` calls hit the python that owns pythainlp/certifi — not an
# older python that might also be on PATH. $Py is "py" (+ a -3.x arg) or "python".
$shimLauncher = $Py
$shimArg      = if ($PyArgs.Count -gt 0) { $PyArgs[0] } else { "" }
Set-Content -Path $PythonShim -Encoding ASCII -Value @"
#!/usr/bin/env sh
exec $shimLauncher $shimArg "`$@"
"@
Set-Content -Path $PythonCmdShim -Encoding ASCII -Value @"
@echo off
$shimLauncher $shimArg %*
"@
if (Have "bash") {
  $ShimForBash = $PythonShim -replace "\\", "/"
  bash -lc "chmod +x '$ShimForBash'" 2>$null
}
Add-UserPath $BinDir
if (Have "python3") { Ok "python3 command available" } else { Warn "python3 shim created; open a new terminal if this shell cannot see it yet" }

# --- 2. Claude Code (native Windows install) ---
Section "Installing Claude Code"
if (Have "claude") {
  Ok "Claude Code already installed"
} else {
  Info "installing Claude Code ..."
  try { Invoke-RestMethod "https://claude.ai/install.ps1" | Invoke-Expression; Refresh-Path }
  catch { Warn "Claude Code install hiccup — you can re-run 'irm https://claude.ai/install.ps1 | iex' later" }
  if (Have "claude") { Ok "Claude Code installed" }
}

# --- 3. Clone (or update) the repo ---
Section "Getting the project"
$Target = Join-Path $HOME "bizdrive-video-workflow"
if (Test-Path (Join-Path $Target ".git")) {
  Info "repo exists — pulling latest ..."
  git -C $Target pull --ff-only 2>$null
  Ok "repo updated"
} else {
  Info "cloning into $Target ..."
  git clone "$RepoUrl.git" $Target
  Ok "repo cloned"
}
Set-Location $Target

# --- 4. Python deps (Thai NLP) ---
Section "Installing Thai NLP libraries"
Info "pythainlp, nlpo3, certifi ..."
Pyrun "-m" "pip" "install" "--quiet" "--upgrade" "pip" | Out-Null
try {
  Pyrun "-m" "pip" "install" "--quiet" "--upgrade" "pythainlp" "nlpo3" "certifi"
  Ok "Thai NLP libs installed"
} catch {
  Warn "nlpo3 (Rust) failed to install on this machine."
  Warn "Installing pythainlp + certifi only; pythainlp's built-in tokenizer is the fallback."
  Pyrun "-m" "pip" "install" "--quiet" "--upgrade" "pythainlp" "certifi"
}

# --- 5. Silero VAD venv (torch — the big one, ~437 MB) ---
Section "Installing Silero VAD (voice detection, ~437 MB — one time)"
$VadPy = Join-Path $VadEnv "Scripts\python.exe"
$vadOk = (Test-Path $VadPy)
if ($vadOk) {
  & $VadPy -c "from silero_vad import load_silero_vad" 2>$null
  if ($LASTEXITCODE -ne 0) { $vadOk = $false }
}
if ($vadOk) {
  Ok "Silero VAD already installed"
} else {
  Info "creating venv at $VadEnv ..."
  Pyrun "-m" "venv" $VadEnv
  & $VadPy -m pip install --quiet --upgrade pip | Out-Null
  Info "installing torch + silero-vad (this is the slow download) ..."
  & $VadPy -m pip install --quiet silero-vad soundfile numpy
  & $VadPy -m pip install --quiet torchcodec 2>$null
  & $VadPy -c "from silero_vad import load_silero_vad" 2>$null
  if ($LASTEXITCODE -eq 0) { Ok "Silero VAD installed" } else { Warn "Silero VAD verify failed — re-run to retry" }
}

# --- 5.5 HyperFrames + its skills ---
# Warm the pinned hyperframes (so the first render doesn't pause to download it)
# and install the HyperFrames skill family for Claude Code. Idempotent.
Section "Installing HyperFrames + skills"
if (Have "npx") {
  cmd /c "npx --yes hyperframes@0.6.25 --version" 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { Ok "hyperframes@0.6.25 ready (cached for offline render)" }
  else { Warn "could not pre-warm hyperframes — npx fetches it on first render" }
  cmd /c "npx --yes hyperframes@0.6.25 skills" 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { Ok "HyperFrames skills installed (restart Claude Code to load them)" }
  else { Warn "skill install skipped — run later: npx hyperframes skills" }
} else {
  Warn "npx not found (Node missing?) — skipping HyperFrames skills"
}

# --- 6. .env — write the keys collected up front. ---
Section "Saving API keys to .env"
$EnvDir  = "templates\_shared\env"
$EnvFile = Join-Path $EnvDir ".env"
New-Item -ItemType Directory -Force -Path $EnvDir | Out-Null

# Start from the example (keeps the optional-key comments), then set the two
# keys we collected. If .env already exists, update those two lines in place so
# we never clobber other keys the user may have added.
$lines =
  if (Test-Path $EnvFile) { Get-Content $EnvFile }
  elseif (Test-Path (Join-Path $EnvDir ".env.example")) { Get-Content (Join-Path $EnvDir ".env.example") }
  else { @("ELEVENLABS_API_KEY=", "OPENROUTER_API_KEY=") }

function Set-EnvLine($content, $key, $val) {
  $set = $false
  $out = foreach ($l in $content) {
    if ($l -match "^\s*#?\s*$key=") { $set = $true; "$key=$val" } else { $l }
  }
  if (-not $set) { $out += "$key=$val" }
  return $out
}

# Only write a key we actually collected this run — never blank out a key that
# was already in .env (the $null case means "skipped, already present").
if (-not [string]::IsNullOrWhiteSpace($ElevenKey)) {
  $lines = Set-EnvLine $lines "ELEVENLABS_API_KEY" $ElevenKey
}
if (-not [string]::IsNullOrWhiteSpace($OpenRouterKey)) {
  $lines = Set-EnvLine $lines "OPENROUTER_API_KEY" $OpenRouterKey
}
Set-Content -Path $EnvFile -Value $lines -Encoding UTF8
Ok "API keys saved to $EnvFile"

# --- Done ---
Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  Setup complete — no WSL needed." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host @"

Next steps:
  1. Add your ElevenLabs key to:
       $Target\templates\_shared\env\.env
       (get one at https://elevenlabs.io/app/settings/api-keys)
  2. Open a NEW terminal (so PATH refreshes), go to the project:
       cd ~\bizdrive-video-workflow
  3. Start Claude Code:
       claude
     Then tell it: "ตัดต่อคลิปนี้ ใช้ Template 01"

"@
Read-Host "Press Enter to close"
