# Enable Claude Code "skip permissions" so Claude never stops to ask during the
# video pipeline. Sets two VS Code settings for the Claude Code extension:
#   claudeCode.allowDangerouslySkipPermissions = true   (unlocks bypass mode)
#   claudeCode.initialPermissionMode           = bypassPermissions  (new chats start in it)
#
# Run once, in PowerShell (works on Windows 10 & 11, any PowerShell version):
#   powershell -ExecutionPolicy Bypass -File tools\enable-claude-bypass.ps1
#
# Requires: VS Code + the Claude Code extension already installed.
# Safe: backs up settings.json first; inserts/updates only the two keys via text
#       edit (does NOT re-serialize the whole file, so comments/formatting and
#       every other setting are preserved).

$ErrorActionPreference = "Stop"

$settingsPath = Join-Path $env:APPDATA "Code\User\settings.json"
Write-Host "Claude Code - enable skip-permissions (bypass mode)"
Write-Host "Settings file: $settingsPath`n"

$dir = Split-Path $settingsPath
if (-not (Test-Path $dir)) {
    Write-Host "VS Code user folder not found at $dir" -ForegroundColor Yellow
    Write-Host "Open VS Code once (and install the Claude Code extension), then re-run this." -ForegroundColor Yellow
    exit 1
}

# Start from existing content, or a fresh empty object.
if (Test-Path $settingsPath) {
    $stamp  = Get-Date -Format "yyyyMMdd-HHmmss"
    $backup = "$settingsPath.bak.$stamp"
    Copy-Item $settingsPath $backup
    Write-Host "Backed up existing settings -> $backup"
    $text = Get-Content $settingsPath -Raw
    if (-not $text.Trim()) { $text = "{`n}" }
} else {
    $text = "{`n}"
}

# upsert-key: replace the key's value if the key already exists, else insert a
# new line right after the opening brace. Text-level edit — no JSON parsing, so
# it can't corrupt other settings or trip over // comments / trailing commas.
function Set-JsonKey {
    param([string]$content, [string]$key, [string]$rawValue)
    $escKey = [regex]::Escape($key)
    # match  "key" : <anything up to , or newline or closing brace>
    $pattern = '("' + $escKey + '"\s*:\s*)([^,\r\n}]*)'
    if ([regex]::IsMatch($content, $pattern)) {
        return [regex]::Replace($content, $pattern, ('${1}' + $rawValue), 1)
    }
    # insert after the first {
    $idx = $content.IndexOf("{")
    if ($idx -lt 0) { return "{`n  `"$key`": $rawValue`n}" }
    $insert = "`n  `"$key`": $rawValue,"
    return $content.Insert($idx + 1, $insert)
}

$text = Set-JsonKey $text "claudeCode.allowDangerouslySkipPermissions" "true"
$text = Set-JsonKey $text "claudeCode.initialPermissionMode" '"bypassPermissions"'

Set-Content $settingsPath -Value $text -Encoding UTF8

Write-Host "`nDone. Set:" -ForegroundColor Green
Write-Host '  claudeCode.allowDangerouslySkipPermissions = true'
Write-Host '  claudeCode.initialPermissionMode           = bypassPermissions'
Write-Host "`nNow reload VS Code (Ctrl+Shift+P -> 'Reload Window'). New Claude chats start in bypass mode — no permission popups." -ForegroundColor Cyan
Write-Host "Warning: bypass mode lets Claude run commands and edit files without asking. Use on machines you trust." -ForegroundColor Yellow
