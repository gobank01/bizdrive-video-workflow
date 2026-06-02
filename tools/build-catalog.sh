#!/usr/bin/env bash
#
# Regenerate templates/CATALOG.md — a visual index of every template.
#
# For each templates/NN-*/ it:
#   1. picks a source render — manifest.reference.output if it points at a real
#      file, otherwise the newest jobs/* built on that template that has a
#      finals/final.mp4;
#   2. extracts a thumbnail (40% through the clip) → templates/NN-*/thumbnail.jpg;
#   3. builds templates/NN-*/mockup.svg — the thumbnail with labelled layout
#      callouts (via tools/build-mockups.py);
#   4. writes a markdown gallery row from the template's manifest.json.
#
# If a template has no available render, the already-committed mockup.svg /
# thumbnail.jpg in the template folder is reused so its preview survives.
#
# Run it any time you add or change a template:
#   bash tools/build-catalog.sh
#
# Requirements: bash, ffmpeg, ffprobe, python3
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

CATALOG="templates/CATALOG.md"
THUMB_W=340       # extracted thumbnail width (px)
MOCKUP_W=480      # mockup.svg display width in the catalog (px)

command -v ffmpeg  >/dev/null || { echo "✗ ffmpeg not found"  >&2; exit 1; }
command -v ffprobe >/dev/null || { echo "✗ ffprobe not found" >&2; exit 1; }

echo "→ Building template catalog"

# --- Catalog header ---------------------------------------------------------
cat > "$CATALOG" <<EOF
# 🎬 Template Catalog

Visual index of every BIZDRIVE video template. **Auto-generated — do not edit by
hand.** Regenerate after adding or changing a template:

\`\`\`bash
bash tools/build-catalog.sh
\`\`\`

Each preview is the template's reference render (or its newest job) with the
layout zones labelled. Start a clip with \`bash tools/new-job.sh <NN> <slug> --raw <raw-slug>\`.

_Last built: $(date '+%Y-%m-%d %H:%M')_

| Preview | Template |
| :-----: | :------- |
EOF

# --- Per-template rows ------------------------------------------------------
count=0
for tdir in templates/[0-9]*-*/; do
  tdir="${tdir%/}"
  tname="$(basename "$tdir")"
  num="${tname%%-*}"
  manifest="$tdir/manifest.json"
  [ -f "$manifest" ] || continue
  count=$((count + 1))

  # Fields from manifest.json
  name=$(python3 -c "import json;print(json.load(open('$manifest')).get('name',''))")
  desc=$(python3 -c "import json;print(json.load(open('$manifest')).get('description','').replace('|','/'))")
  tid=$(python3 -c "import json;print(json.load(open('$manifest')).get('id','$tname'))")
  spec=$(python3 -c "
import json
o=json.load(open('$manifest')).get('output',{})
print(f\"{o.get('aspect','?')} · {o.get('width','?')}×{o.get('height','?')} · {o.get('fps','?')}fps\")")
  caption=$(python3 -c "
import json
c=json.load(open('$manifest')).get('captions',{})
print(c.get('style') or c.get('system') or '?')")

  # Source render: manifest.reference.output if it is a real file, else newest job
  src=$(python3 -c "
import json,os,glob
m=json.load(open('$manifest'))
ref=(m.get('reference') or {}).get('output','') or ''
ref=ref.split(' ')[0].strip()
if ref and os.path.isfile(ref):
    print(ref); raise SystemExit
cands=[]
for jm in glob.glob('jobs/*/manifest.json'):
    try: jd=json.load(open(jm))
    except Exception: continue
    if not isinstance(jd, dict): continue   # skip malformed local job manifests
    if jd.get('template')=='$tid':
        f=os.path.join(os.path.dirname(jm),'output/finals/final.mp4')
        if os.path.isfile(f): cands.append(f)
print(sorted(cands)[-1] if cands else '')")

  # Thumbnail + labelled mockup
  thumb_rel=""
  mockup_rel=""
  if [ -n "$src" ] && [ -f "$src" ]; then
    dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$src" 2>/dev/null || echo 0)
    ts=$(python3 -c "print(round(max(float('$dur'),0.1)*0.4,2))")
    if ffmpeg -y -v error -ss "$ts" -i "$src" -vframes 1 -vf "scale=${THUMB_W}:-1" -q:v 3 "$tdir/thumbnail.jpg" 2>/dev/null; then
      thumb_rel="$tname/thumbnail.jpg"
      if python3 tools/build-mockups.py "$tdir" >/dev/null 2>&1 && [ -f "$tdir/mockup.svg" ]; then
        mockup_rel="$tname/mockup.svg"
      fi
      echo "  ✓ $tname  ← $(basename "$(dirname "$(dirname "$(dirname "$src")")")")"
    fi
  fi
  # Fallback: no fresh render this run, but the template already ships a
  # committed mockup.svg / thumbnail.jpg — reuse it so the preview survives even
  # when the source job render is gone (jobs/ is gitignored and gets pruned).
  if [ -z "$mockup_rel" ] && [ -f "$tdir/mockup.svg" ]; then
    mockup_rel="$tname/mockup.svg"
    [ -n "$src" ] || echo "  ↺ $tname  (reused committed mockup.svg — no fresh render)"
  fi
  if [ -z "$thumb_rel" ] && [ -f "$tdir/thumbnail.jpg" ]; then
    thumb_rel="$tname/thumbnail.jpg"
  fi
  if [ -z "$mockup_rel" ] && [ -z "$thumb_rel" ]; then
    echo "  ⚠ $tname  (no render yet — no preview)"
  fi

  # Markdown row — prefer the labelled mockup, fall back to the plain thumbnail
  if [ -n "$mockup_rel" ]; then
    cell_img="<img src=\"$mockup_rel\" width=\"$MOCKUP_W\" />"
  elif [ -n "$thumb_rel" ]; then
    cell_img="<img src=\"$thumb_rel\" width=\"$THUMB_W\" />"
  else
    cell_img="_(no render yet)_"
  fi
  printf '| %s | **%s — %s**<br>📐 %s<br>💬 Captions: **%s**<br><br>%s<br><br>📂 `templates/%s/` · scaffold: `bash tools/new-job.sh %s <slug> --raw <raw>` |\n' \
    "$cell_img" "$num" "$name" "$spec" "$caption" "$desc" "$tname" "$num" \
    >> "$CATALOG"
done

# --- Footer -----------------------------------------------------------------
cat >> "$CATALOG" <<EOF

---

**$count templates.** Pick by layout + caption style:

- **Layout** — \`stacked\` (screen recording on top + face circle) · \`fullscreen\` (single talking-head) · \`top-insert\` (full-screen + floating B-roll card)
- **Captions** — \`particle-burst\` (white/gold text + dot burst, calmer premium) · \`caption-highlight\` / Karaoke (red/gold box sweep, punchy CapCut style)

See each template's \`DESIGN.md\` for the full spec.
EOF

echo "✓ Wrote $CATALOG ($count templates)"
