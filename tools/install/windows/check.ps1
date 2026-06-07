# check.ps1 — BIZDRIVE Video, "are the dependencies installed?" checker.
#
# Double-click 2-CHECK.bat (which runs this). Prints a green/red list of
# every tool the pipeline needs, plus whether the ElevenLabs key is filled in.
# Read-only — it installs nothing.

# Show UTF-8 (Thai) correctly regardless of the machine's codepage.
try {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}
$Interactive = $true
try { $Interactive = -not [Console]::IsInputRedirected } catch {}

$VadEnv = Join-Path $HOME ".bizdrive\vad-env"

# This checker lives at <repo>\tools\install\windows\check.ps1; the project is the
# folder we're inside (3 levels up) — used only to find the .env file.
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$Repo = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path

$pass = 0; $fail = 0

# Have(): true if a REAL command exists. Ignore the Microsoft Store
# "App execution alias" python/python3 stubs under ...\WindowsApps.
function Have($cmd) {
  $cmds = @(Get-Command $cmd -All -ErrorAction SilentlyContinue)
  foreach ($c in $cmds) {
    if ($c.Source -and ($c.Source -match '\\Microsoft\\WindowsApps\\python(3)?\.exe$')) { continue }
    return $true
  }
  return $false
}
function Yes($label, $detail) { Write-Host "  [OK]   $label" -ForegroundColor Green -NoNewline; if ($detail) { Write-Host "  $detail" -ForegroundColor DarkGray } else { Write-Host "" }; $script:pass++ }
function No($label, $hint)    { Write-Host "  [X]    $label" -ForegroundColor Red   -NoNewline; if ($hint)   { Write-Host "  -> $hint" -ForegroundColor Yellow } else { Write-Host "" }; $script:fail++ }

# Make tools installed earlier visible, including spots PATH doesn't always pick up.
$env:Path = "$([System.Environment]::GetEnvironmentVariable('Path','Machine'));$([System.Environment]::GetEnvironmentVariable('Path','User'))"
foreach ($d in @(
  (Join-Path $HOME ".bizdrive\bin"),
  (Join-Path $HOME ".bizdrive\node"),
  "$env:ProgramFiles\nodejs"
)) { if ((Test-Path $d) -and (($env:Path -split ";") -notcontains $d)) { $env:Path = "$env:Path;$d" } }

# Return the version string if <exe [arg]> is python >= 3.10, else $null.
function Get-PyVer($exe, $argList) {
  $eap = $ErrorActionPreference; $ErrorActionPreference = "SilentlyContinue"
  try {
    $a = @(); foreach ($x in $argList) { if ($x) { $a += $x } }
    $a += @("-c", "import sys;print('.'.join(map(str,sys.version_info[:3])))")
    $o = (& $exe @a 2>$null | Select-Object -First 1)
    if ($o -and ($o -match '^(\d+)\.(\d+)')) {
      if (([int]$Matches[1] -gt 3) -or ([int]$Matches[1] -eq 3 -and [int]$Matches[2] -ge 10)) { return $o.Trim() }
    }
  } catch {} finally { $ErrorActionPreference = $eap }
  return $null
}
# Resolve a usable python (>=3.10), preferring a real python.exe full path.
function Resolve-Py {
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
      foreach ($c in $cands) { $v = Get-PyVer $c.FullName @(); if ($v) { return @{ exe = $c.FullName; ver = $v } } }
    }
  }
  if (Have "py") { foreach ($x in @("-3.13","-3.12","-3.11","-3.10","-3")) { $v = Get-PyVer "py" @($x); if ($v) { return @{ exe = "py"; args = @($x); ver = $v } } } }
  foreach ($n in @("python3","python")) { if (Have $n) { $v = Get-PyVer $n @(); if ($v) { return @{ exe = $n; ver = $v } } } }
  return $null
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BIZDRIVE Video — install check" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- System tools ---
if (Have "git")    { Yes "Git"     ((git --version) 2>$null) }              else { No "Git"     "re-run the installer" }
if (Have "ffmpeg") { Yes "ffmpeg"  (((ffmpeg -version 2>$null) | Select-Object -First 1)) } else { No "ffmpeg" "re-run the installer" }
if (Have "ffprobe"){ Yes "ffprobe" "" }                                     else { No "ffprobe" "ships with ffmpeg — re-run installer" }

$py = Resolve-Py
if ($py) { Yes "Python"  ("Python " + $py.ver) }                            else { No "Python"  "re-run the installer (or disable the Microsoft Store python alias)" }
if (Have "python3") { Yes "python3 command" "" }                            else { No "python3 command" "shim missing — re-run installer, open a NEW terminal" }
if (Have "node")   { Yes "Node.js"  ((node --version) 2>$null) }            else { No "Node.js"  "re-run the installer" }

# --- Silero VAD venv ---
$vadPy = Join-Path $VadEnv "Scripts\python.exe"
if (Test-Path $vadPy) {
  $eap = $ErrorActionPreference; $ErrorActionPreference = "SilentlyContinue"
  try { & $vadPy -c "from silero_vad import load_silero_vad" 2>$null } finally { $ErrorActionPreference = $eap }
  if ($LASTEXITCODE -eq 0) { Yes "Silero VAD (voice detection)" "" } else { No "Silero VAD" "venv exists but broken (VC++ runtime missing?) — re-run installer" }
} else { No "Silero VAD" "not installed — re-run installer" }

# --- Thai NLP (pythainlp; nlpo3 optional) ---
if ($py) {
  $eap = $ErrorActionPreference; $ErrorActionPreference = "SilentlyContinue"
  try { $a=@(); if ($py.args) { foreach($x in $py.args){$a+=$x} }; $a+=@("-c","import pythainlp"); & $py.exe @a 2>$null } finally { $ErrorActionPreference = $eap }
  if ($LASTEXITCODE -eq 0) { Yes "Thai NLP (pythainlp)" "" } else { No "Thai NLP (pythainlp)" "re-run installer" }
} else { No "Thai NLP (pythainlp)" "Python missing — re-run installer" }

# --- API keys in .env ---
$envFile = Join-Path $Repo "templates\_shared\env\.env"
if (Test-Path $envFile) {
  $envTxt = Get-Content $envFile -Raw
  if ($envTxt -match "(?m)^\s*ELEVENLABS_API_KEY=\S+") { Yes "ElevenLabs API key" "" } else { No "ElevenLabs API key" "required — add it to $envFile" }
  if ($envTxt -match "(?m)^\s*OPENROUTER_API_KEY=\S+") { Yes "OpenRouter API key (optional)" "" } else { Write-Host "  [--]   OpenRouter API key (optional)  not set — only needed for AI B-roll" -ForegroundColor DarkGray }
} else {
  No "ElevenLabs API key" "no .env yet — re-run installer (or add the key by hand)"
}

# --- Verdict ---
Write-Host ""
Write-Host "------------------------------------------------------------"
if ($fail -eq 0) {
  Write-Host "  ALL GOOD ($pass checks passed) — dependencies are ready." -ForegroundColor Green
  Write-Host ""
  Write-Host "  Next: open this folder in VS Code and use the Claude Code panel."
} else {
  Write-Host "  $fail item(s) missing, $pass OK. Fix the red lines above," -ForegroundColor Yellow
  Write-Host "  then double-click 2-CHECK.bat again." -ForegroundColor Yellow
}
Write-Host "------------------------------------------------------------"
Write-Host ""
if ($Interactive) { Read-Host "Press Enter to close" }
