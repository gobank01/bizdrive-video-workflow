#!/usr/bin/env bash
#
# Scaffold a new template from the _starter skeleton.
#
# Usage:
#   bash tools/new-template.sh <number> <slug>
#
# Example:
#   bash tools/new-template.sh 02 horizontal-talking-head
#   → creates templates/02-horizontal-talking-head/ from templates/_starter/
#
# After scaffolding, customize:
#   - manifest.json   (aspect, fps, caption style, gold rule)
#   - index.html      (composition layout)
#   - DESIGN.md       (colors, fonts, position)
#   - prompts/        (subagent slot defaults)

set -e

if [ $# -lt 2 ]; then
  echo "Usage: bash tools/new-template.sh <number> <slug>" >&2
  echo "Example: bash tools/new-template.sh 02 horizontal-talking-head" >&2
  exit 1
fi

NUM=$1
SLUG=$2
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Pad number to 2 digits
NUM=$(printf "%02d" "$NUM")

STARTER="$REPO_ROOT/templates/_starter"
NEW_TEMPLATE="$REPO_ROOT/templates/${NUM}-${SLUG}"

if [ ! -d "$STARTER" ]; then
  echo "✗ Starter not found at $STARTER" >&2
  exit 1
fi

if [ -d "$NEW_TEMPLATE" ]; then
  echo "✗ Template already exists: $NEW_TEMPLATE" >&2
  exit 1
fi

echo "→ Cloning starter → $NEW_TEMPLATE"
cp -r "$STARTER" "$NEW_TEMPLATE"

# Replace placeholder __TEMPLATE_NUMBER__ and __TEMPLATE_SLUG__ in copied files
find "$NEW_TEMPLATE" -type f \( -name "*.md" -o -name "*.json" -o -name "*.html" \) | while read -r f; do
  if [ "$(uname)" = "Darwin" ]; then
    sed -i '' "s/__TEMPLATE_NUMBER__/${NUM}/g; s/__TEMPLATE_SLUG__/${SLUG}/g" "$f"
  else
    sed -i "s/__TEMPLATE_NUMBER__/${NUM}/g; s/__TEMPLATE_SLUG__/${SLUG}/g" "$f"
  fi
done

# RULE: the Template Manager display file always stays in sync with the set of
# templates. Re-generate it now so the new template appears in
# tools/template-manager.html. See templates/_shared/docs/JOB_SPEC.md §4.
if [ -f "$REPO_ROOT/tools/build-manager.py" ]; then
  if python3 "$REPO_ROOT/tools/build-manager.py" >/dev/null 2>&1; then
    echo "→ Template Manager synced (tools/template-manager.html)"
  else
    echo "⚠ build-manager.py failed — run it manually: python3 tools/build-manager.py"
  fi
fi

echo ""
echo "✓ Template scaffolded: $NEW_TEMPLATE"
echo ""
echo "Next:"
echo "  1. Edit templates/${NUM}-${SLUG}/manifest.json  (aspect, fps, caption style,"
echo "     and the features[] block — the toggles the Template Manager will show)"
echo "  2. Edit templates/${NUM}-${SLUG}/DESIGN.md      (colors, fonts, position)"
echo "  3. Edit templates/${NUM}-${SLUG}/index.html     (composition layout)"
echo "  4. Edit templates/${NUM}-${SLUG}/prompts/       (subagent slot defaults)"
echo "  5. Add to templates/README.md comparison table"
echo "  6. Re-run: python3 tools/build-manager.py  (after editing manifest.json)"
echo ""
echo "Then test with: bash tools/new-job.sh ${NUM} test-slug"
echo "After the first render, refresh the visual index: bash tools/build-catalog.sh"
