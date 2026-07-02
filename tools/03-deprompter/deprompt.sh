#!/usr/bin/env bash
#
# Tool 03 — De-prompter.  Repeat-after footage in → clean talent-only clip out.
#
# Shooting style this fixes: an off-camera person reads each line out loud
# (prompter), their voice bleeds into the camera mic, and the on-camera talent
# repeats the line. Raw audio = prompter + talent alternating. This tool keeps
# ONLY the talent (audio + video) and drops every prompter segment.
#
# How it decides who the talent is (gender-agnostic, no hard-coded voice):
#   ElevenLabs Scribe v2 diarization (diarize=true, num_speakers=N) → per-word
#   speaker_id. Talent = the speaker who, across adjacent A→B pairs, speaks
#   SECOND (the repeater) most often AND holds the most airtime.
#
# Confidence guard: if only ONE speaker is detected but the transcript has
# repeated phrases (two voices too similar to split — e.g. same gender), it
# REFUSES to auto-cut and exits 2 with guidance. It never guesses.
#
# Joins between kept takes (see docs / README "why hard cut, not dissolve"):
#   DEFAULT = HARD CUT + continuous audio + alternating PUNCH-IN. Repeat-after
#   takes differ a lot in pose; a dissolve would alpha-blend two poses into a
#   ghost ("ลายตา"). Hard cut + a 12% alternating punch makes each join read as a
#   deliberate angle change. Gold standard on top: cover the biggest joins with
#   B-roll/captions when this feeds v88.
#
# Usage:
#   bash tools/03-deprompter/deprompt.sh <raw.mp4> [slug] \
#        [--punch <n> | --no-punch] [--talent <speaker_id>] \
#        [--num-speakers <n>] [--lang tha] [--date YYYY-MM-DD] [--fresh]
#
# Examples:
#   bash tools/03-deprompter/deprompt.sh raw-media/talk.mp4
#   bash tools/03-deprompter/deprompt.sh raw-media/talk.mp4 bank-ai --punch 0.15
#   bash tools/03-deprompter/deprompt.sh raw-media/talk.mp4 --no-punch   # plain hard cut
#
# Output (staging/deprompter/<DATE>-<SLUG>/):
#   talent-only.mp4   — the clean clip (deliverable; feed straight into v88)
#   edl.json          — kept talent segments (v88 keep-EDL format)
#   report.json       — diarization breakdown + decision + join style
#   diarization.json  — raw Scribe response (cached; re-runs skip the API)
#
# Exit codes: 0 done · 2 AMBIGUOUS (same-gender — see report) · 1 error
#
# Requirements: bash, ffmpeg, ffprobe, python3, and templates/_shared/env/.env
# with ELEVENLABS_API_KEY.

set -e

# ── Parse args ───────────────────────────────────────────────
PUNCH="0.12"          # recommended default: fake-second-camera on every other take
TALENT=""
NUM_SPK="2"
LANG="tha"
DATE=$(date +%Y-%m-%d)
FRESH=0
POSITIONAL=()

while [ $# -gt 0 ]; do
  case "$1" in
    --punch)        PUNCH="$2"; shift 2 ;;
    --no-punch)     PUNCH="0"; shift ;;
    --talent)       TALENT="$2"; shift 2 ;;
    --num-speakers) NUM_SPK="$2"; shift 2 ;;
    --lang)         LANG="$2"; shift 2 ;;
    --date)         DATE="$2"; shift 2 ;;
    --fresh)        FRESH=1; shift ;;   # ignore cached diarization, call the API again
    -h|--help)      sed -n '2,46p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)              POSITIONAL+=("$1"); shift ;;
  esac
done

if [ ${#POSITIONAL[@]} -lt 1 ]; then
  echo "Usage: bash tools/03-deprompter/deprompt.sh <raw.mp4> [slug] [--punch <n>|--no-punch] [--talent <id>]" >&2
  exit 1
fi

INPUT=${POSITIONAL[0]}
SLUG=${POSITIONAL[1]:-}
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPROMPTER_PY="$(dirname "${BASH_SOURCE[0]}")/deprompter.py"
ENV_FILE="$REPO_ROOT/templates/_shared/env/.env"

if [ ! -f "$INPUT" ]; then
  echo "✗ Input video not found: $INPUT" >&2
  exit 1
fi
INPUT_ABS="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"

# Default slug from filename (ascii-kebab)
if [ -z "$SLUG" ]; then
  SLUG=$(basename "$INPUT" | sed 's/\.[^.]*$//' | tr '[:upper:] _' '[:lower:]--' \
         | tr -cd 'a-z0-9-' | sed 's/-\{2,\}/-/g; s/^-//; s/-$//')
  [ -z "$SLUG" ] && SLUG="clip"
fi

STAGE_DIR="$REPO_ROOT/staging/deprompter/${DATE}-${SLUG}"
mkdir -p "$STAGE_DIR"
OUT="$STAGE_DIR/talent-only.mp4"
EDL="$STAGE_DIR/edl.json"
REPORT="$STAGE_DIR/report.json"
DIAR="$STAGE_DIR/diarization.json"

JOIN="hard cut + continuous audio"
[ "$PUNCH" != "0" ] && JOIN="$JOIN + punch-in ${PUNCH}"

echo "═══ Tool 03 — De-prompter: ${DATE}-${SLUG} ═══"
echo "    source:  $INPUT_ABS"
echo "    staging: ${STAGE_DIR#$REPO_ROOT/}/"
echo "    joins:   $JOIN"
echo ""

# ── Env (ElevenLabs) ─────────────────────────────────────────
[ -f "$ENV_FILE" ] || { echo "✗ Missing .env: $ENV_FILE" >&2; exit 1; }
set -a; source "$ENV_FILE"; set +a
[ -n "${ELEVENLABS_API_KEY:-}" ] || { echo "✗ ELEVENLABS_API_KEY empty in $ENV_FILE" >&2; exit 1; }

# ── Run de-prompter ──────────────────────────────────────────
ARGS=( "$INPUT_ABS" --lang "$LANG" --num-speakers "$NUM_SPK"
       --out-edl "$EDL" --report "$REPORT" --apply "$OUT"
       --xfade 0 --punch "$PUNCH" )
[ -n "$TALENT" ] && ARGS+=( --talent "$TALENT" )

# Cache the diarization: reuse it on re-runs unless --fresh (saves API cost).
if [ -f "$DIAR" ] && [ "$FRESH" -eq 0 ]; then
  echo "─── Diarization: reusing cached $DIAR (use --fresh to re-call API)"
  ARGS+=( --diar-json "$DIAR" )
else
  echo "─── Diarization: ElevenLabs Scribe v2 (diarize, num_speakers=$NUM_SPK)"
  ARGS+=( --save-diar "$DIAR" )
fi

set +e
python3 "$DEPROMPTER_PY" "${ARGS[@]}"
RC=$?
set -e

echo ""
if [ "$RC" -eq 2 ]; then
  echo "⚠ AMBIGUOUS — could not separate the two voices (likely same gender)."
  echo "  Nothing was cut. See $REPORT for the warning + options"
  echo "  (voice reference / lip-sync / cut by hand)."
  exit 2
elif [ "$RC" -ne 0 ]; then
  echo "✗ De-prompter failed (exit $RC)." >&2
  exit "$RC"
fi

echo "✓ Done"
echo "    deliverable: ${OUT#$REPO_ROOT/}"
echo "    keep-EDL:    ${EDL#$REPO_ROOT/}"
echo "    report:      ${REPORT#$REPO_ROOT/}"
