#!/usr/bin/env bash
#
# Build the sample pack — a zip the maintainer shares with new developers so
# they can run the golden test. NOT committed to git (too large).
#
# Usage:
#   bash tools/build-sample-pack.sh              # raw clip only (default, smaller)
#   bash tools/build-sample-pack.sh --with-output # also include reference final.mp4
#
# Produces:  sample-pack-v88.zip  (in the repo root, gitignored)
#
# The golden-test TOLERANCES (frame count, duration, caption-group count,
# loudness) are documented in
#   templates/01-stacked-vertical-burst/manifest.json -> reference.goldenTest
# and are already in the repo — so the reference video is optional. A new dev
# checks their output's ffprobe numbers against those documented values.

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

WITH_OUTPUT=0
[ "$1" = "--with-output" ] && WITH_OUTPUT=1

RAW_DIR="raw-media/2026-04-23-bizdrive-stock-promo"
REF_FINAL="jobs/2026-05-19-bizdrive-video-div/output/finals/final.mp4"
STAGE=".sample-pack-stage"
OUT="sample-pack-v88.zip"

# --- Validate sources ---
for f in "$RAW_DIR/top.mp4" "$RAW_DIR/bottom.mp4" "$RAW_DIR/bg.png"; do
  if [ ! -e "$f" ]; then
    echo "✗ Missing reference raw file: $f" >&2
    exit 1
  fi
done

echo "→ Staging sample pack (mode: $([ $WITH_OUTPUT -eq 1 ] && echo 'raw + reference output' || echo 'raw only'))..."
rm -rf "$STAGE" "$OUT"
mkdir -p "$STAGE/raw-media/2026-04-23-bizdrive-stock-promo"

# Copy raw clip (resolve symlinks with -L)
cp -L "$RAW_DIR/top.mp4"    "$STAGE/raw-media/2026-04-23-bizdrive-stock-promo/top.mp4"
cp -L "$RAW_DIR/bottom.mp4" "$STAGE/raw-media/2026-04-23-bizdrive-stock-promo/bottom.mp4"
cp -L "$RAW_DIR/bg.png"     "$STAGE/raw-media/2026-04-23-bizdrive-stock-promo/bg.png"

# Optionally include the reference output
if [ $WITH_OUTPUT -eq 1 ] && [ -e "$REF_FINAL" ]; then
  mkdir -p "$STAGE/reference-output"
  cp -L "$REF_FINAL" "$STAGE/reference-output/v88-final.mp4"
  echo "  ✓ included reference output"
fi

# Sample-pack README
cat > "$STAGE/SAMPLE-PACK-README.md" <<'EOF'
# BIZDRIVE Sample Pack (v88 reference clip)

Companion to the bizdrive-video-workflow repo — lets you run the golden test.

## Use it

1. Unzip and copy the raw clip into your cloned repo's `raw-media/`:

       unzip sample-pack-v88.zip
       cp -r raw-media/2026-04-23-bizdrive-stock-promo  <repo>/raw-media/

2. Scaffold a job and run the pipeline:

       cd <repo>
       bash tools/new-job.sh 01 golden-test --raw 2026-04-23-bizdrive-stock-promo
       # then follow templates/_shared/docs/V88_PLAYBOOK.md

3. Golden-test check — compare YOUR output's ffprobe numbers to the documented
   tolerances in:
       templates/01-stacked-vertical-burst/manifest.json -> reference.goldenTest

   Expected (v88 reference): ~103.5s, 3107 video frames, 48 ±5 caption groups,
   loudness -14 to -18 LUFS. If your output lands in range, your environment
   is correct.

The reference clip is a Thai BIZDRIVE direct-response video about AI stock
analysis — 130s of raw footage, ~103s final.

(If this pack was built with --with-output, reference-output/v88-final.mp4 is
the maintainer's rendered result for visual comparison.)
EOF

# --- Zip ---
echo "→ Zipping..."
( cd "$STAGE" && zip -qr "../$OUT" . )
rm -rf "$STAGE"

SIZE=$(du -h "$OUT" | cut -f1)
echo ""
echo "✓ Built $OUT ($SIZE)"
echo ""
echo "Share this file with new developers (Google Drive / WeTransfer / etc)."
echo "It is gitignored — do NOT commit it."
