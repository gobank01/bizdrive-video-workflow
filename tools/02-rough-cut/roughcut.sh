#!/usr/bin/env bash
#
# Tool 02 — Rough Cut.  Raw recording in → one finished, watchable rough cut out.
#
# "Rough cut" here = condense, not just clean (see docs/adr/0002 + CONTEXT.md):
#   1. Invisible cuts — retakes, false starts, fillers, stumbles, dead air
#   2. Water cuts     — rambling / over-explanation / tangents, judged vs Context
#   3. Content cuts   — whole good points dropped, ONLY when --target is set
# Then a Silero VAD jump-cut tightens micro-pauses, and the audio is leveled
# (loudnorm) so the result is listenable. NO captions / template / B-roll /
# thumbnail / aspect reframe — it keeps the source's aspect ratio and fps.
#
# This is the SINGLE terminal deliverable of Tool 02. It does NOT scaffold a
# job / workspace / template — it calls templates/_shared/scripts/clean-cut/*.py
# directly (docs/adr/0001).
#
# Resumable: the script auto-detects the next phase from file presence and
# exits 100 at the one Editorial subagent pause. Re-run the SAME command after
# spawning the subagent.
#
# Usage:
#   bash tools/02-rough-cut/roughcut.sh <raw.mp4> [slug] \
#        [--target <sec>] [--context "what this clip should say / what must survive"] \
#        [--date YYYY-MM-DD]
#
# Examples:
#   bash tools/02-rough-cut/roughcut.sh raw-media/talk.mp4 my-talk \
#     --context "พี่แบงค์อธิบายว่าทำไมคนทำธุรกิจต้องเริ่มลงมือก่อนพร้อม"
#   bash tools/02-rough-cut/roughcut.sh raw-media/talk.mp4 my-talk --target 100
#
# Output (staging/roughcut/<DATE>-<SLUG>/):
#   rough-cut.mp4   — the finished rough cut (deliverable)
#   edl.json        — the kept-segment list (for re-apply / feeding v88)
#
# Exit codes: 0 done · 100 paused for Editorial subagent · 1 error
#
# Requirements: bash, ffmpeg, ffprobe, python3, the VAD env at
# ~/.ii23/vad-env, and templates/_shared/env/.env with ELEVENLABS_API_KEY.

set -e

# ── Parse args ───────────────────────────────────────────────
TARGET=""
CONTEXT=""
DATE=$(date +%Y-%m-%d)
POSITIONAL=()

while [ $# -gt 0 ]; do
  case "$1" in
    --target)  TARGET="$2"; shift 2 ;;
    --context|--topic) CONTEXT="$2"; shift 2 ;;
    --date)    DATE="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,38p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

if [ ${#POSITIONAL[@]} -lt 1 ]; then
  echo "Usage: bash tools/02-rough-cut/roughcut.sh <raw.mp4> [slug] [--target <sec>] [--context \"...\"]" >&2
  exit 1
fi

INPUT=${POSITIONAL[0]}
SLUG=${POSITIONAL[1]:-}
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CC="$REPO_ROOT/templates/_shared/scripts/clean-cut"
TRANSCRIBE_PY="$REPO_ROOT/templates/_shared/scripts/transcribe/transcribe.py"
ENV_FILE="$REPO_ROOT/templates/_shared/env/.env"
VAD_PY="$HOME/.ii23/vad-env/bin/python3"
RULES="$CC/references/editorial-rules.md"

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

STAGE_DIR="$REPO_ROOT/staging/roughcut/${DATE}-${SLUG}"
mkdir -p "$STAGE_DIR"
SRC="$STAGE_DIR/source.mp4"

echo "═══ Tool 02 — Rough Cut: ${DATE}-${SLUG} ═══"
echo "    source:  $INPUT_ABS"
echo "    staging: ${STAGE_DIR#$REPO_ROOT/}/"
[ -n "$TARGET" ] && echo "    target:  ${TARGET}s (Target Mode — content cuts allowed)" \
                 || echo "    mode:    Clean (condense, no content cuts)"
echo ""

# ── Step 1 — clean copy + duration ───────────────────────────
if [ ! -f "$SRC" ]; then
  echo "─── Step 1 — clean-copy source (stream-copy, drops Thai metadata)"
  ffmpeg -hide_banner -loglevel error -nostdin -y \
    -i "$INPUT_ABS" -c copy -map_metadata -1 -movflags +faststart "$SRC"
fi
DURATION=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$SRC")
echo "$DURATION" > "$STAGE_DIR/duration.txt"
DUR_INT=$(printf '%.0f' "$DURATION")
if [ "$DUR_INT" -lt 1 ]; then echo "✗ Zero-duration source." >&2; exit 1; fi
echo "    ✓ ${DURATION}s"

# ── Step 2 — transcribe (ElevenLabs Scribe v2, always) ───────
if [ ! -f "$STAGE_DIR/raw-elevenlabs.json" ]; then
  echo "─── Step 2 — transcribe (ElevenLabs Scribe v2)"
  [ -f "$ENV_FILE" ] || { echo "✗ Missing .env: $ENV_FILE" >&2; exit 1; }
  set -a; source "$ENV_FILE"; set +a
  [ -n "${ELEVENLABS_API_KEY:-}" ] || { echo "✗ ELEVENLABS_API_KEY empty" >&2; exit 1; }
  export SSL_CERT_FILE="$(python3 -c 'import certifi; print(certifi.where())')"
  python3 "$TRANSCRIBE_PY" "$SRC" \
    --provider elevenlabs --lang th \
    --save-all "$STAGE_DIR/" --words-per-group 2
  # drop zero-duration boundary artifacts + patch duration
  python3 - "$STAGE_DIR/raw-elevenlabs.json" "$DURATION" <<'PY'
import json, sys
p, dur = sys.argv[1], float(sys.argv[2])
d = json.load(open(p))
before = len(d.get("words", []))
d["words"] = [w for w in d.get("words", []) if (w["end"] - w["start"]) >= 0.05]
d["text"] = " ".join(w.get("text", "") for w in d["words"]).strip()
d["duration"] = dur
json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)
print(f"    ✓ {len(d['words'])} words (dropped {before-len(d['words'])} artifacts)")
PY
fi

# ── Step 3 — Editorial subagent (the one pause) ──────────────
if [ ! -f "$STAGE_DIR/edl-rough.json" ]; then
  PROMPT_FILE="$STAGE_DIR/editorial-prompt.txt"
  if [ -n "$TARGET" ]; then
    TARGET_LINE="A target length IS set: ${TARGET} seconds. After invisible + water cuts, if the result is still longer than ${TARGET}s, make CONTENT CUTS — drop whole lowest-value points — until segments total roughly ${TARGET}s (±10%). List every dropped point in \"content_cuts\"."
  else
    TARGET_LINE="No target length is set. Make invisible + water cuts ONLY (do NOT drop whole good points). In \"suggestions\", list the points that COULD be dropped to go shorter, so the user can decide."
  fi
  if [ -n "$CONTEXT" ]; then
    CONTEXT_LINE="Context (what this clip should say / what must survive): ${CONTEXT}"
  else
    CONTEXT_LINE="Context: NOT PROVIDED. First infer, from the transcript, what point this clip is making and what must survive — state it in \"context_used\" — then cut against it."
  fi
  cat > "$PROMPT_FILE" <<EOF
You are producing a ROUGH CUT of a raw Thai recording. This is condensing, like
making a tight summary — not just cleaning. Read the rules, then emit an EDL.

## Inputs
- Transcript (ElevenLabs Scribe v2, word timings): $STAGE_DIR/raw-elevenlabs.json
- Source media: $SRC
- Original duration: ${DURATION}s
- ${CONTEXT_LINE}
- ${TARGET_LINE}
- Output EDL: $STAGE_DIR/edl-rough.json

## Read FIRST
$RULES
(Apply last-take-wins, false starts, fillers, mid-sentence stumbles, dead air,
final-20% scrutiny. Thai particles ครับ/นะ/ค่ะ and natural conjunctions are KEPT.)

## Cut in three layers
1. INVISIBLE — spoiled material (retakes / false starts / fillers / stumbles /
   dead air). Always.
2. WATER — rambling, over-explanation, repeated examples, tangents: the point
   survives, only the padding goes. Cut whatever does not serve the Context.
   Always (this is the condense step).
3. CONTENT — whole good points dropped to hit a target. ONLY per the target line
   above.

## Guardrail — do NOT over-cut
Never cut so much that a surviving point becomes unintelligible or loses its
setup/payoff. Keep the through-line coherent end to end. When unsure whether
something is water or substance, KEEP it.

## Hard requirements
1. Every segment uses real timings from raw-elevenlabs.json words[] — invent nothing.
2. start_ms / end_ms are integers (ms), chronological, non-overlapping.
3. Pad head ~200ms, tail ~100ms; never bleed into a dropped next word.
4. Output strict JSON to $STAGE_DIR/edl-rough.json:

\`\`\`json
{
  "segments": [{"start_ms": int, "end_ms": int}],
  "language": "th",
  "context_used": "supplied or inferred context, one sentence",
  "original_seconds": ${DURATION},
  "natural_seconds": float,
  "kept_seconds": float,
  "content_cuts": ["points dropped to hit target, or empty"],
  "suggestions": ["points that could be dropped to go shorter, or empty"],
  "notes": ["every retake group dropped, water trimmed, stumble removed"]
}
\`\`\`
(natural_seconds = length after invisible+water only; kept_seconds = total of
the segments you output. In Clean Mode they are equal.)

After writing, report briefly: original→kept seconds, top 3-5 cuts, what (if
anything) you dropped as content, and whether the result stays coherent.
EOF
  echo "─── Step 3 ⏸ Editorial subagent needed"
  echo "    Prompt: ${PROMPT_FILE#$REPO_ROOT/}"
  echo "    Output: ${STAGE_DIR#$REPO_ROOT/}/edl-rough.json"
  echo ""
  echo "    Spawn a general-purpose subagent with that prompt, then re-run:"
  echo "      bash tools/02-rough-cut/roughcut.sh \"$INPUT_ABS\" $SLUG${TARGET:+ --target $TARGET}"
  exit 100
fi

# ── Step 4 — pad-bleed validation ────────────────────────────
if [ ! -f "$STAGE_DIR/edl-rough-safe.json" ]; then
  echo "─── Step 4 — pad-bleed validation"
  python3 "$CC/editorial_pass.py" \
    "$STAGE_DIR/edl-rough.json" "$STAGE_DIR/raw-elevenlabs.json" \
    -o "$STAGE_DIR/edl-rough-safe.json" 2>&1 | tail -3
fi

# ── Step 5 — apply rough EDL → cleaned-rough.mp4 ─────────────
if [ ! -f "$STAGE_DIR/cleaned-rough.mp4" ]; then
  echo "─── Step 5 — apply rough EDL → cleaned-rough.mp4"
  python3 "$CC/apply_edits.py" \
    "$SRC" "$STAGE_DIR/edl-rough-safe.json" \
    -o "$STAGE_DIR/cleaned-rough.mp4" 2>&1 | tail -3
fi

# ── Step 6 — Silero VAD jump-cut EDL ─────────────────────────
if [ ! -f "$STAGE_DIR/edl-jump.json" ]; then
  echo "─── Step 6 — Silero VAD jump-cut"
  mkdir -p "$STAGE_DIR/.tmp"
  ffmpeg -hide_banner -loglevel error -nostdin -y \
    -i "$STAGE_DIR/cleaned-rough.mp4" -ac 1 -ar 16000 "$STAGE_DIR/.tmp/rough.wav"
  [ -x "$VAD_PY" ] || { echo "✗ VAD env not found at $VAD_PY (run templates/_shared/scripts/clean-cut/install_vad.sh)" >&2; exit 1; }
  "$VAD_PY" "$CC/vad_detect.py" "$STAGE_DIR/.tmp/rough.wav" \
    --min-silence-ms 300 --pad-ms 200 \
    --output "$STAGE_DIR/.tmp/speech.json" 2>&1 | tail -1
  python3 "$CC/speech_to_edl.py" "$STAGE_DIR/.tmp/speech.json" \
    -o "$STAGE_DIR/edl-jump.json" 2>&1 | tail -2
fi

# ── Step 7 — apply jump EDL → jumpcut.mp4 ────────────────────
if [ ! -f "$STAGE_DIR/jumpcut.mp4" ]; then
  echo "─── Step 7 — apply jump-cut → jumpcut.mp4"
  python3 "$CC/apply_edits.py" \
    "$STAGE_DIR/cleaned-rough.mp4" "$STAGE_DIR/edl-jump.json" \
    -o "$STAGE_DIR/jumpcut.mp4" 2>&1 | tail -3
fi

# ── Step 8 — level audio (2-pass loudnorm + corrective) + mux ─
FINAL="$STAGE_DIR/rough-cut.mp4"
if [ ! -f "$FINAL" ]; then
  echo "─── Step 8 — level audio + mux → rough-cut.mp4"
  POL="$STAGE_DIR/.tmp/polished.wav"
  mkdir -p "$STAGE_DIR/.tmp"
  CHAIN="highpass=f=80,lowpass=f=12000,afftdn=nf=-25,agate=threshold=-40dB:ratio=2:attack=20:release=200,acompressor=threshold=-18dB:ratio=3:attack=5:release=50"
  # Pass 1 — analyze
  P1=$(ffmpeg -nostats -nostdin -i "$STAGE_DIR/jumpcut.mp4" -vn -ac 1 -ar 48000 \
    -af "${CHAIN},loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | python3 -c "
import sys, re, json
m = re.search(r'\{[^}]*input_i[^}]*\}', sys.stdin.read())
if not m: print('NONE'); sys.exit(0)
d = json.loads(m.group(0))
print(d['input_i'], d['input_tp'], d['input_lra'], d['input_thresh'], d.get('target_offset','0'))
")
  [ "$P1" = "NONE" ] && { echo "✗ loudnorm pass-1 parse failed" >&2; exit 1; }
  read -r IM_I IM_TP IM_LRA IM_TH IM_OFF <<< "$P1"
  # Pass 2 — apply (linear), no apad (keep A/V in sync)
  ffmpeg -nostats -nostdin -y -i "$STAGE_DIR/jumpcut.mp4" -vn -ac 1 -ar 48000 \
    -af "${CHAIN},loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${IM_I}:measured_TP=${IM_TP}:measured_LRA=${IM_LRA}:measured_thresh=${IM_TH}:offset=${IM_OFF}:linear=true:print_format=summary,alimiter=limit=-1.5dB:level=disabled" \
    -c:a pcm_s16le "$POL" 2>&1 | tail -1
  # Corrective pass (per MISTAKES.md #7 — alimiter can drift level)
  C1=$(ffmpeg -nostats -nostdin -i "$POL" \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | python3 -c "
import sys, re, json
m = re.search(r'\{[^}]*input_i[^}]*\}', sys.stdin.read())
if not m: print('NONE'); sys.exit(0)
d = json.loads(m.group(0))
print(d['input_i'], d['input_tp'], d['input_lra'], d['input_thresh'], d.get('target_offset','0'))
")
  if [ "$C1" != "NONE" ]; then
    read -r C_I C_TP C_LRA C_TH C_OFF <<< "$C1"
    ffmpeg -nostats -nostdin -y -i "$POL" \
      -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${C_I}:measured_TP=${C_TP}:measured_LRA=${C_LRA}:measured_thresh=${C_TH}:offset=${C_OFF}:print_format=summary,alimiter=limit=-1.5dB:level=disabled" \
      -ar 48000 -c:a pcm_s16le "$STAGE_DIR/.tmp/polished.corr.wav" 2>&1 | tail -1
    mv "$STAGE_DIR/.tmp/polished.corr.wav" "$POL"
  fi
  # Mux leveled audio back onto the jump-cut video (video copied, fps/aspect preserved)
  ffmpeg -hide_banner -loglevel error -nostdin -y \
    -i "$STAGE_DIR/jumpcut.mp4" -i "$POL" \
    -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -ar 48000 \
    -movflags +faststart -shortest "$FINAL"
  cp "$STAGE_DIR/edl-rough-safe.json" "$STAGE_DIR/edl.json"
fi

# ── Done ─────────────────────────────────────────────────────
FINAL_DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$FINAL")
echo ""
echo "✓ Rough cut done."
echo "    deliverable: ${FINAL#$REPO_ROOT/}"
echo "    edl:         ${STAGE_DIR#$REPO_ROOT/}/edl.json"
echo "    length:      ${DURATION}s → ${FINAL_DUR}s"
if [ -n "$TARGET" ]; then
  OVER=$(python3 -c "print(1 if ${FINAL_DUR} > ${TARGET}*1.15 else 0)")
  [ "$OVER" = "1" ] && echo "    ⚠ ${FINAL_DUR}s is >15% over the ${TARGET}s target — re-run editorial with stricter content cuts if needed."
fi
echo ""
echo "  Watch/post as-is, or feed into v88 as a new job's input/bottom.mp4."
