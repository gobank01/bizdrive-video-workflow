#!/usr/bin/env bash
# polish-audio.sh <input.(wav|mp3|mp4)> <output.wav>
#
# v88 Step 8 audio polish chain, extracted verbatim from tools/v88-clip.sh
# lines 292-340 (2-pass loudnorm linear + alimiter level=disabled + corrective
# pass per MISTAKES.md #7). If v88 Step 8 changes, re-sync this file.
set -euo pipefail

IN="$1"
OUT="$2"

P1=$(ffmpeg -nostats -nostdin -i "$IN" -vn -ac 1 -ar 48000 \
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

ffmpeg -nostats -nostdin -y -i "$IN" -vn -ac 1 -ar 48000 \
  -af "highpass=f=80,lowpass=f=12000,afftdn=nf=-25,agate=threshold=-40dB:ratio=2:attack=20:release=200,acompressor=threshold=-18dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${IM_I}:measured_TP=${IM_TP}:measured_LRA=${IM_LRA}:measured_thresh=${IM_TH}:offset=${IM_OFF}:linear=true:print_format=summary,alimiter=limit=-1.5dB:level=disabled,apad=pad_dur=0.5" \
  -c:a pcm_s16le "$OUT" 2>&1 | tail -2

C1=$(ffmpeg -nostats -nostdin -i "$OUT" \
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
ffmpeg -nostats -nostdin -y -i "$OUT" \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${C_I}:measured_TP=${C_TP}:measured_LRA=${C_LRA}:measured_thresh=${C_TH}:offset=${C_OFF}:print_format=summary,alimiter=limit=-1.5dB:level=disabled" \
  -ar 48000 -c:a pcm_s16le "${OUT%.wav}.corrected.wav" 2>&1 | tail -1
mv "${OUT%.wav}.corrected.wav" "$OUT"

FINAL_I=$(ffmpeg -nostats -i "$OUT" -af "ebur128=peak=true" -f null - 2>&1 | grep -A 14 "Summary:" | grep "I:" | head -1 | awk '{print $2}')
echo "✓ polished audio I=${FINAL_I} LUFS -> $OUT"
