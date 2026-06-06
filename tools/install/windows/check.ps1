# check.ps1 — BIZDRIVE Video, "is everything installed?" checker.
#
# Double-click 2-CHECK.bat (which runs this). Prints a green/red list of
# every tool the pipeline needs, plus whether the API keys are filled in.
# Read-only — it installs nothing.

$RepoUrl = "https://github.com/gobank01/bizdrive-video-workflow"
$VadEnv  = Join-Path $HOME ".ii23\vad-env"
$Repo    = Join-Path $HOME "bizdrive-video-workflow"

$pass = 0; $fail = 0
function Have($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Yes($label, $detail) { Write-Host "  [OK]   $label" -ForegroundColor Green -NoNewline; if ($detail) { Write-Host "  $detail" -ForegroundColor DarkGray } else { Write-Host "" }; $script:pass++ }
function No($label, $hint)    { Write-Host "  [X]    $label" -ForegroundColor Red   -NoNewline; if ($hint)   { Write-Host "  → $hint" -ForegroundColor Yellow } else { Write-Host "" }; $script:fail++ }

# Make sure tools installed earlier in the same session are visible.
$env:Path = "$([System.Environment]::GetEnvironmentVariable('Path','Machine'));$([System.Environment]::GetEnvironmentVariable('Path','User'))"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BIZDRIVE Video — install check" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- System tools ---
if (Have "git")    { Yes "Git"     ((git --version) 2>$null) }              else { No "Git"     "re-run the installer" }
if (Have "ffmpeg") { Yes "ffmpeg"  (((ffmpeg -version 2>$null) | Select-Object -First 1)) } else { No "ffmpeg" "re-run the installer" }
if (Have "ffprobe"){ Yes "ffprobe" "" }                                     else { No "ffprobe" "ships with ffmpeg — re-run installer" }

$pyCmd = if (Have "python3") { "python3" } elseif (Have "py") { "py" } elseif (Have "python") { "python" } else { $null }
if ($pyCmd) { Yes "Python"  ((& $pyCmd --version 2>&1)) }                   else { No "Python"  "re-run the installer" }
if (Have "python3") { Yes "python3 command" "" }                            else { No "python3 command" "shim missing — re-run installer, open a NEW terminal" }
if (Have "node")   { Yes "Node.js"  ((node --version) 2>$null) }            else { No "Node.js"  "re-run the installer" }
if (Have "claude") { Yes "Claude Code" "" }                                 else { No "Claude Code" "run: irm https://claude.ai/install.ps1 | iex" }

# --- Silero VAD venv ---
$vadPy = Join-Path $VadEnv "Scripts\python.exe"
if (Test-Path $vadPy) {
  & $vadPy -c "from silero_vad import load_silero_vad" 2>$null
  if ($LASTEXITCODE -eq 0) { Yes "Silero VAD (voice detection)" "" } else { No "Silero VAD" "venv exists but broken — re-run installer" }
} else { No "Silero VAD" "not installed — re-run installer" }

# --- Thai NLP (pythainlp; nlpo3 optional) ---
if ($pyCmd) {
  & $pyCmd -c "import pythainlp" 2>$null
  if ($LASTEXITCODE -eq 0) { Yes "Thai NLP (pythainlp)" "" } else { No "Thai NLP (pythainlp)" "re-run installer" }
}

# --- HyperFrames skills (installed by `npx hyperframes skills`) ---
if (Test-Path (Join-Path $HOME ".claude\skills\hyperframes")) {
  Yes "HyperFrames skills" ""
} else {
  No "HyperFrames skills" "run: npx hyperframes skills (then restart Claude)"
}

# --- Repo present ---
if (Test-Path (Join-Path $Repo ".git")) { Yes "Project files" $Repo } else { No "Project files" "clone: git clone $RepoUrl.git into your home folder" }

# --- API keys in .env ---
$envFile = Join-Path $Repo "templates\_shared\env\.env"
if (Test-Path $envFile) {
  $envTxt = Get-Content $envFile -Raw
  if ($envTxt -match "(?m)^\s*ELEVENLABS_API_KEY=\S+") { Yes "ElevenLabs API key" "" } else { No "ElevenLabs API key" "required — add it to $envFile" }
  if ($envTxt -match "(?m)^\s*OPENROUTER_API_KEY=\S+") { Yes "OpenRouter API key" "" } else { No "OpenRouter API key" "needed for B-roll — add it to $envFile" }
} else {
  No "ElevenLabs API key" "no .env yet — re-run installer"
  No "OpenRouter API key" "no .env yet — re-run installer"
}

# --- Verdict ---
Write-Host ""
Write-Host "------------------------------------------------------------"
if ($fail -eq 0) {
  Write-Host "  ALL GOOD ($pass checks passed) — you're ready to make videos." -ForegroundColor Green
  Write-Host ""
  Write-Host "  Next:  cd ~\bizdrive-video-workflow  then  claude"
} else {
  Write-Host "  $fail item(s) missing, $pass OK. Fix the red lines above," -ForegroundColor Yellow
  Write-Host "  then double-click 2-CHECK.bat again." -ForegroundColor Yellow
}
Write-Host "------------------------------------------------------------"
Write-Host ""
Read-Host "Press Enter to close"
