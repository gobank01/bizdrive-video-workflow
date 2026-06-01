#!/usr/bin/env bash
#
# longform-shipit.sh — full longform→shorts→delivered pipeline orchestrator.
#
# Wraps the four pieces (prep → Shorts Finder → split → v88-clip × N) into one
# resumable command. At every subagent point it writes a ready-to-paste prompt
# file and exits with code 100 so the caller (Claude / Codex / human) can
# spawn the subagent and re-run.
#
# Usage:
#
#   # First run — from a source video:
#   bash tools/01-longform-shorts/shipit.sh --source <video.mp4> --slug <slug> --topic "<one sentence>"
#
#   # Subsequent runs (resume) — staging dir is enough:
#   bash tools/01-longform-shorts/shipit.sh staging/longform/<date>-<slug>
#
# The script auto-detects which phase to run next based on which files exist
# in the staging dir and which child jobs are done.
#
# Exit codes:
#   0   — all clips delivered (final mp4 + thumbnail for every child)
#   100 — paused, subagent needed (see printed prompt path)
#   1   — error
#
# Workflow per source:
#   Phase 1   prep   → raw-elevenlabs.json + silence.json + PROMPT.md
#   Phase 1.5 ⏸ Shorts Finder subagent → shorts.json
#   Phase 2   split  → N child jobs in jobs/
#   Phase 3   per-clip v88-clip.sh (each one pauses 2x for subagents)
#
# Tips: re-running the script is cheap — every phase is idempotent.

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# --- Parse args ---
STAGE_DIR=""
SOURCE_VIDEO=""
SLUG=""
TOPIC=""
DATE=$(date +%Y-%m-%d)
TEMPLATE_OVERRIDE=""
POSITIONAL=()

while [ $# -gt 0 ]; do
  case "$1" in
    --source) SOURCE_VIDEO="$2"; shift 2 ;;
    --slug) SLUG="$2"; shift 2 ;;
    --topic) TOPIC="$2"; shift 2 ;;
    --date) DATE="$2"; shift 2 ;;
    --template) TEMPLATE_OVERRIDE="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

# Resolve staging dir
if [ ${#POSITIONAL[@]} -ge 1 ]; then
  ARG=${POSITIONAL[0]}
  if [[ "$ARG" = /* ]]; then STAGE_DIR="$ARG"; else STAGE_DIR="$REPO_ROOT/$ARG"; fi
elif [ -n "$SOURCE_VIDEO" ] && [ -n "$SLUG" ]; then
  STAGE_DIR="$REPO_ROOT/staging/longform/${DATE}-${SLUG}"
else
  echo "Usage:" >&2
  echo "  bash tools/01-longform-shorts/shipit.sh --source <video.mp4> --slug <slug> --topic \"<one sentence>\"" >&2
  echo "  bash tools/01-longform-shorts/shipit.sh <staging-dir>" >&2
  exit 1
fi

# ─────────────────────────────────────────────
# Phase 1 — prep (idempotent: skipped if raw-elevenlabs.json exists)
# ─────────────────────────────────────────────
if [ ! -f "$STAGE_DIR/raw-elevenlabs.json" ]; then
  if [ -z "$SOURCE_VIDEO" ] || [ -z "$SLUG" ]; then
    echo "✗ Staging dir not prepped yet, but --source / --slug missing." >&2
    echo "  Pass --source <video.mp4> --slug <slug> --topic \"...\" to run Phase 1." >&2
    exit 1
  fi
  echo "═══ Phase 1 — prep ═══"
  bash "$REPO_ROOT/tools/01-longform-shorts/prep.sh" "$SOURCE_VIDEO" "$SLUG" \
    --topic "$TOPIC" --date "$DATE"
  echo ""
fi

# ─────────────────────────────────────────────
# Phase 1.5 — Shorts Finder subagent
# ─────────────────────────────────────────────
if [ ! -f "$STAGE_DIR/shorts.json" ]; then
  echo "═══ Phase 1.5 ⏸ Shorts Finder subagent needed ═══"
  echo ""
  echo "  Read this file and feed it to a subagent:"
  echo "    $STAGE_DIR/PROMPT.md"
  echo ""
  echo "  Or just say to Claude: 'run shorts finder on ${STAGE_DIR#$REPO_ROOT/}'"
  echo ""
  echo "  When shorts.json is written, re-run:"
  echo "    bash tools/01-longform-shorts/shipit.sh ${STAGE_DIR#$REPO_ROOT/}"
  exit 100
fi

# ─────────────────────────────────────────────
# Phase 2 — split (idempotent: skipped if any child job exists)
# ─────────────────────────────────────────────
META_SLUG=$(python3 -c "import json; print(json.load(open('$STAGE_DIR/meta.json'))['slug'])")
META_DATE=$(python3 -c "import json; print(json.load(open('$STAGE_DIR/meta.json'))['date'])")
CHILD_PATTERN="jobs/${META_DATE}-${META_SLUG}-clip*"
CHILD_DIRS=( $(cd "$REPO_ROOT" && ls -d $CHILD_PATTERN 2>/dev/null || true) )

if [ ${#CHILD_DIRS[@]} -eq 0 ]; then
  echo "═══ Phase 2 — split ═══"
  ARGS=("$STAGE_DIR")
  [ -n "$TEMPLATE_OVERRIDE" ] && ARGS+=(--template "$TEMPLATE_OVERRIDE")
  bash "$REPO_ROOT/tools/01-longform-shorts/split.sh" "${ARGS[@]}"
  echo ""
  CHILD_DIRS=( $(cd "$REPO_ROOT" && ls -d $CHILD_PATTERN 2>/dev/null || true) )
fi

# ─────────────────────────────────────────────
# Phase 3 — loop v88-clip.sh on each child
# ─────────────────────────────────────────────
echo "═══ Phase 3 — v88-clip ${#CHILD_DIRS[@]} child jobs ═══"
echo ""

DONE_COUNT=0
PENDING_COUNT=0
DELIVERED=()
NEEDS_SUBAGENT=()

for CHILD_REL in "${CHILD_DIRS[@]}"; do
  CHILD_DIR="$REPO_ROOT/$CHILD_REL"
  CHILD_NAME=$(basename "$CHILD_DIR")
  FINAL_MP4="$CHILD_DIR/output/finals/$CHILD_NAME.mp4"
  if [ -f "$FINAL_MP4" ]; then
    DONE_COUNT=$((DONE_COUNT + 1))
    DELIVERED+=("$FINAL_MP4")
    echo "  ✓ $CHILD_NAME  (already delivered)"
    continue
  fi

  echo "─── $CHILD_NAME"
  set +e
  bash "$REPO_ROOT/tools/v88-clip.sh" "$CHILD_REL" 2>&1
  RC=$?
  set -e
  echo ""

  if [ "$RC" = "100" ]; then
    PENDING_COUNT=$((PENDING_COUNT + 1))
    NEEDS_SUBAGENT+=("$CHILD_NAME")
  elif [ "$RC" = "0" ]; then
    DONE_COUNT=$((DONE_COUNT + 1))
    DELIVERED+=("$FINAL_MP4")
  else
    echo "✗ v88-clip failed (exit $RC) for $CHILD_NAME" >&2
    exit 1
  fi
done

# ─────────────────────────────────────────────
echo "═══ shipit summary ═══"
echo "  delivered: $DONE_COUNT / ${#CHILD_DIRS[@]}"
if [ $DONE_COUNT -gt 0 ]; then
  for d in "${DELIVERED[@]}"; do
    echo "    ✓ ${d#$REPO_ROOT/}"
  done
fi

if [ $PENDING_COUNT -gt 0 ]; then
  echo ""
  echo "  $PENDING_COUNT clips waiting for subagent:"
  for n in "${NEEDS_SUBAGENT[@]}"; do
    echo "    ⏸ $n"
  done
  echo ""
  echo "  Spawn the subagents (each clip's prompt is at"
  echo "  jobs/<clip>/workspace/assets/intermediates/v88-test/editorial-prompt.txt"
  echo "  or .../post-process-prompt.txt) then re-run:"
  echo "    bash tools/01-longform-shorts/shipit.sh ${STAGE_DIR#$REPO_ROOT/}"
  exit 100
fi

echo ""
echo "✓ All ${#CHILD_DIRS[@]} clips delivered."
