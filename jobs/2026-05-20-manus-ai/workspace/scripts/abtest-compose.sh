#!/usr/bin/env bash
# Compose the slot 2 + slot 4 BEFORE/AFTER comparison MP4 from the 4 A/B clips.
set -euo pipefail

DIR="../intermediates/broll-abtest"
FONT="/System/Library/Fonts/Supplemental/Ayuthaya.ttf"
TMP="$DIR/labels"
mkdir -p "$TMP"

# --- label text (Thai) written to files so ffmpeg drawtext needs no escaping ---
printf '%s' "SLOT 2  -  ~27s"                                          > "$TMP/s2-title.txt"
printf '%s' "พูดว่า: ทำภาพ / ทำวิดีโอ / ทำสไลด์ / ทำเว็บไซต์"          > "$TMP/s2-sub.txt"
printf '%s' "SLOT 4  -  ~58s"                                          > "$TMP/s4-title.txt"
printf '%s' "พูดว่า: สมัครเข้าเรียนได้ทันที แค่ 3,900 บาท"             > "$TMP/s4-sub.txt"
printf '%s' "BEFORE - prompt เดิม"                                     > "$TMP/before.txt"
printf '%s' "AFTER - prompt ใหม่"                                      > "$TMP/after.txt"

segment () {
  local old="$1" new="$2" title="$3" sub="$4" out="$5"
  ffmpeg -y -loglevel error -i "$old" -i "$new" -filter_complex "
    [0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[l];
    [1:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[r];
    [l][r]hstack=inputs=2[s];
    [s]pad=1440:1480:0:200:color=0x0c0c18[bg];
    [bg]drawtext=fontfile=${FONT}:textfile=${title}:fontcolor=0xFFD700:fontsize=48:x=(w-text_w)/2:y=44[t1];
    [t1]drawtext=fontfile=${FONT}:textfile=${sub}:fontcolor=white:fontsize=34:x=(w-text_w)/2:y=120[t2];
    [t2]drawbox=x=0:y=200:w=720:h=62:color=0x7a1f1f@0.95:t=fill[d1];
    [d1]drawbox=x=720:y=200:w=720:h=62:color=0x1f5a2a@0.95:t=fill[d2];
    [d2]drawtext=fontfile=${FONT}:textfile=${TMP}/before.txt:fontcolor=white:fontsize=34:x=24:y=210[d3];
    [d3]drawtext=fontfile=${FONT}:textfile=${TMP}/after.txt:fontcolor=white:fontsize=34:x=744:y=210[v]
  " -map "[v]" -r 30 -c:v libx264 -pix_fmt yuv420p -preset medium -crf 18 -an "$out"
}

segment "$DIR/slot2-old.mp4" "$DIR/slot2-new.mp4" "$TMP/s2-title.txt" "$TMP/s2-sub.txt" "$DIR/seg-slot2.mp4"
segment "$DIR/slot4-old.mp4" "$DIR/slot4-new.mp4" "$TMP/s4-title.txt" "$TMP/s4-sub.txt" "$DIR/seg-slot4.mp4"

ffmpeg -y -loglevel error -i "$DIR/seg-slot2.mp4" -i "$DIR/seg-slot4.mp4" \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" \
  -map "[v]" -r 30 -c:v libx264 -pix_fmt yuv420p -preset medium -crf 18 -an \
  "$DIR/broll-before-after.mp4"

echo "done -> $DIR/broll-before-after.mp4"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,nb_frames,duration -of default=nw=1 "$DIR/broll-before-after.mp4"
