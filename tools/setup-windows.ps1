# setup-windows.ps1 — BIZDRIVE Video, native Windows install (NO WSL).
#
# Installs everything the pipeline needs directly on Windows:
#   Git, ffmpeg, Python, Node.js, Claude Code, the repo, and all deps
#   (pythainlp, nlpo3, certifi + the Silero VAD venv with torch).
#
# No WSL. No reboot. No admin shell. Just run it and wait.
#
# Run via the double-click wrapper (install-windows.bat) or directly:
#   powershell -ExecutionPolicy Bypass -File tools\setup-windows.ps1

$ErrorActionPreference = "Stop"
$RepoUrl   = "https://github.com/gobank01/bizdrive-video-workflow"
$VadEnv    = Join-Path $HOME ".ii23\vad-env"
$BinDir    = Join-Path $HOME ".ii23\bin"

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

# --- 1. System tools ---
Section "Installing system tools"
Ensure "git"     "Git.Git"                 "Git"
Ensure "ffmpeg"  "Gyan.FFmpeg"             "ffmpeg"
Ensure "python"  "Python.Python.3.12"      "Python 3.12"
Ensure "node"    "OpenJS.NodeJS.LTS"       "Node.js LTS"
Refresh-Path

# Resolve a python launcher (py or python).
$Py = if (Have "py") { "py" } elseif (Have "python") { "python" } else { $null }
if (-not $Py) { Warn "Python not on PATH — open a NEW terminal and re-run this script."; Read-Host "Press Enter to exit"; exit 1 }

Section "Preparing Python command"
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
$PythonShim = Join-Path $BinDir "python3"
$PythonCmdShim = Join-Path $BinDir "python3.cmd"
Set-Content -Path $PythonShim -Encoding ASCII -Value @'
#!/usr/bin/env sh
if command -v py >/dev/null 2>&1; then
  exec py -3 "$@"
fi
exec python "$@"
'@
Set-Content -Path $PythonCmdShim -Encoding ASCII -Value @'
@echo off
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 %*
) else (
  python %*
)
'@
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
& $Py -m pip install --quiet --upgrade pip | Out-Null
try {
  & $Py -m pip install --quiet --upgrade pythainlp nlpo3 certifi
  Ok "Thai NLP libs installed"
} catch {
  Warn "nlpo3 (Rust) failed to install on this machine."
  Warn "Installing pythainlp + certifi only; pythainlp's built-in tokenizer is the fallback."
  & $Py -m pip install --quiet --upgrade pythainlp certifi
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
  & $Py -m venv $VadEnv
  & $VadPy -m pip install --quiet --upgrade pip | Out-Null
  Info "installing torch + silero-vad (this is the slow download) ..."
  & $VadPy -m pip install --quiet silero-vad soundfile numpy
  & $VadPy -m pip install --quiet torchcodec 2>$null
  & $VadPy -c "from silero_vad import load_silero_vad" 2>$null
  if ($LASTEXITCODE -eq 0) { Ok "Silero VAD installed" } else { Warn "Silero VAD verify failed — re-run to retry" }
}

# --- 6. .env for API keys ---
Section "API key file"
$EnvFile    = "templates\_shared\env\.env"
$EnvExample = "templates\_shared\env\.env.example"
if (Test-Path $EnvFile) {
  Ok ".env already exists (left untouched)"
} elseif (Test-Path $EnvExample) {
  Copy-Item $EnvExample $EnvFile
  Ok "created .env from template"
  Warn "EDIT it — add your ELEVENLABS_API_KEY (and OPENROUTER_API_KEY for B-roll)"
}

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
