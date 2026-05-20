#!/usr/bin/env bash
#
# Scaffold a new job from a template.
#
# Usage:
#   bash tools/new-job.sh <template-number> <slug> [--raw <raw-media-slug>] [--date <YYYY-MM-DD>]
#
# Examples:
#   # 1. Scaffold empty job (drop files into input/ manually later)
#   bash tools/new-job.sh 01 promo-may-25
#
#   # 2. Scaffold + symlink input/ to existing raw clip
#   bash tools/new-job.sh 01 promo-may-25 --raw 2026-05-20-promo-may-recording
#
#   # 3. Scaffold with explicit date
#   bash tools/new-job.sh 01 promo-may-25 --date 2026-05-25
#
# Requirements: bash, ln, cp, mkdir

set -e

# --- Parse args ---
TEMPLATE_NUM=""
SLUG=""
RAW_SLUG=""
DATE=$(date +%Y-%m-%d)
POSITIONAL=()

while [ $# -gt 0 ]; do
  case "$1" in
    --raw)
      RAW_SLUG="$2"; shift 2 ;;
    --date)
      DATE="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *)
      POSITIONAL+=("$1"); shift ;;
  esac
done

if [ ${#POSITIONAL[@]} -lt 2 ]; then
  echo "Usage: bash tools/new-job.sh <template-number> <slug> [--raw <raw-media-slug>] [--date YYYY-MM-DD]" >&2
  exit 1
fi
TEMPLATE_NUM=${POSITIONAL[0]}
SLUG=${POSITIONAL[1]}
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- Find template ---
TEMPLATE_DIR=$(find "$REPO_ROOT/templates" -maxdepth 1 -type d -name "${TEMPLATE_NUM}-*" | head -1)
if [ -z "$TEMPLATE_DIR" ]; then
  echo "✗ No template found matching ${TEMPLATE_NUM}-*. Available templates:" >&2
  find "$REPO_ROOT/templates" -maxdepth 1 -type d -name '[0-9]*' -exec basename {} \; >&2
  exit 1
fi
TEMPLATE_NAME=$(basename "$TEMPLATE_DIR")
echo "→ Using template: $TEMPLATE_NAME"

# --- Validate --raw if provided ---
RAW_DIR=""
if [ -n "$RAW_SLUG" ]; then
  RAW_DIR="$REPO_ROOT/raw-media/$RAW_SLUG"
  if [ ! -d "$RAW_DIR" ]; then
    echo "✗ Raw clip not found: $RAW_DIR" >&2
    echo "  Available raw clips:" >&2
    find "$REPO_ROOT/raw-media" -maxdepth 1 -type d -not -name '_*' -not -path "$REPO_ROOT/raw-media" -exec basename {} \; >&2 2>/dev/null
    exit 1
  fi
  echo "→ Will symlink input/ from: raw-media/$RAW_SLUG"
fi

# --- Build job dir ---
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

# --- Symlink input/ from raw-media if --raw provided ---
if [ -n "$RAW_DIR" ]; then
  for f in top.mp4 bottom.mp4 bg.png; do
    if [ -e "$RAW_DIR/$f" ]; then
      ln -sf "../../../raw-media/$RAW_SLUG/$f" "$JOB_DIR/input/$f"
      echo "  ✓ input/$f → raw-media/$RAW_SLUG/$f"
    else
      echo "  ⚠ raw-media/$RAW_SLUG/$f missing — skipping"
    fi
  done
fi

# --- Write job manifest ---
cat > "$JOB_DIR/manifest.json" <<EOF
{
  "id": "${JOB_NAME}",
  "template": "${TEMPLATE_NAME}",
  "createdAt": "${DATE}",
  "status": "scaffolded",
  "source": {
    "rawSlug": "${RAW_SLUG}",
    "top": "input/top.mp4",
    "bottom": "input/bottom.mp4",
    "bg": "input/bg.png"
  },
  "notes": "Follow templates/_shared/docs/V88_PLAYBOOK.md to run the pipeline."
}
EOF

# --- Write job notes ---
cat > "$JOB_DIR/notes.md" <<EOF
# Job Notes — ${JOB_NAME}

Template: ${TEMPLATE_NAME}
Scaffolded: ${DATE}
Raw clip: ${RAW_SLUG:-"(not linked — drop files manually into input/)"}

## Next steps

1. ${RAW_SLUG:+input/ already symlinked to raw-media/${RAW_SLUG}/.}${RAW_SLUG:-Drop input files into input/{top.mp4, bottom.mp4, bg.png}.}

2. Follow the 15-step playbook:
   - Open \`templates/_shared/docs/V88_PLAYBOOK.md\`
   - Replace \`<JOB>\` with \`${JOB_NAME}\`
   - Replace \`<INPUT_DIR>\` with \`jobs/${JOB_NAME}/input\`

3. Subagent prompts:
   - Step 3 (editorial): \`templates/_shared/docs/SUBAGENT_PROMPTS.md\` Section A
   - Step 10 (post-process): \`templates/_shared/docs/SUBAGENT_PROMPTS.md\` Section B
   - Slot defaults for ${TEMPLATE_NAME}: \`${TEMPLATE_DIR#$REPO_ROOT/}/prompts/\`

4. Render in \`workspace/\` (already set up with symlinks).
EOF

# --- Build workspace ---
WS="$JOB_DIR/workspace"
echo "→ Building workspace at $WS"

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

# Assets — paths match template's index.html
mkdir -p "$WS/assets"
ln -sf "../../intermediates" "$WS/assets/intermediates"
ln -sf "../../../../templates/_shared/broll" "$WS/assets/broll"
ln -sf "../../../../templates/_shared/bgm" "$WS/assets/bgm"
ln -sf "../../input" "$WS/assets/input"

echo ""
echo "✓ Job scaffolded: $JOB_DIR"
echo ""
if [ -n "$RAW_SLUG" ]; then
  echo "Raw clip already linked. Next:"
  echo "  1. Follow templates/_shared/docs/V88_PLAYBOOK.md"
  echo "  2. cd jobs/${JOB_NAME}/workspace && npm run check"
else
  echo "Next:"
  echo "  1. Drop input files into: jobs/${JOB_NAME}/input/{top.mp4, bottom.mp4, bg.png}"
  echo "     (OR put them in raw-media/<slug>/ and re-run with --raw <slug>)"
  echo "  2. Follow templates/_shared/docs/V88_PLAYBOOK.md"
  echo "  3. cd jobs/${JOB_NAME}/workspace && npm run check"
fi
echo ""
echo "Template ${TEMPLATE_NUM} prompt defaults: ${TEMPLATE_DIR#$REPO_ROOT/}/prompts/"
