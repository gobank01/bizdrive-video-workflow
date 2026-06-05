#!/usr/bin/env bash
#
# v88-clip.sh — mechanical 16-step runner for ONE child job.
#
# Takes a scaffolded job dir (with input/bottom.mp4 + intermediates/raw-elevenlabs.json
# + job-spec.json) and runs every v88 step that doesn't need a subagent.
#
# At Step 3 (Editorial) and Step 10 (Post-process), the script writes a
# ready-to-paste subagent prompt file and EXITS with code 100. The calling
# agent (Claude / Codex / human) spawns the subagent, lands its output JSON
# at the expected path, then re-runs this script. The script detects the
# JSON and resumes — same command, no flags needed.
#
# Usage:
#   bash tools/v88-clip.sh <job-dir> [--bgm <id>] [--main "X"] [--hero "Y"] [--sub "Z"] [--skip-thumbnail]
#
# Example:
#   bash tools/v88-clip.sh jobs/2026-05-27-next-humans-finance-clip01
#   # → exits 100 with "spawn Editorial subagent" instructions
#   # (agent spawns subagent → writes edl-rough.json)
#   bash tools/v88-clip.sh jobs/2026-05-27-next-humans-finance-clip01
#   # → continues past Step 3, exits 100 again for Post-process
#   # (agent spawns subagent → writes caption-groups.json)
#   bash tools/v88-clip.sh jobs/2026-05-27-next-humans-finance-clip01
#   # → finishes Steps 11-16, emits <clip>.mp4 + <clip>.png
#
# Exit codes:
#   0   — fully done (final deliverable exists)
#   100 — paused for subagent (read the printed prompt file)
#   1   — error
#
# Defaults: BGM = mixkit-720 (uplifting bass + business-tech), thumbnail
# 3-line headline derived from topic if not overridden.

set -e

# --- Parse args ---
JOB_DIR_ARG=""
BGM_ID="mixkit-720-new-bass-01"
TH_MAIN=""
TH_HERO=""
TH_SUB=""
SKIP_THUMB=0
CAPTION_OFFSET_MS=120
POSITIONAL=()

while [ $# -gt 0 ]; do
  case "$1" in
    --bgm) BGM_ID="$2"; shift 2 ;;
    --main) TH_MAIN="$2"; shift 2 ;;
    --hero) TH_HERO="$2"; shift 2 ;;
    --sub) TH_SUB="$2"; shift 2 ;;
    --skip-thumbnail) SKIP_THUMB=1; shift ;;
    --caption-offset-ms) CAPTION_OFFSET_MS="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,38p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

if [ ${#POSITIONAL[@]} -lt 1 ]; then
  echo "Usage: bash tools/v88-clip.sh <job-dir> [--bgm <id>] [--main \"X\"] [--hero \"Y\"] [--sub \"Z\"]" >&2
  exit 1
fi

JOB_DIR_ARG=${POSITIONAL[0]}
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Resolve job dir
if [[ "$JOB_DIR_ARG" = /* ]]; then
  JOB_DIR="$JOB_DIR_ARG"
else
  JOB_DIR="$REPO_ROOT/$JOB_DIR_ARG"
fi
JOB_DIR="$(cd "$JOB_DIR" && pwd)"
JOB_NAME=$(basename "$JOB_DIR")
WS="$JOB_DIR/workspace"

if [ ! -d "$WS" ]; then
  echo "✗ No workspace/ in $JOB_DIR" >&2
  exit 1
fi
if [ ! -f "$JOB_DIR/job-spec.json" ]; then
  echo "✗ No job-spec.json in $JOB_DIR" >&2
  exit 1
fi
if [ ! -f "$JOB_DIR/input/bottom.mp4" ]; then
  echo "✗ No input/bottom.mp4 in $JOB_DIR" >&2
  exit 1
fi

# Read job spec
TEMPLATE_FULL=$(python3 -c "import json; print(json.load(open('$JOB_DIR/job-spec.json'))['template'])")
TEMPLATE_NUM=${TEMPLATE_FULL:0:2}
TOPIC=$(python3 -c "import json; print(json.load(open('$JOB_DIR/job-spec.json')).get('topic',''))")
HAS_TRANSCRIPT=$(python3 -c "
import json
s=json.load(open('$JOB_DIR/job-spec.json'))
print(s.get('inputs',{}).get('transcript_provided','') != '')
")

echo "═══ v88-clip: $JOB_NAME ═══"
echo "    template: $TEMPLATE_FULL (T$TEMPLATE_NUM)"
echo "    topic:    $TOPIC"
echo ""

V88="$WS/assets/intermediates/v88-test"
TRANSCRIPT="$WS/assets/intermediates/transcript"
mkdir -p "$V88" "$TRANSCRIPT"

# Resolve the Silero VAD venv python. Linux/macOS put it at bin/python3;
# native Windows (Git Bash) puts it at Scripts/python.exe. Pick whichever
# exists so Step 6 runs the same on every OS.
VAD_PY="$HOME/.ii23/vad-env/bin/python3"
if [ ! -x "$VAD_PY" ] && [ -x "$HOME/.ii23/vad-env/Scripts/python.exe" ]; then
  VAD_PY="$HOME/.ii23/vad-env/Scripts/python.exe"
fi

# Caption builder choice based on template
case "$TEMPLATE_NUM" in
  01|03) CAPTION_SCRIPT="build-burst-captions.py" ; CAPTION_HTML="captions-burst.html" ;;
  02)    CAPTION_SCRIPT="build-burst-captions.py" ; CAPTION_HTML="captions-burst.html" ;;
  04|05) CAPTION_SCRIPT="build-highlight-captions.py" ; CAPTION_HTML="captions-highlight.html" ;;
  06)    CAPTION_SCRIPT="build-burst-captions.py" ; CAPTION_HTML="captions-burst.html" ;;
  07)    CAPTION_SCRIPT="build-highlight-captions.py" ; CAPTION_HTML="captions-highlight.html" ;;
  08)    CAPTION_SCRIPT="build-weightshift-captions.py" ; CAPTION_HTML="captions-weightshift.html" ;;
  *)
    echo "✗ Unknown template number: $TEMPLATE_NUM" >&2
    exit 1 ;;
esac

# Bottom px (caption position) per template
case "$TEMPLATE_NUM" in
  04|02) CAPTION_BOTTOM=330 ;;
  05|01|08) CAPTION_BOTTOM=360 ;;
  *)     CAPTION_BOTTOM=330 ;;
esac

# ─────────────────────────────────────────────
# Step 1 — inspect (also normalize 50/60→30 fps if needed)
# ─────────────────────────────────────────────
if [ ! -f "$V88/.step1.done" ]; then
  echo "─── Step 1 — inspect bottom.mp4"
  FPS=$(ffprobe -v error -select_streams v -show_entries stream=r_frame_rate -of default=nw=1:nk=1 "$JOB_DIR/input/bottom.mp4")
  NUM=${FPS%/*}; DEN=${FPS#*/}
  FPS_INT=$((NUM / DEN))
  if [ "$FPS_INT" != "30" ]; then
    echo "    ⚠ source is ${FPS_INT}fps — re-encoding to 30fps + GOP 30"
    ffmpeg -hide_banner -loglevel error -nostdin -y \
      -i "$JOB_DIR/input/bottom.mp4" \
      -r 30 -c:v libx264 -preset veryfast -crf 18 \
      -g 30 -keyint_min 30 -movflags +faststart \
      -c:a aac -b:a 192k -ar 48000 \
      "$JOB_DIR/input/bottom.30fps.mp4"
    mv "$JOB_DIR/input/bottom.30fps.mp4" "$JOB_DIR/input/bottom.mp4"
  fi
  DURATION=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$JOB_DIR/input/bottom.mp4")
  echo "    ✓ $DURATION s @ 30fps"
  echo "$DURATION" > "$V88/.step1.done"
fi
DURATION=$(cat "$V88/.step1.done")

# ─────────────────────────────────────────────
# Step 2 — transcript (copy from intermediates/ + clean boundary artifacts)
# ─────────────────────────────────────────────
if [ ! -f "$V88/raw-elevenlabs.json" ]; then
  echo "─── Step 2 — transcript"
  if [ "$HAS_TRANSCRIPT" = "True" ] && [ -f "$JOB_DIR/intermediates/raw-elevenlabs.json" ]; then
    cp "$JOB_DIR/intermediates/raw-elevenlabs.json" "$V88/raw-elevenlabs.json"
    python3 - "$V88/raw-elevenlabs.json" "$DURATION" <<'PY'
import json, sys
p, dur = sys.argv[1], float(sys.argv[2])
d = json.load(open(p))
before = len(d.get("words", []))
d["words"] = [w for w in d["words"] if (w["end"] - w["start"]) >= 0.05]
d["text"] = " ".join(w.get("text", "") for w in d["words"]).strip()
d["duration"] = dur
after = len(d["words"])
json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)
print(f"    ✓ {after} entries (dropped {before-after} zero-duration artifacts)")
PY
  else
    echo "    ⚠ no transcript_provided in job-spec — would need to run ElevenLabs Scribe here"
    echo "      (out of scope for v88-clip.sh; use longform-prep.sh upstream)"
    exit 1
  fi
fi

# ─────────────────────────────────────────────
# Step 3 — Editorial subagent
# ─────────────────────────────────────────────
if [ ! -f "$V88/edl-rough.json" ]; then
  PROMPT_FILE="$V88/editorial-prompt.txt"
  cat > "$PROMPT_FILE" <<EOF
You are doing a rough cut on a raw recording for the BIZDRIVE stacked-video workflow (v88, bizdrive-pipeline integration).

## Inputs

- Raw transcript (ElevenLabs Scribe v2, Thai): $V88/raw-elevenlabs.json
- Source media (sliced from longform): $JOB_DIR/input/bottom.mp4
- Source duration: ${DURATION}s
- Topic / context: $TOPIC
- Speaker register: hype (closing/conviction-driven if longform-child)
- Target language: th
- Target output duration: ceiling ~${DURATION}s — usually keep most of it (pre-curated short)
- Output: $V88/edl-rough.json

## Read the editorial rules FIRST

$WS/scripts/clean-cut/references/editorial-rules.md

(Apply: last-take-wins, false starts, fillers, mid-sentence stumbles, dead air, final-20% scrutiny. Thai particles ครับ/นะ/ค่ะ are KEPT.)

## Hard requirements

1. Every kept segment from raw.json.words[] timing — don't invent.
2. start_ms/end_ms integers (ms).
3. Segments chronological, non-overlapping.
4. Pad head ~200ms, tail 50-100ms — never bleed into a dropped next word.
5. Output strict JSON to $V88/edl-rough.json:

\`\`\`json
{
  "segments": [{"start_ms": int, "end_ms": int}, ...],
  "language": "th",
  "register": "hype",
  "kept_seconds": float,
  "original_seconds": ${DURATION},
  "notes": ["..."]
}
\`\`\`

After writing, report briefly: trims, segments survived, top 3-5 cuts (or "no major cuts"), ambiguities, whether content is coherent.
EOF
  echo "─── Step 3 ⏸ Editorial subagent needed"
  echo "    Prompt: $PROMPT_FILE"
  echo "    Output: $V88/edl-rough.json"
  echo ""
  echo "    Spawn a subagent with this prompt, then re-run:"
  echo "      bash tools/v88-clip.sh ${JOB_DIR#$REPO_ROOT/}"
  exit 100
fi

# ─────────────────────────────────────────────
# Step 4 — pad-bleed
# ─────────────────────────────────────────────
if [ ! -f "$V88/edl-rough-safe.json" ]; then
  echo "─── Step 4 — pad-bleed validation"
  (cd "$WS" && npm run rough:cut:padbleed -- \
    assets/intermediates/v88-test/edl-rough.json \
    assets/intermediates/v88-test/raw-elevenlabs.json \
    -o assets/intermediates/v88-test/edl-rough-safe.json 2>&1 | tail -3)
fi

# ─────────────────────────────────────────────
# Step 5 — apply rough EDL
# ─────────────────────────────────────────────
if [ ! -f "$V88/cleaned-rough.mp4" ]; then
  echo "─── Step 5 — apply rough EDL → cleaned-rough.mp4"
  (cd "$WS" && npm run apply:edits -- \
    assets/input/bottom.mp4 \
    assets/intermediates/v88-test/edl-rough-safe.json \
    -o assets/intermediates/v88-test/cleaned-rough.mp4 2>&1 | tail -3)
fi

# ─────────────────────────────────────────────
# Step 6 — Silero VAD jump-cut
# ─────────────────────────────────────────────
if [ ! -f "$V88/edl-jump.json" ]; then
  echo "─── Step 6 — Silero VAD jump-cut"
  mkdir -p "$V88/.tmp"
  ffmpeg -hide_banner -loglevel error -nostdin -y \
    -i "$V88/cleaned-rough.mp4" -ac 1 -ar 16000 "$V88/.tmp/post-rough.wav"
  "$VAD_PY" "$WS/scripts/clean-cut/vad_detect.py" \
    "$V88/.tmp/post-rough.wav" \
    --min-silence-ms 300 --pad-ms 200 \
    --output "$V88/.tmp/speech.json" 2>&1 | tail -1
  (cd "$WS" && npm run jump:cut:edl -- \
    assets/intermediates/v88-test/.tmp/speech.json \
    -o assets/intermediates/v88-test/edl-jump.json 2>&1 | tail -2)
fi

# ─────────────────────────────────────────────
# Step 7 — apply jump EDL → bottom_visual_master.mp4
# ─────────────────────────────────────────────
if [ ! -f "$WS/assets/intermediates/bottom_visual_master.mp4" ]; then
  echo "─── Step 7 — apply jump EDL → bottom_visual_master.mp4"
  (cd "$WS" && npm run apply:edits -- \
    assets/intermediates/v88-test/cleaned-rough.mp4 \
    assets/intermediates/v88-test/edl-jump.json \
    -o assets/intermediates/bottom_visual_master.mp4 2>&1 | tail -3)
fi
MASTER_DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$WS/assets/intermediates/bottom_visual_master.mp4")
echo "    bottom_visual_master.mp4 = ${MASTER_DUR}s"

# ─────────────────────────────────────────────
# Step 8 — polish bottom audio (2-pass + corrective)
# ─────────────────────────────────────────────
SPEECH_WAV="$WS/assets/intermediates/speech_polished.wav"
if [ ! -f "$SPEECH_WAV" ]; then
  echo "─── Step 8 — polish audio (2-pass loudnorm + corrective)"
  cd "$WS"
  # Pass 1 — analyze
  P1=$(ffmpeg -nostats -nostdin -i assets/intermediates/bottom_visual_master.mp4 -vn -ac 1 -ar 48000 \
    -af "highpass=f=80,lowpass=f=12000,afftdn=nf=-25,agate=threshold=-40dB:ratio=2:attack=20:release=200,acompressor=threshold=-18dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" \
    -f null - 2>&1 | python3 -c "
import sys, re, json
text = sys.stdin.read()
m = re.search(r'\{[^}]*input_i[^}]*\}', text)
if not m:
    print('NONE'); sys.exit(0)
d = json.loads(m.group(0))
print(d['input_i'], d['input_tp'], d['input_lra'], d['input_thresh'], d.get('target_offset', '0'))
")
  if [ "$P1" = "NONE" ]; then
    echo "✗ pass-1 loudnorm parse failed" >&2
    exit 1
  fi
  read -r IM_I IM_TP IM_LRA IM_TH IM_OFF <<< "$P1"
  # Pass 2 — apply (linear, alimiter level=disabled, apad)
  ffmpeg -nostats -nostdin -y -i assets/intermediates/bottom_visual_master.mp4 -vn -ac 1 -ar 48000 \
    -af "highpass=f=80,lowpass=f=12000,afftdn=nf=-25,agate=threshold=-40dB:ratio=2:attack=20:release=200,acompressor=threshold=-18dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${IM_I}:measured_TP=${IM_TP}:measured_LRA=${IM_LRA}:measured_thresh=${IM_TH}:offset=${IM_OFF}:linear=true:print_format=summary,alimiter=limit=-1.5dB:level=disabled,apad=pad_dur=0.5" \
    -c:a pcm_s16le assets/intermediates/speech_polished.wav 2>&1 | tail -2

  # Corrective — re-analyze + apply (per MISTAKES.md #7)
  C1=$(ffmpeg -nostats -nostdin -i assets/intermediates/speech_polished.wav \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | python3 -c "
import sys, re, json
text = sys.stdin.read()
m = re.search(r'\{[^}]*input_i[^}]*\}', text)
if not m:
    print('NONE'); sys.exit(0)
d = json.loads(m.group(0))
print(d['input_i'], d['input_tp'], d['input_lra'], d['input_thresh'], d.get('target_offset', '0'))
")
  read -r C_I C_TP C_LRA C_TH C_OFF <<< "$C1"
  ffmpeg -nostats -nostdin -y -i assets/intermediates/speech_polished.wav \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${C_I}:measured_TP=${C_TP}:measured_LRA=${C_LRA}:measured_thresh=${C_TH}:offset=${C_OFF}:print_format=summary,alimiter=limit=-1.5dB:level=disabled" \
    -ar 48000 -c:a pcm_s16le assets/intermediates/speech_polished.corrected.wav 2>&1 | tail -1
  mv assets/intermediates/speech_polished.corrected.wav assets/intermediates/speech_polished.wav

  FINAL_I=$(ffmpeg -nostats -i assets/intermediates/speech_polished.wav -af "ebur128=peak=true" -f null - 2>&1 | grep -A 14 "Summary:" | grep "I:" | head -1 | awk '{print $2}')
  echo "    ✓ polished audio I=${FINAL_I} LUFS"
  cd - >/dev/null
fi

# ─────────────────────────────────────────────
# Step 9 — re-transcribe polished audio
# ─────────────────────────────────────────────
if [ ! -f "$TRANSCRIPT/raw-elevenlabs.json" ]; then
  echo "─── Step 9 — re-transcribe polished audio (ElevenLabs)"
  cd "$WS"
  export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
  set -a; source .env 2>/dev/null; set +a
  python3 scripts/transcribe/transcribe.py assets/intermediates/speech_polished.wav \
    --provider elevenlabs --lang th \
    --save-all assets/intermediates/transcript/ \
    --words-per-group 2 2>&1 | tail -1
  python3 - "$TRANSCRIPT/raw-elevenlabs.json" "$MASTER_DUR" <<'PY'
import json, sys
p, dur = sys.argv[1], float(sys.argv[2])
d = json.load(open(p))
d["duration"] = dur
json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)
print(f"    ✓ duration patched → {dur}s, words = {len(d.get('words', []))}")
PY
  cd - >/dev/null
fi

# ─────────────────────────────────────────────
# Step 10 — Post-process subagent → caption-groups.json
# ─────────────────────────────────────────────
if [ ! -f "$TRANSCRIPT/caption-groups.json" ]; then
  PROMPT_FILE="$V88/post-process-prompt.txt"
  cat > "$PROMPT_FILE" <<EOF
You are doing post-process #1 (text fix) AND caption segmentation for the BIZDRIVE v88 pipeline.

## Inputs

- Raw transcript (edited timeline, polished): $TRANSCRIPT/raw-elevenlabs.json
- Source audio: $WS/assets/intermediates/speech_polished.wav
- Video duration: ${MASTER_DUR}s
- Post-process protocol: $WS/scripts/transcribe/references/post-process-protocol.md
- Topic: $TOPIC
- Gold token policy: brand/tech names (AI, AI Agent, crypto, US Dollar, Stablecoin, etc.), numeric figures, key emphasis words. Aim 1:3-1:4 gold:white ratio.

## Output

Write to: $TRANSCRIPT/caption-groups.json

\`\`\`json
{
  "duration": ${MASTER_DUR},
  "language": "th",
  "source_provider": "elevenlabs",
  "post_processed_at": "<ISO 8601>",
  "groups": [{ "start": <float>, "end": <float, ≤${MASTER_DUR}>, "tokens": [{"text":"...","gold":false}] }],
  "notes": ["..."]
}
\`\`\`

Rules: ≤22 visible Thai chars/group · 1-3 tokens · timing from raw.words[] (don't invent) · break at ครับ/นะ/ค่ะ/แต่/ก็/และ/ที่/หรือ/เพราะ/แล้ว · Latin loanwords stay Latin · numbers → digits where natural · particles KEPT, standalone fillers (เออ/อ่ะ/อืม) DROPPED · no overlaps · last end ≤ duration.

After writing, report briefly: counts, top fixes, merges/splits, ambiguities, first 3 + last 2 groups.
EOF
  echo "─── Step 10 ⏸ Post-process subagent needed"
  echo "    Prompt: $PROMPT_FILE"
  echo "    Output: $TRANSCRIPT/caption-groups.json"
  echo ""
  echo "    Spawn a subagent with this prompt, then re-run:"
  echo "      bash tools/v88-clip.sh ${JOB_DIR#$REPO_ROOT/}"
  exit 100
fi

# ─────────────────────────────────────────────
# Step 11 — build composition + captions
# ─────────────────────────────────────────────
if [ ! -f "$WS/compositions/$CAPTION_HTML" ] || [ ! -f "$V88/.step11.done" ]; then
  echo "─── Step 11 — set-duration + caption-offset (-${CAPTION_OFFSET_MS}ms) + build $CAPTION_HTML"
  (cd "$WS" && python3 scripts/set-duration.py "$MASTER_DUR" 2>&1 | tail -2)
  # Apply universal caption offset to fix ElevenLabs phrase-level lag.
  # Reads transcript/caption-groups.json, writes a shifted copy that the
  # build script consumes. Original subagent output preserved.
  python3 "$REPO_ROOT/tools/01-longform-shorts/apply-caption-offset.py" \
    "$TRANSCRIPT/caption-groups.json" \
    "$TRANSCRIPT/caption-groups.shifted.json" \
    --offset-ms "$CAPTION_OFFSET_MS"
  (cd "$WS" && python3 "scripts/$CAPTION_SCRIPT" \
    "assets/intermediates/transcript/caption-groups.shifted.json" \
    "compositions/$CAPTION_HTML" \
    "$MASTER_DUR" \
    "$CAPTION_BOTTOM" 2>&1 | tail -2)
  touch "$V88/.step11.done"
fi

# ─────────────────────────────────────────────
# Step 12 — lint + validate + inspect
# ─────────────────────────────────────────────
if [ ! -f "$V88/.step12.done" ]; then
  echo "─── Step 12 — lint + validate + inspect"
  (cd "$WS" && npm run check 2>&1 | tail -5)
  touch "$V88/.step12.done"
fi

# ─────────────────────────────────────────────
# Step 13 — render visual.mp4
# ─────────────────────────────────────────────
mkdir -p "$JOB_DIR/output/finals"
if [ ! -f "$JOB_DIR/output/finals/visual.mp4" ]; then
  echo "─── Step 13 — render visual.mp4 (this is the slow one)"
  (cd "$WS" && npx --yes hyperframes@0.6.25 render \
    --output ../output/finals/visual.mp4 \
    --quality standard 2>&1 | tail -3)
fi

# ─────────────────────────────────────────────
# Step 14 — mix final audio (speech + BGM)
# ─────────────────────────────────────────────
if [ ! -f "$JOB_DIR/output/finals/final.mp4" ] && [ ! -f "$JOB_DIR/output/finals/$JOB_NAME.mp4" ]; then
  echo "─── Step 14 — mix audio (BGM: $BGM_ID)"
  cat > "$JOB_DIR/intermediates/sfx-plan.json" <<EOF
{
  "duration": $MASTER_DUR,
  "visual": "../output/finals/visual.mp4",
  "speech": "assets/intermediates/speech_polished.wav",
  "bgm": "assets/bgm/stock/mixkit/${BGM_ID}.mp3",
  "bgmGainPercent": 5,
  "sfx": []
}
EOF
  (cd "$WS" && python3 scripts/mix-sfx.py 2>&1 | tail -3)
fi

# ─────────────────────────────────────────────
# Step 15 — QA
# ─────────────────────────────────────────────
echo "─── Step 15 — QA"
ffprobe -v error -show_entries format=duration:stream=codec_type,nb_frames -of csv=p=0 "$JOB_DIR/output/finals/final.mp4" 2>/dev/null | head -3 | sed 's/^/    /'

# ─────────────────────────────────────────────
# Step 16 — thumbnail + poster prepend
# ─────────────────────────────────────────────
if [ "$SKIP_THUMB" != "1" ] && [ ! -f "$JOB_DIR/output/finals/$JOB_NAME.png" ]; then
  echo "─── Step 16 — thumbnail + poster prepend"
  # Auto thumbnail lines from topic if not provided
  if [ -z "$TH_MAIN" ]; then
    # Split topic into 3 chunks at natural break points
    SPLIT=$(python3 - "$TOPIC" <<'PY'
import sys, re
t = sys.argv[1].strip()
# Try splitting on " — " or " - " first
for sep in [" — ", " - ", " | ", "? ", "! "]:
    if sep in t:
        parts = t.split(sep, 1)
        # Try further splitting the second half
        rest = parts[1]
        for s2 in [" — ", " - ", " | ", ", "]:
            if s2 in rest:
                p2 = rest.split(s2, 1)
                print(parts[0]); print(p2[0]); print(p2[1])
                sys.exit(0)
        # No 2nd split — split at midpoint of rest by space
        words = rest.split()
        mid = max(1, len(words) // 2)
        print(parts[0]); print(" ".join(words[:mid])); print(" ".join(words[mid:]))
        sys.exit(0)
# Fallback — split into 3 even chunks by word count
words = t.split()
n = max(1, len(words) // 3)
print(" ".join(words[:n]))
print(" ".join(words[n:2*n]))
print(" ".join(words[2*n:]) or "—")
PY
)
    TH_MAIN=$(echo "$SPLIT" | sed -n '1p')
    TH_HERO=$(echo "$SPLIT" | sed -n '2p')
    TH_SUB=$(echo "$SPLIT"  | sed -n '3p')
  fi
  (cd "$WS" && python3 scripts/build-thumbnail.py "$TH_MAIN" "$TH_HERO" "$TH_SUB" 2>&1 | tail -3)
fi

# ─────────────────────────────────────────────
echo ""
echo "✓ v88-clip done: $JOB_NAME"
DELIVERABLE="$JOB_DIR/output/finals/$JOB_NAME.mp4"
[ -f "$DELIVERABLE" ] && echo "  → $DELIVERABLE" || echo "  → $JOB_DIR/output/finals/final.mp4 (no thumbnail prepended)"
