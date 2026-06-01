#!/usr/bin/env bash
#
# Longform Shorts — Phase 1 (prep).
#
# Takes a long source video (5-60 min) and prepares the inputs that the
# Shorts Finder subagent (SUBAGENT_PROMPTS.md Section C) needs to pick
# short-form moments out of it.
#
# Outputs to:  staging/longform/<DATE>-<SLUG>/
#   source.mp4              — symlink to the input
#   duration.txt            — ffprobe seconds (float)
#   silence.json            — ffmpeg silencedetect points (>= 0.8s gaps)
#   raw-elevenlabs.json     — ElevenLabs Scribe v2 transcript (full source)
#   meta.json               — slug, date, topic, paths
#   PROMPT.md               — ready-to-paste Shorts Finder prompt with slots filled
#
# Phase 2 (after the subagent writes shorts.json) is `tools/01-longform-shorts/split.sh`.
#
# Usage:
#   bash tools/01-longform-shorts/prep.sh <input.mp4> <slug> [--topic "<one sentence>"] [--date YYYY-MM-DD]
#
# Example:
#   bash tools/01-longform-shorts/prep.sh raw-media/2026-05-25-podcast-ep03/source.mp4 podcast-ep03 \
#     --topic "พี่แบงค์เล่าเรื่องการลงทุน 20 ปีและความผิดพลาดในช่วงโควิด"
#
# Requirements: bash, ffmpeg, ffprobe, python3, node, the .env file
# (templates/_shared/env/.env with ELEVENLABS_API_KEY).

set -e

# --- Parse args ---
INPUT=""
SLUG=""
TOPIC=""
DATE=$(date +%Y-%m-%d)
POSITIONAL=()

while [ $# -gt 0 ]; do
  case "$1" in
    --topic) TOPIC="$2"; shift 2 ;;
    --date) DATE="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

if [ ${#POSITIONAL[@]} -lt 2 ]; then
  echo "Usage: bash tools/01-longform-shorts/prep.sh <input.mp4> <slug> [--topic '<one sentence>'] [--date YYYY-MM-DD]" >&2
  exit 1
fi

INPUT=${POSITIONAL[0]}
SLUG=${POSITIONAL[1]}
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ ! -f "$INPUT" ]; then
  echo "✗ Input video not found: $INPUT" >&2
  exit 1
fi

INPUT_ABS="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
STAGE_DIR="$REPO_ROOT/staging/longform/${DATE}-${SLUG}"

if [ -d "$STAGE_DIR" ]; then
  echo "✗ Staging already exists: $STAGE_DIR" >&2
  echo "  Remove it or pick a different --slug/--date." >&2
  exit 1
fi

mkdir -p "$STAGE_DIR"

echo "→ Staging dir: $STAGE_DIR"
echo "→ Source video: $INPUT_ABS"

# --- Step 1: stream-copy source to a clean ASCII path (drops metadata).
#     A symlink to a Thai-filename source can break downstream tools whose
#     subprocess wrappers assume UTF-8 stderr — observed: ffprobe inside
#     transcribe.py's count_audio_tracks() raised UnicodeDecodeError when the
#     file embedded Thai metadata. Stream-copy is ~5-10s even for 200 MB and
#     normalises the path completely.
echo "→ Copying source (stream-copy, no re-encode, ~5-10s)..."
ffmpeg -hide_banner -loglevel error -nostdin -y \
  -i "$INPUT_ABS" \
  -c copy -map_metadata -1 -movflags +faststart \
  "$STAGE_DIR/source.mp4"

# --- Step 2: duration via ffprobe (use the clean copy) ---
SOURCE_CLEAN="$STAGE_DIR/source.mp4"
DURATION=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$SOURCE_CLEAN")
echo "$DURATION" > "$STAGE_DIR/duration.txt"
echo "→ Duration: ${DURATION}s"

# Sanity: refuse anything shorter than 3 minutes — too short for shorts splitting
DUR_INT=$(printf '%.0f' "$DURATION")
if [ "$DUR_INT" -lt 180 ]; then
  echo "✗ Source is ${DUR_INT}s — too short for longform splitting." >&2
  echo "  Use tools/new-job.sh for normal single-clip workflow instead." >&2
  rm -rf "$STAGE_DIR"
  exit 1
fi

# --- Step 3: silence detect (gaps >= 0.8s, noise floor -30dB) ---
echo "→ Detecting silence points (this takes ~30s for a 20-min clip)..."
SILENCE_LOG="$STAGE_DIR/silence.log"
ffmpeg -hide_banner -nostats -i "$SOURCE_CLEAN" \
  -af "silencedetect=noise=-30dB:d=0.8" -f null - 2> "$SILENCE_LOG" || true

# Parse silencedetect output into JSON
python3 - "$SILENCE_LOG" "$STAGE_DIR/silence.json" <<'PY'
import re, json, sys
log_path, out_path = sys.argv[1], sys.argv[2]
starts, ends = [], []
with open(log_path, encoding="utf-8", errors="ignore") as f:
    for line in f:
        m = re.search(r"silence_start:\s*([\d.]+)", line)
        if m: starts.append(float(m.group(1)))
        m = re.search(r"silence_end:\s*([\d.]+)", line)
        if m: ends.append(float(m.group(1)))
points = []
for s, e in zip(starts, ends):
    points.append({"start": round(s, 3), "end": round(e, 3), "gap": round(e - s, 3)})
with open(out_path, "w") as f:
    json.dump({"noise_db": -30, "min_gap": 0.8, "points": points}, f, indent=2)
print(f"   {len(points)} silence points written")
PY
rm -f "$SILENCE_LOG"

# --- Step 4: ElevenLabs transcription ---
ENV_FILE="$REPO_ROOT/templates/_shared/env/.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "✗ Missing .env: $ENV_FILE" >&2
  echo "  Copy from .env.example and add ELEVENLABS_API_KEY." >&2
  exit 1
fi

# Source .env to get the key
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

if [ -z "${ELEVENLABS_API_KEY:-}" ]; then
  echo "✗ ELEVENLABS_API_KEY is empty in $ENV_FILE" >&2
  exit 1
fi

echo "→ Transcribing with ElevenLabs Scribe v2 (cost ~\$0.024 per 100s)..."
SCRIBE_PY="$REPO_ROOT/templates/_shared/scripts/transcribe/transcribe.py"

# Call the python script directly (npm wrapper swallows args per memory note)
export SSL_CERT_FILE="$(python3 -c 'import certifi; print(certifi.where())')"
python3 "$SCRIBE_PY" "$SOURCE_CLEAN" \
  --provider elevenlabs --lang th \
  --save-all "$STAGE_DIR/" \
  --words-per-group 2

# Patch null duration in raw-elevenlabs.json with ffprobe value
python3 - "$STAGE_DIR/raw-elevenlabs.json" "$DURATION" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
if d.get("duration") in (None, 0):
    d["duration"] = float(sys.argv[2])
    json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)
    print(f"   patched duration → {d['duration']}s")
PY

# --- Step 5: meta.json ---
cat > "$STAGE_DIR/meta.json" <<EOF
{
  "slug": "${SLUG}",
  "date": "${DATE}",
  "source_original": "${INPUT_ABS}",
  "source": "${SOURCE_CLEAN}",
  "duration": ${DURATION},
  "topic": $(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "${TOPIC:-}"),
  "phase": "prepped",
  "next": "Run the Shorts Finder subagent (SUBAGENT_PROMPTS.md Section C), then bash tools/01-longform-shorts/split.sh ${STAGE_DIR#$REPO_ROOT/}"
}
EOF

# --- Step 6: pre-rendered prompt ---
TOPIC_OUT="${TOPIC:-<one sentence describing what the long video is about>}"
cat > "$STAGE_DIR/PROMPT.md" <<EOF
# Shorts Finder — ready-to-paste prompt

Spawn a Claude subagent (Task tool, general-purpose) with the prompt from:
  \`templates/_shared/docs/SUBAGENT_PROMPTS.md\` → Section D

Fill the slots with these values:

- ABS_PATH_RAW_JSON: \`${STAGE_DIR}/raw-elevenlabs.json\`
- ABS_PATH_SILENCE_JSON: \`${STAGE_DIR}/silence.json\`
- ABS_PATH_SOURCE_MP4: \`${STAGE_DIR}/source.mp4\`
- DURATION_SECONDS: \`${DURATION}\`
- TOPIC: \`${TOPIC_OUT}\`
- ABS_PATH_SHORTS_JSON (output): \`${STAGE_DIR}/shorts.json\`

After the subagent writes \`shorts.json\`, run Phase 2:

\`\`\`bash
bash tools/01-longform-shorts/split.sh "${STAGE_DIR#$REPO_ROOT/}"
\`\`\`
EOF

echo ""
echo "✓ Phase 1 complete."
echo ""
echo "  Staging:   ${STAGE_DIR#$REPO_ROOT/}/"
echo "  Source:    ${DURATION}s"
echo "  Silence:   $(python3 -c "import json; print(len(json.load(open('$STAGE_DIR/silence.json'))['points']))") gaps"
echo "  Transcript: raw-elevenlabs.json"
echo ""
echo "Next step (in Claude Code):"
echo "  → Read ${STAGE_DIR#$REPO_ROOT/}/PROMPT.md"
echo "  → Spawn Shorts Finder subagent (SUBAGENT_PROMPTS.md Section C)"
echo "  → Or just say to Claude: 'run shorts finder on ${STAGE_DIR#$REPO_ROOT/}'"
echo "  → When shorts.json exists, run:"
echo "      bash tools/01-longform-shorts/split.sh ${STAGE_DIR#$REPO_ROOT/}"
