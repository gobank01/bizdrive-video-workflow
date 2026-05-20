#!/usr/bin/env bash
#
# Build the sample pack — a zip the maintainer shares with new developers so
# they can run the golden test. NOT committed to git (too large).
#
# Usage:
#   bash tools/build-sample-pack.sh
#
# Produces:  sample-pack-v88.zip  (in the repo root, gitignored)
#
# Contents:
#   raw-media/2026-04-23-bizdrive-stock-promo/   (the v88 reference raw clip)
#   reference-output/v88-final.mp4               (expected golden-test result)
#   SAMPLE-PACK-README.md                        (how to use it)

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

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

echo "→ Staging sample pack..."
rm -rf "$STAGE" "$OUT"
mkdir -p "$STAGE/raw-media/2026-04-23-bizdrive-stock-promo"
mkdir -p "$STAGE/reference-output"

# Copy raw clip (resolve symlinks with -L)
cp -L "$RAW_DIR/top.mp4"    "$STAGE/raw-media/2026-04-23-bizdrive-stock-promo/top.mp4"
cp -L "$RAW_DIR/bottom.mp4" "$STAGE/raw-media/2026-04-23-bizdrive-stock-promo/bottom.mp4"
cp -L "$RAW_DIR/bg.png"     "$STAGE/raw-media/2026-04-23-bizdrive-stock-promo/bg.png"

# Copy reference output if it exists
if [ -e "$REF_FINAL" ]; then
  cp -L "$REF_FINAL" "$STAGE/reference-output/v88-final.mp4"
  echo "  ✓ included reference output"
else
  echo "  ⚠ reference output not found ($REF_FINAL) — pack will have raw only"
fi

# Sample-pack README
cat > "$STAGE/SAMPLE-PACK-README.md" <<'EOF'
# BIZDRIVE Sample Pack (v88 reference clip)

Companion to the bizdrive-video-workflow repo — lets you run the golden test.

## Use it

1. Unzip into your cloned repo's `raw-media/`:

       unzip sample-pack-v88.zip
       cp -r raw-media/2026-04-23-bizdrive-stock-promo  <repo>/raw-media/

2. Scaffold a job and run the pipeline:

       cd <repo>
       bash tools/new-job.sh 01 golden-test --raw 2026-04-23-bizdrive-stock-promo
       # then follow templates/_shared/docs/V88_PLAYBOOK.md

3. Compare your final.mp4 against `reference-output/v88-final.mp4`.
   Tolerances: templates/01-stacked-vertical-burst/manifest.json → reference.goldenTest
   (duration ±50ms, ~3107 frames, 48±5 caption groups, loudness -14 to -18 LUFS).

The reference clip is a Thai BIZDRIVE direct-response video about AI stock
analysis — 130s of raw footage, ~103s final.
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
