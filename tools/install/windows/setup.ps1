# setup.ps1 — BIZDRIVE Video, native Windows install (NO WSL).
#
# Installs the dependencies the pipeline needs, directly on Windows:
#   Git, ffmpeg, Python, Node.js, the Thai NLP libs (pythainlp, nlpo3, certifi),
#   and the Silero VAD venv with torch (+ the VC++ runtime torch needs).
# It does NOT install Claude Code — use the Claude Code VS Code extension.
#
# No WSL. No reboot. No admin shell. Just run it and wait.
#
# Run via the double-click wrapper (1-INSTALL.bat) or directly:
#   powershell -ExecutionPolicy Bypass -File tools\install\windows\setup.ps1

$ErrorActionPreference = "Stop"

# Show UTF-8 (Thai + em-dashes) correctly no matter the machine's locale/codepage.
# Without this, consoles on a non-UTF-8 codepage (e.g. Thai CP874) garble output.
try {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

# Detect a real interactive console. When Claude Code (or any automation) runs
# this script, stdin is redirected and Read-Host would hang forever — so we skip
# prompts and fall back to non-interactive behaviour, mirroring setup.sh's
# "no terminal detected" path.
$Interactive = $true
try { $Interactive = -not [Console]::IsInputRedirected } catch {}

$RepoUrl   = "https://github.com/gobank01/bizdrive-video-workflow"
$VadEnv    = Join-Path $HOME ".bizdrive\vad-env"
$BinDir    = Join-Path $HOME ".bizdrive\bin"

# This script lives at <repo>\tools\install\windows\setup.ps1. If the student
# unzipped the repo and double-clicked the .bat next to us, the repo is already
# here (3 levels up) — use it in place, do NOT clone a second copy. Only clone
# (later) if we're somehow run from outside a repo checkout.
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$RepoFromZip = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path

function Section($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Ok($t)      { Write-Host "  [ok] $t"   -ForegroundColor Green }
function Info($t)    { Write-Host "  - $t" }
function Warn($t)    { Write-Host "  [!] $t"    -ForegroundColor Yellow }

function Have($cmd) {
  # Look at ALL matches, not just the first: Windows puts a Microsoft Store
  # "App execution alias" stub for python/python3 under ...\WindowsApps that is
  # earlier on PATH than a real install. We must ignore those stubs and still
  # report true if a real interpreter exists further down PATH.
  $cmds = @(Get-Command $cmd -All -ErrorAction SilentlyContinue)
  foreach ($c in $cmds) {
    if ($c.Source -and ($c.Source -match '\\Microsoft\\WindowsApps\\python(3)?\.exe$')) { continue }
    return $true
  }
  return $false
}

# Refresh PATH in the CURRENT session so tools installed this run are usable
# immediately (winget updates the registry, not our live process env).
function Refresh-Path {
  $machine = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
  $user    = [System.Environment]::GetEnvironmentVariable("Path", "User")
  $env:Path = "$machine;$user"
  # winget often can't update THIS process's PATH in the same run (a known issue
  # on Windows PowerShell 5.1). Probe the well-known install locations of the
  # tools we just installed and append any that exist, so they're usable now —
  # not only after the user opens a fresh terminal.
  $known = @(
    "$env:ProgramFiles\nodejs",
    "${env:ProgramFiles(x86)}\nodejs",
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python313"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\Scripts"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\Scripts"),
    "$env:ProgramFiles\Git\cmd",
    "$env:LOCALAPPDATA\Microsoft\WindowsApps"
  )
  # ffmpeg (Gyan.FFmpeg) lands under a versioned winget Packages dir — find its bin.
  $pkgRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
  if (Test-Path $pkgRoot) {
    Get-ChildItem $pkgRoot -Directory -Filter "Gyan.FFmpeg*" -ErrorAction SilentlyContinue | ForEach-Object {
      $bin = Get-ChildItem $_.FullName -Recurse -Filter ffmpeg.exe -ErrorAction SilentlyContinue | Select-Object -First 1
      if ($bin) { $known += $bin.Directory.FullName }
    }
  }
  foreach ($d in $known) {
    if ($d -and (Test-Path $d) -and (($env:Path -split ";") -notcontains $d)) { $env:Path = "$env:Path;$d" }
  }
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
  # Pin --source winget. On some machines the 'msstore' source fails (e.g. a TLS
  # certificate error) and, because an id can match BOTH sources, winget aborts
  # with "specify a source" and installs nothing. Pinning the source avoids that.
  # Run with EAP=Continue so winget writing to stderr can't kill the whole script.
  $old = $ErrorActionPreference; $ErrorActionPreference = "Continue"
  try {
    winget install --id $wingetId -e --source winget --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null
  } catch {} finally { $ErrorActionPreference = $old }
  $code = $LASTEXITCODE
  Refresh-Path
  if (Have $cmd) { Ok "$label installed" }
  elseif ($code -and $code -ne 0) { Warn "${label}: winget exit code $code — '$cmd' not found yet. May need a new terminal, admin rights (UAC), or a manual install." }
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
  if ($Interactive) { Read-Host "Press Enter to exit" }
  exit 1
}
Ok "winget available"

# --- 0.5 Ask for API keys UP FRONT so the long install runs unattended. ---
# We collect them now and write .env at the end. ElevenLabs is required (STT);
# OpenRouter is for AI B-roll. Both are requested for the class.
Section "Your API keys (paste them now — install runs while you wait)"

# Skip asking for a key that's already filled in an existing .env (re-runs).
# Check the .env inside the repo we're actually about to use (the unzipped copy
# next to us), not a guessed path under $HOME — otherwise re-runs always re-ask.
$existingEnv = Join-Path $RepoFromZip "templates\_shared\env\.env"
if (-not (Test-Path $existingEnv)) {
  $existingEnv = Join-Path (Join-Path $HOME "bizdrive-video-workflow") "templates\_shared\env\.env"
}
$haveEl = $false; $haveOr = $false
if (Test-Path $existingEnv) {
  $t = Get-Content $existingEnv -Raw
  $haveEl = ($t -match "(?m)^\s*ELEVENLABS_API_KEY=\S")
  $haveOr = ($t -match "(?m)^\s*OPENROUTER_API_KEY=\S")
}

$ElevenKey = $null; $OpenRouterKey = $null
if ($haveEl -and $haveOr) {
  Ok "API keys already in .env — not asking again"
} elseif (-not $Interactive) {
  # No console to prompt at (Claude Code / automation). Don't hang on Read-Host —
  # skip and tell the user to add keys to .env afterwards.
  Warn "No interactive console — skipping the API-key prompt."
  Warn "After setup, add your keys to: templates\_shared\env\.env"
  Write-Host "    ELEVENLABS_API_KEY=...   (required  - https://elevenlabs.io/app/settings/api-keys)"
  Write-Host "    OPENROUTER_API_KEY=...   (for B-roll - https://openrouter.ai/keys)"
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

# Node.js needs special handling: the winget package is a MACHINE-scope MSI that
# triggers a UAC prompt and needs admin. That's fine when a student double-clicks
# the installer (they click "Yes"), but it blocks on locked-down / no-admin
# machines and in automation. So: try winget first, then fall back to a portable
# Node.js (downloaded to ~/.bizdrive/node) that needs no admin at all.
function Ensure-Node {
  if (Have "node") { Ok "Node.js already installed"; return }
  # Only try the winget MSI when we have an interactive console: it pops a UAC
  # prompt that must be clicked. In automation (no console) that would hang
  # forever, so we skip straight to the portable install below.
  if ($Interactive) {
    Info "installing Node.js LTS (winget; may show a UAC prompt — click Yes) ..."
    $old = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    try {
      winget install --id OpenJS.NodeJS.LTS -e --source winget --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null
    } catch {} finally { $ErrorActionPreference = $old }
    Refresh-Path
    if (Have "node") { Ok "Node.js installed (winget)"; return }
  }

  Info "winget needs admin — installing a portable Node.js (no admin required) ..."
  try {
    $arch = if ([Environment]::Is64BitOperatingSystem) {
      if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") { "arm64" } else { "x64" }
    } else { "x86" }
    # Resolve the current LTS version from the official dist index (no hardcoding).
    $ver = $null
    try {
      $idx = Invoke-RestMethod "https://nodejs.org/dist/index.json" -UseBasicParsing
      $ver = ($idx | Where-Object { $_.lts } | Select-Object -First 1).version
    } catch {}
    if (-not $ver) { $ver = "v22.13.1" }   # safety net if the index is unreachable
    $name = "node-$ver-win-$arch"
    $url  = "https://nodejs.org/dist/$ver/$name.zip"
    $zip  = Join-Path $env:TEMP "$name.zip"
    $base = Join-Path $HOME ".bizdrive"
    $dst  = Join-Path $base "node"
    New-Item -ItemType Directory -Force -Path $base | Out-Null
    Info "downloading $url ..."
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
    if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
    Expand-Archive -Path $zip -DestinationPath $base -Force
    $extracted = Join-Path $base $name
    if (Test-Path $extracted) { Rename-Item $extracted $dst }
    Add-UserPath $dst
    Refresh-Path
    if (Have "node") { Ok "Node.js (portable) installed at $dst" }
    else { Warn "Node.js still not found — install it manually from https://nodejs.org and re-run." }
  } catch {
    Warn "Portable Node.js install failed: $($_.Exception.Message)"
    Warn "Install Node.js manually from https://nodejs.org, then re-run."
  }
}

# Ensure the Microsoft Visual C++ runtime (needed by PyTorch — without it
# "import torch" fails with a DLL load error). The redist is a machine-scope
# component, so installing it needs admin (UAC). Skip silently in automation.
function Ensure-VCRedist {
  $have = (Test-Path "$env:SystemRoot\System32\vcruntime140.dll") -and
          (Test-Path "$env:SystemRoot\System32\vcruntime140_1.dll")
  if ($have) { Ok "Visual C++ runtime present"; return }
  if (-not $Interactive) {
    Warn "Visual C++ runtime missing — PyTorch needs it, and it requires admin to install."
    Warn "Install it once from https://aka.ms/vs/17/release/vc_redist.x64.exe, then re-run."
    return
  }
  Info "installing Microsoft Visual C++ runtime (UAC prompt — click Yes) ..."
  $old = $ErrorActionPreference; $ErrorActionPreference = "Continue"
  try {
    winget install --id Microsoft.VCRedist.2015+.x64 -e --source winget --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null
  } catch {} finally { $ErrorActionPreference = $old }
  if (Test-Path "$env:SystemRoot\System32\vcruntime140.dll") { Ok "Visual C++ runtime installed" }
  else { Warn "Could not confirm the VC++ runtime — if torch fails later, install https://aka.ms/vs/17/release/vc_redist.x64.exe manually." }
}

# --- 1. System tools ---
Section "Installing system tools"
Ensure "git"     "Git.Git"                 "Git"
Ensure "ffmpeg"  "Gyan.FFmpeg"             "ffmpeg"
Ensure "python"  "Python.Python.3.12"      "Python 3.12"
Ensure-Node
Refresh-Path

# Resolve a python launcher that is >= 3.10. A machine may already have an old
# python on PATH (or only the Microsoft Store stub); winget just installed 3.12,
# so prefer the version-pinned `py` launcher, then a real `python`, then search
# the known install dirs directly. Every candidate is verified to report >= 3.10.
$PyProbe = "import sys; print('%d.%d' % sys.version_info[:2]) if sys.version_info >= (3,10) else ''"
function PyVersionOK($exe, $argList) {
  # Run "<exe> [launcherArg] -c <probe>" safely: native stderr must not throw the
  # whole script (the Store stub writes to stderr), and a non-version reply = no.
  $old = $ErrorActionPreference; $ErrorActionPreference = "SilentlyContinue"
  try {
    $a = @(); foreach ($x in $argList) { if ($x) { $a += $x } }
    $a += @("-c", $PyProbe)
    $out = (& $exe @a 2>$null | Select-Object -First 1)
    return (-not [string]::IsNullOrWhiteSpace($out))
  } catch { return $false }
  finally { $ErrorActionPreference = $old }
}
$Py = $null; $PyArgs = @()
# 1. Most reliable: a real python.exe in the standard install dirs. A full path
#    bypasses both the Microsoft Store stub and any PATH-refresh timing, and it's
#    what we bake into the shim so the pipeline always hits the right python.
$roots = @(
  (Join-Path $env:LOCALAPPDATA "Programs\Python"),
  "$env:ProgramFiles\Python313","$env:ProgramFiles\Python312","$env:ProgramFiles\Python311","$env:ProgramFiles\Python310",
  "C:\Python313","C:\Python312","C:\Python311","C:\Python310"
)
foreach ($r in $roots) {
  if (Test-Path $r) {
    $cands = Get-ChildItem $r -Recurse -Filter python.exe -ErrorAction SilentlyContinue |
             Where-Object { $_.FullName -notmatch 'WindowsApps' -and $_.FullName -notmatch '\\Lib\\venv\\' } |
             Sort-Object FullName -Descending
    foreach ($c in $cands) {
      if (PyVersionOK $c.FullName @()) { $Py = $c.FullName; $PyArgs = @(); break }
    }
  }
  if ($Py) { break }
}
# 2. Fall back to the py launcher, then a real python on PATH.
if (-not $Py -and (Have "py")) {
  foreach ($v in @("-3.13","-3.12","-3.11","-3.10","-3")) {
    if (PyVersionOK "py" @($v)) { $Py = "py"; $PyArgs = @($v); break }
  }
}
if (-not $Py -and (Have "python")) {
  if (PyVersionOK "python" @()) { $Py = "python"; $PyArgs = @() }
}
if (-not $Py) {
  Warn "Python 3.10+ not found even after install."
  Warn "Open a NEW terminal (so PATH refreshes) and re-run, or install Python 3.12 from python.org."
  if ($Interactive) { Read-Host "Press Enter to exit" }
  exit 1
}
# Helper to invoke the resolved python with its launcher args.
function Pyrun { & $Py @PyArgs @args }
Ok ("Python " + ((Pyrun "--version") -replace 'Python *','') + " via '$Py $($PyArgs -join ' ')'")

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
exec "$shimLauncher" $shimArg "`$@"
"@
Set-Content -Path $PythonCmdShim -Encoding ASCII -Value @"
@echo off
"$shimLauncher" $shimArg %*
"@
if (Have "bash") {
  $ShimForBash = $PythonShim -replace "\\", "/"
  $oldEAP = $ErrorActionPreference; $ErrorActionPreference = "Continue"
  try { bash -lc "chmod +x '$ShimForBash'" 2>$null } catch {} finally { $ErrorActionPreference = $oldEAP }
}
Add-UserPath $BinDir
if (Have "python3") { Ok "python3 command available" } else { Warn "python3 shim created; open a new terminal if this shell cannot see it yet" }

# --- 3. Locate the project ---
# We run from inside the project (the .bat sits at tools\install\windows). Just
# work in that folder — installing dependencies is all this script does; how the
# student got the project here (zip, clone, ...) doesn't matter.
Section "Project folder"
$Target = $RepoFromZip
Set-Location $Target
Ok "using project folder: $Target"

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
# torch on Windows needs the Microsoft Visual C++ runtime or "import torch" dies
# with a DLL load error — make sure it's there before we build the venv.
Ensure-VCRedist
$VadPy = Join-Path $VadEnv "Scripts\python.exe"
# The venv python prints tracebacks to stderr; under EAP=Stop that stderr would
# terminate the whole script (and skip the .env + final steps). Run this section
# with EAP=Continue and rely on exit codes / Test-Path instead.
$oldEAP = $ErrorActionPreference; $ErrorActionPreference = "Continue"
try {
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
    & $VadPy -m pip install --quiet --upgrade pip 2>$null | Out-Null
    Info "installing torch + silero-vad (this is the slow download) ..."
    & $VadPy -m pip install --quiet silero-vad soundfile numpy 2>$null
    & $VadPy -m pip install --quiet torchcodec 2>$null
    & $VadPy -c "from silero_vad import load_silero_vad" 2>$null
    if ($LASTEXITCODE -eq 0) { Ok "Silero VAD installed" }
    else { Warn "Silero VAD verify failed. If you saw a VC++ runtime warning, install https://aka.ms/vs/17/release/vc_redist.x64.exe then re-run." }
  }
} finally { $ErrorActionPreference = $oldEAP }

# --- 6. .env — write the keys collected up front. ---
Section "Saving API keys to .env"
$EnvDir  = "templates\_shared\env"
$EnvFile = Join-Path $EnvDir ".env"
New-Item -ItemType Directory -Force -Path $EnvDir | Out-Null

# Start from the example (keeps the optional-key comments), then set the two
# keys we collected. If .env already exists, update those two lines in place so
# we never clobber other keys the user may have added. Read as UTF-8 so the
# comment em-dashes don't get mangled on a non-UTF-8 codepage (e.g. Thai CP874).
$lines =
  if (Test-Path $EnvFile) { Get-Content $EnvFile -Encoding UTF8 }
  elseif (Test-Path (Join-Path $EnvDir ".env.example")) { Get-Content (Join-Path $EnvDir ".env.example") -Encoding UTF8 }
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
# Write UTF-8 WITHOUT a BOM — bash/python .env parsers can choke on a leading BOM.
$EnvFileFull = Join-Path $Target $EnvFile
[System.IO.File]::WriteAllLines($EnvFileFull, $lines, (New-Object System.Text.UTF8Encoding($false)))
Ok "API keys saved to $EnvFile"

# --- Done ---
Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  Setup complete — no WSL needed." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host @"

Next steps:
  1. Make sure your ElevenLabs key is in:
       $Target\templates\_shared\env\.env
       (get one at https://elevenlabs.io/app/settings/api-keys)
  2. Open this project folder in VS Code, then open the Claude Code panel
     (the Claude Code extension). Tell Claude: "edit this clip with Template 01"

"@
if ($Interactive) { Read-Host "Press Enter to close" }
