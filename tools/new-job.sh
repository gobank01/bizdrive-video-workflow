#!/usr/bin/env bash
#
# Scaffold a new job from a template.
#
# Usage:
#   bash tools/new-job.sh <template-number> <slug>
#
# Example:
#   bash tools/new-job.sh 01 promo-may-25
#   → creates jobs/2026-MM-DD-promo-may-25/{input,intermediates,output,workspace}
#   → workspace has copy of template-01 + symlinks to intermediates and _shared resources
#
# Requirements: bash, ln, cp, mkdir

set -e

if [ $# -lt 2 ]; then
  echo "Usage: bash tools/new-job.sh <template-number> <slug>" >&2
  echo "Example: bash tools/new-job.sh 01 promo-may-25" >&2
  exit 1
fi

TEMPLATE_NUM=$1
SLUG=$2
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Find template dir by prefix
TEMPLATE_DIR=$(find "$REPO_ROOT/templates" -maxdepth 1 -type d -name "${TEMPLATE_NUM}-*" | head -1)
if [ -z "$TEMPLATE_DIR" ]; then
  echo "✗ No template found matching ${TEMPLATE_NUM}-*. Available templates:" >&2
  find "$REPO_ROOT/templates" -maxdepth 1 -type d -name '[0-9]*' -exec basename {} \; >&2
  exit 1
fi
TEMPLATE_NAME=$(basename "$TEMPLATE_DIR")
echo "→ Using template: $TEMPLATE_NAME"

# Build job dir name
DATE=$(date +%Y-%m-%d)
JOB_NAME="${DATE}-${SLUG}"
JOB_DIR="$REPO_ROOT/jobs/$JOB_NAME"

if [ -d "$JOB_DIR" ]; then
  echo "✗ Job already exists: $JOB_DIR" >&2
  exit 1
fi

echo "→ Creating job: $JOB_NAME"
mkdir -p "$JOB_DIR/input"
mkdir -p "$JOB_DIR/intermediates"
mkdir -p "$JOB_DIR/output/finals"
mkdir -p "$JOB_DIR/output/reports"
mkdir -p "$JOB_DIR/workspace"

# Write job manifest
cat > "$JOB_DIR/manifest.json" <<EOF
{
  "id": "${JOB_NAME}",
  "template": "${TEMPLATE_NAME}",
  "createdAt": "${DATE}",
  "status": "scaffolded",
  "source": {
    "top": "input/top.mp4",
    "bottom": "input/bottom.mp4",
    "bg": "input/bg.png"
  },
  "notes": "Drop source files into input/, then follow templates/_shared/docs/V88_PLAYBOOK.md"
}
EOF

cat > "$JOB_DIR/notes.md" <<EOF
# Job Notes — ${JOB_NAME}

Template: ${TEMPLATE_NAME}
Scaffolded: ${DATE}

## Next steps

1. Drop input files:
   - \`input/top.mp4\` (screen recording, will be muted in final)
   - \`input/bottom.mp4\` (face video, contains master audio)
   - \`input/bg.png\` (background image)

2. Follow the 15-step playbook:
   - Open \`templates/_shared/docs/V88_PLAYBOOK.md\`
   - Replace \`<JOB>\` with \`${JOB_NAME}\`
   - Replace \`<INPUT_DIR>\` with \`jobs/${JOB_NAME}/input\`

3. Subagent prompts:
   - Step 3 (editorial): \`templates/_shared/docs/SUBAGENT_PROMPTS.md\` Section A
   - Step 10 (post-process): \`templates/_shared/docs/SUBAGENT_PROMPTS.md\` Section B
   - Slot defaults for ${TEMPLATE_NAME}: \`${TEMPLATE_DIR#$REPO_ROOT/}/prompts/\`

4. Render happens in \`workspace/\` (already set up with symlinks).
EOF

# Build workspace
WS="$JOB_DIR/workspace"
echo "→ Building workspace at $WS"

# Copy core composition files
cp "$TEMPLATE_DIR/index.html" "$WS/" 2>/dev/null || echo "  (no index.html in template — create one)"
cp "$TEMPLATE_DIR/hyperframes.json" "$WS/" 2>/dev/null || true
cp "$TEMPLATE_DIR/meta.json" "$WS/" 2>/dev/null || true
cp "$TEMPLATE_DIR/package.json" "$WS/" 2>/dev/null || true
[ -d "$TEMPLATE_DIR/compositions" ] && cp -r "$TEMPLATE_DIR/compositions" "$WS/"
[ -d "$TEMPLATE_DIR/backups" ] && cp -r "$TEMPLATE_DIR/backups" "$WS/"

# Copy template-specific scripts; symlink shared ones
mkdir -p "$WS/scripts"
[ -d "$TEMPLATE_DIR/scripts" ] && cp -r "$TEMPLATE_DIR/scripts/." "$WS/scripts/" 2>/dev/null || true
ln -sf "../../../../templates/_shared/scripts/transcribe" "$WS/scripts/transcribe"
ln -sf "../../../../templates/_shared/scripts/clean-cut" "$WS/scripts/clean-cut"

# Symlink _shared resources
ln -sf "../../../templates/_shared/bgm-library" "$WS/bgm-library"
ln -sf "../../../templates/_shared/schemas" "$WS/schemas"
ln -sf "../../../templates/_shared/env/.env" "$WS/.env"
ln -sf "../../../templates/_shared/env/.env.example" "$WS/.env.example"

# Set up assets/ with paths that match template's index.html expectations
mkdir -p "$WS/assets"
ln -sf "../../intermediates" "$WS/assets/intermediates"  # generic catch-all
ln -sf "../../../../templates/_shared/broll" "$WS/assets/broll"
ln -sf "../../../../templates/_shared/bgm" "$WS/assets/bgm"

# Symlink input/ for convenience
ln -sf "../input" "$WS/assets/input"

echo ""
echo "✓ Job scaffolded: $JOB_DIR"
echo ""
echo "Next:"
echo "  1. Drop input files into: jobs/${JOB_NAME}/input/{top.mp4, bottom.mp4, bg.png}"
echo "  2. Follow templates/_shared/docs/V88_PLAYBOOK.md"
echo "  3. Render workspace: cd jobs/${JOB_NAME}/workspace && npm run check"
echo ""
echo "For Template ${TEMPLATE_NUM} specific defaults: ${TEMPLATE_DIR#$REPO_ROOT/}/prompts/"
