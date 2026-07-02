#!/usr/bin/env bash
# clean-job.sh — strip a finished job down to its deliverables.
#
# Keeps ONLY  output/finals/<job>.mp4  +  output/finals/<job>.png
# Deletes      input/  intermediates/  workspace/  output/reports/  and every
#              other file in output/finals/ (visual.mp4, no-bgm.mp4, final.mp4 …).
#
# Safety: refuses to clean a job that has no canonical <job>.mp4 final (so a
# failed/in-progress render keeps its intermediates). Use --force to clean
# anyway (keeps whatever final.mp4 + *.png it finds, or nothing).
#
# Usage:
#   tools/clean-job.sh [--dry-run] [--force] jobs/<job-dir> [jobs/<job-dir> ...]
#   tools/clean-job.sh [--dry-run] [--force] --all          # every dir under jobs/
#
# This is wired as the final step of the v88 pipeline so new renders self-clean.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRY=0; FORCE=0; ALL=0
targets=()
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --force)   FORCE=1 ;;
    --all)     ALL=1 ;;
    *)         targets+=("$a") ;;
  esac
done

if [ "$ALL" -eq 1 ]; then
  for d in "$ROOT"/jobs/*/; do [ -d "$d" ] && targets+=("$d"); done
fi

if [ "${#targets[@]}" -eq 0 ]; then
  echo "usage: clean-job.sh [--dry-run] [--force] <job-dir>... | --all" >&2
  exit 1
fi

freed=0
clean_one() {
  local dir="${1%/}"
  [ -d "$dir" ] || { echo "MISSING: $dir" >&2; return 0; }
  local name finals keep_mp4 keep_png
  name="$(basename "$dir")"
  finals="$dir/output/finals"
  keep_mp4="$finals/$name.mp4"
  keep_png="$finals/$name.png"

  if [ ! -f "$keep_mp4" ] && [ "$FORCE" -eq 0 ]; then
    echo "SKIP (no canonical final): $name"
    return 0
  fi

  # Bytes that will be removed = everything except the kept deliverables.
  local before kept
  before=$(find "$dir" -type f -print0 2>/dev/null | xargs -0 stat -f '%z' 2>/dev/null | awk '{s+=$1} END{print s+0}')
  kept=0
  [ -f "$keep_mp4" ] && kept=$((kept + $(stat -f '%z' "$keep_mp4")))
  [ -f "$keep_png" ] && kept=$((kept + $(stat -f '%z' "$keep_png")))
  local delta=$((before - kept))
  freed=$((freed + delta))

  if [ "$DRY" -eq 1 ]; then
    printf 'WOULD CLEAN %-46s -%s\n' "$name" "$(bytes_h $delta)"
    return 0
  fi

  # Delete every file that is not a kept deliverable, then prune empty dirs.
  find "$dir" -type f ! -path "$keep_mp4" ! -path "$keep_png" -delete
  find "$dir" -depth -type d -empty -delete 2>/dev/null || true
  printf 'CLEANED %-46s -%s\n' "$name" "$(bytes_h $delta)"
}

bytes_h() { awk -v b="$1" 'BEGIN{ split("B KB MB GB TB",u); i=1; while(b>=1024 && i<5){b/=1024;i++} printf "%.1f%s", b, u[i] }'; }

for t in "${targets[@]}"; do clean_one "$t"; done
echo "----"
echo "Total $([ "$DRY" -eq 1 ] && echo would-free || echo freed): $(bytes_h $freed)"
