#!/usr/bin/env bash
#
# Longform Shorts — Phase 2 (split).
#
# Reads shorts.json produced by the Shorts Finder subagent
# (SUBAGENT_PROMPTS.md Section C) and scaffolds one child job per short.
# Each child job gets:
#   - input/bottom.mp4         — sliced from staging/source.mp4
#   - input/top.mp4            — sliced from staging/source-top.mp4 if present
#   - intermediates/raw-elevenlabs.json  — sliced + rebased transcript
#                                          (so v88 Step 2 can be skipped)
#   - job-spec.json            — Template Manager-style spec (template-hint honoured)
#   - manifest.json            — written by new-job.sh
#
# Usage:
#   bash tools/01-longform-shorts/split.sh <staging-dir> [--template NN] [--max N]
#                                              [--ranks 1,3,5]
#                                              [--dry-run]
#
# Examples:
#   # Default — every short the subagent emitted, template per-short hint
#   bash tools/01-longform-shorts/split.sh staging/longform/2026-05-25-podcast-ep03
#
#   # Force template 04 for every short
#   bash tools/01-longform-shorts/split.sh staging/longform/2026-05-25-podcast-ep03 --template 04
#
#   # Only the top 3 ranked shorts
#   bash tools/01-longform-shorts/split.sh staging/longform/2026-05-25-podcast-ep03 --max 3
#
#   # Only specific ranks
#   bash tools/01-longform-shorts/split.sh staging/longform/2026-05-25-podcast-ep03 --ranks 1,2,5
#
# Requirements: bash, ffmpeg, python3, tools/new-job.sh

set -e

# --- Parse args ---
STAGE_DIR_ARG=""
TEMPLATE_OVERRIDE=""
MAX_N=""
RANKS=""
DRY_RUN=0
POSITIONAL=()

while [ $# -gt 0 ]; do
  case "$1" in
    --template) TEMPLATE_OVERRIDE="$2"; shift 2 ;;
    --max) MAX_N="$2"; shift 2 ;;
    --ranks) RANKS="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      sed -n '2,32p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

if [ ${#POSITIONAL[@]} -lt 1 ]; then
  echo "Usage: bash tools/01-longform-shorts/split.sh <staging-dir> [--template NN] [--max N] [--ranks 1,3,5] [--dry-run]" >&2
  exit 1
fi

STAGE_DIR_ARG=${POSITIONAL[0]}
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Resolve staging dir (accept absolute or repo-relative)
if [[ "$STAGE_DIR_ARG" = /* ]]; then
  STAGE_DIR="$STAGE_DIR_ARG"
else
  STAGE_DIR="$REPO_ROOT/$STAGE_DIR_ARG"
fi
STAGE_DIR="$(cd "$STAGE_DIR" && pwd)"

# --- Validate staging contents ---
for f in shorts.json source.mp4 raw-elevenlabs.json meta.json; do
  if [ ! -e "$STAGE_DIR/$f" ]; then
    echo "✗ Missing in staging: $f" >&2
    if [ "$f" = "shorts.json" ]; then
      echo "  → Run the Shorts Finder subagent first (SUBAGENT_PROMPTS.md Section C)" >&2
      echo "  → See $STAGE_DIR/PROMPT.md" >&2
    fi
    exit 1
  fi
done

SLUG=$(python3 -c "import json; print(json.load(open('$STAGE_DIR/meta.json'))['slug'])")
DATE=$(python3 -c "import json; print(json.load(open('$STAGE_DIR/meta.json'))['date'])")

# Optional top track (for stacked T01/T05)
TOP_SRC=""
if [ -f "$STAGE_DIR/source-top.mp4" ]; then
  TOP_SRC="$STAGE_DIR/source-top.mp4"
  echo "→ Stacked source detected: source-top.mp4 + source.mp4 (bottom)"
else
  echo "→ Single-camera source (no source-top.mp4)"
fi

# --- Iterate shorts.json ---
echo ""
echo "→ Reading $STAGE_DIR/shorts.json"

# Build a TSV the bash loop can consume safely
SHORTS_TSV=$(python3 - "$STAGE_DIR/shorts.json" "${TEMPLATE_OVERRIDE}" "${MAX_N}" "${RANKS}" <<'PY'
import json, sys
shorts = json.load(open(sys.argv[1]))["shorts"]
override = sys.argv[2].strip()
max_n = sys.argv[3].strip()
ranks_filter = sys.argv[4].strip()

if ranks_filter:
    wanted = {int(x) for x in ranks_filter.split(",") if x.strip()}
    shorts = [s for s in shorts if s.get("rank") in wanted]

if max_n:
    shorts = sorted(shorts, key=lambda s: -s.get("scores", {}).get("overall", 0))
    shorts = shorts[: int(max_n)]
    shorts.sort(key=lambda s: s.get("start_ms", 0))

for s in shorts:
    rank = s.get("rank", "?")
    start_ms = int(s["start_ms"])
    end_ms = int(s["end_ms"])
    dur = round((end_ms - start_ms) / 1000.0, 2)
    hint = (s.get("template_hint") or "any").strip()
    if override:
        tmpl = override
    elif hint and hint != "any":
        tmpl = hint
    else:
        tmpl = "05"  # project default per user choice
    title = s.get("title_th", "")
    overall = s.get("scores", {}).get("overall", 0)
    # tab-separated; titles never carry tabs in practice
    print(f"{rank}\t{start_ms}\t{end_ms}\t{dur}\t{tmpl}\t{overall}\t{title}")
PY
)

if [ -z "$SHORTS_TSV" ]; then
  echo "✗ No shorts to process (after filters)." >&2
  exit 1
fi

COUNT=$(printf "%s\n" "$SHORTS_TSV" | wc -l | tr -d ' ')
echo "→ $COUNT shorts to scaffold"
echo ""

# Pad rank to 2 digits for slug
CHILD_SLUGS=()
while IFS=$'\t' read -r RANK START_MS END_MS DUR TMPL OVERALL TITLE; do
  RANK_PAD=$(printf "%02d" "$RANK")
  CHILD_SLUG="${SLUG}-clip${RANK_PAD}"
  JOB_NAME="${DATE}-${CHILD_SLUG}"
  JOB_DIR="$REPO_ROOT/jobs/$JOB_NAME"

  echo "─── rank=$RANK  duration=${DUR}s  template=T${TMPL}  score=${OVERALL}"
  echo "    title: $TITLE"
  echo "    slug:  $CHILD_SLUG"

  if [ "$DRY_RUN" = "1" ]; then
    echo "    (dry-run — not creating)"
    continue
  fi

  if [ -d "$JOB_DIR" ]; then
    echo "    ⚠ already exists, skipping: $JOB_DIR"
    continue
  fi

  # 1. Scaffold the empty job via new-job.sh
  bash "$REPO_ROOT/tools/new-job.sh" "$TMPL" "$CHILD_SLUG" --date "$DATE" >/dev/null

  # 1b. Resolve full template id (e.g. "04" → "04-fullscreen-vertical-karaoke")
  TEMPLATE_FULL=$(basename "$(find "$REPO_ROOT/templates" -maxdepth 1 -type d -name "${TMPL}-*" | head -1)")

  # 2. Slice the bottom video — force 30 fps + 30 GOP so v88 render is happy
  #    -nostdin: critical — otherwise ffmpeg eats remaining TSV from the
  #    while-read heredoc and breaks subsequent iterations.
  #    -r 30 + -g 30: v88 (hyperframes) expects 30 fps with dense keyframes;
  #    YouTube/podcast sources are often 25/50/60 fps with sparse keyframes.
  START_S=$(python3 -c "print($START_MS / 1000)")
  DURATION_S=$(python3 -c "print(($END_MS - $START_MS) / 1000)")
  ffmpeg -hide_banner -loglevel error -nostdin -y \
    -ss "$START_S" -i "$STAGE_DIR/source.mp4" \
    -t "$DURATION_S" \
    -r 30 -c:v libx264 -preset veryfast -crf 18 \
    -g 30 -keyint_min 30 -movflags +faststart \
    -c:a aac -b:a 192k -ar 48000 \
    -avoid_negative_ts make_zero \
    "$JOB_DIR/input/bottom.mp4"

  # 3. Slice the top video if available (same 30 fps normalization)
  if [ -n "$TOP_SRC" ]; then
    ffmpeg -hide_banner -loglevel error -nostdin -y \
      -ss "$START_S" -i "$TOP_SRC" \
      -t "$DURATION_S" \
      -r 30 -c:v libx264 -preset veryfast -crf 18 \
      -g 30 -keyint_min 30 -movflags +faststart \
      -c:a aac -b:a 192k -ar 48000 \
      -avoid_negative_ts make_zero \
      "$JOB_DIR/input/top.mp4"
  fi

  # 3b. Copy template's default bg.png so the v88 composition can find it.
  #     T04/T02 (single-cam) use it as a fallback; T01/T05 use it visibly.
  TEMPLATE_BG="$REPO_ROOT/templates/$TEMPLATE_FULL/assets/bg.png"
  if [ -f "$TEMPLATE_BG" ]; then
    cp "$TEMPLATE_BG" "$JOB_DIR/input/bg.png"
  fi

  # 4. Slice transcript (skips Step 2 of v88 — saves ~$0.024 per short)
  python3 "$REPO_ROOT/tools/01-longform-shorts/slice-transcript.py" \
    --in "$STAGE_DIR/raw-elevenlabs.json" \
    --out "$JOB_DIR/intermediates/raw-elevenlabs.json" \
    --start-ms "$START_MS" \
    --end-ms "$END_MS"

  # 5. Write Job Spec (canonical bizdrive-job-spec schema — see JOB_SPEC.md)
  python3 - "$JOB_DIR" "$TEMPLATE_FULL" "$TITLE" "$RANK" "$STAGE_DIR" "$START_MS" "$END_MS" "$OVERALL" <<'PY'
import json, sys
from pathlib import Path
job_dir, template_full, title, rank, stage, start_ms, end_ms, overall = sys.argv[1:9]
spec = {
    "spec": "bizdrive-job-spec",
    "version": 1,
    "template": template_full,
    "topic": title,
    "features": {
        "dead_air_cut": {"on": True},
        "audio_polish": {"on": True},
        "captions":     {"on": True},
        "broll":        {"on": False, "mode": "ai-gen", "max": 4},
        "bgm":          {"on": True, "gain": 5},
        "sfx":          {"on": False},
        "thumbnail":    {"on": True, "main": title, "hero": "", "sub": ""}
    },
    "inputs": {
        "transcript_provided": "intermediates/raw-elevenlabs.json",
        "note": "Sliced from longform parent — skip V88 Step 2 (transcribe). Editorial subagent (Step 3) still runs on this slice."
    },
    "longform_source": {
        "staging": str(stage),
        "rank": int(rank),
        "start_ms": int(start_ms),
        "end_ms": int(end_ms),
        "score_overall": float(overall)
    },
    "notes": f"Auto-generated by tools/01-longform-shorts/split.sh — rank #{rank} of longform source."
}
Path(f"{job_dir}/job-spec.json").write_text(
    json.dumps(spec, ensure_ascii=False, indent=2)
)
PY

  CHILD_SLUGS+=("$JOB_NAME")
  echo "    ✓ jobs/$JOB_NAME/"
  echo ""
done <<< "$SHORTS_TSV"

if [ "$DRY_RUN" = "1" ]; then
  echo "(dry-run — nothing created)"
  exit 0
fi

echo ""
echo "✓ Phase 2 complete. ${#CHILD_SLUGS[@]} child jobs scaffolded:"
for j in "${CHILD_SLUGS[@]}"; do
  echo "    jobs/$j/"
done
echo ""
echo "Next:"
echo "  For each child job, follow V88_PLAYBOOK.md — but SKIP Step 2"
echo "  (transcribe is already done; see intermediates/raw-elevenlabs.json)."
echo "  The Job Spec is at jobs/<...>/job-spec.json."
