#!/usr/bin/env bash
# Enable Claude Code "skip permissions" so Claude never stops to ask during the
# video pipeline. Sets two VS Code settings for the Claude Code extension:
#   claudeCode.allowDangerouslySkipPermissions = true   (unlocks bypass mode)
#   claudeCode.initialPermissionMode           = bypassPermissions  (new chats start in it)
#
# Run once:  bash tools/enable-claude-bypass.sh
# Requires:  VS Code + the Claude Code extension already installed.
# Safe:      backs up settings.json first, merges (does not overwrite other settings).
set -euo pipefail

case "$(uname -s)" in
  Darwin*) SETTINGS="$HOME/Library/Application Support/Code/User/settings.json" ;;
  Linux*)  SETTINGS="$HOME/.config/Code/User/settings.json" ;;
  *)       echo "Unsupported OS. On Windows use tools/enable-claude-bypass.ps1" >&2; exit 1 ;;
esac

echo "Claude Code — enable skip-permissions (bypass mode)"
echo "Settings file: $SETTINGS"

DIR="$(dirname "$SETTINGS")"
if [ ! -d "$DIR" ]; then
  echo "VS Code user folder not found. Open VS Code once + install the Claude Code extension, then re-run." >&2
  exit 1
fi

if [ -f "$SETTINGS" ]; then
  BACKUP="$SETTINGS.bak.$(date +%Y%m%d-%H%M%S 2>/dev/null || echo manual)"
  cp "$SETTINGS" "$BACKUP"
  echo "Backed up existing settings -> $BACKUP"
fi

# VS Code settings.json is JSONC (// comments, trailing commas). Strip those,
# then merge the two keys without clobbering anything else.
python3 - "$SETTINGS" <<'PY'
import json, re, sys, os
p = sys.argv[1]
raw = ""
if os.path.exists(p):
    raw = open(p, encoding="utf-8").read()

# String-aware JSONC -> JSON: drop // and /* */ comments, but NEVER inside a
# string (so "https://..." values survive). Then remove trailing commas.
def strip_jsonc(s):
    out = []
    i, n = 0, len(s)
    in_str = False
    while i < n:
        c = s[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:      # keep escaped char as-is
                out.append(s[i+1]); i += 2; continue
            if c == '"':
                in_str = False
            i += 1; continue
        if c == '"':
            in_str = True; out.append(c); i += 1; continue
        if c == "/" and i + 1 < n and s[i+1] == "/":
            i += 2
            while i < n and s[i] not in "\r\n": i += 1
            continue
        if c == "/" and i + 1 < n and s[i+1] == "*":
            i += 2
            while i + 1 < n and not (s[i] == "*" and s[i+1] == "/"): i += 1
            i += 2; continue
        out.append(c); i += 1
    return "".join(out)

raw = strip_jsonc(raw)
raw = re.sub(r",(\s*[}\]])", r"\1", raw)       # trailing commas
try:
    obj = json.loads(raw) if raw.strip() else {}
except Exception:
    print("Could not parse settings.json — add these two keys manually:", file=sys.stderr)
    print('  "claudeCode.allowDangerouslySkipPermissions": true,', file=sys.stderr)
    print('  "claudeCode.initialPermissionMode": "bypassPermissions"', file=sys.stderr)
    sys.exit(1)
if not isinstance(obj, dict):
    obj = {}
obj["claudeCode.allowDangerouslySkipPermissions"] = True
obj["claudeCode.initialPermissionMode"] = "bypassPermissions"
json.dump(obj, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY

echo ""
echo "Done. New Claude chats start in bypass mode — no permission popups."
echo "Reload VS Code (Cmd/Ctrl+Shift+P -> 'Reload Window') to apply."
echo "Warning: bypass mode lets Claude run commands and edit files without asking. Use on machines you trust."
