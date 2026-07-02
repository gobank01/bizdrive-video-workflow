# Template 10 — Production Recipe (out-of-studio slides + face → multimode clip)

> **#0 RULE — หน้าคนเป็นหลัก (face-first):** the presenter's face is the hero of
> the clip. Every framing/crop/layout choice prioritises a centered, prominent
> face. Slides/B-roll/AI inserts are *support* — they must never bury the face.
> Split still shows the face clearly (bottom half); full-screen inserts are short
> beats only. When in doubt, choose "see the face" over "show the visual." Verify
> by extracting real frames (full + split + insert) before delivery.

The full, reproducible concept + step-by-step playbook, as proven on
`jobs/2026-06-24-claude-model-t10` ("Claude models" clip). Use this whenever the
source is an **out-of-studio recording that has both a face cam AND a screen /
slide recording** and you want the T10 look.

---

## The concept (why it doesn't get boring)

ONE presenter, audio master = the face. The video **cuts between THREE visual
beats**, switched by content:

1. **Full-face** (1080×1920) — the hook, personal/recommendation moments. Face centered.
2. **Split-top** — the screen/slide fills the TOP half, the face drops to a
   full-bleed BOTTOM rectangle. Used while a slide/topic is being explained.
   This is the workhorse — aim **~65–70 % of the clip**.
3. **Full-screen AI insert** — an OpenRouter-generated B-roll cutaway fills the
   whole frame for ~3 s at a "talking-in-the-abstract" transition (no slide tied
   to it). The 3rd beat that adds variety.

Captions throughout = **BIZDRIVE blue word-sweep** (every word white, the spoken
word pops to blue `#2EA8FF`, no box, no particles), centered over the seam (bottom 910).

The pacing rule that makes it feel intentional: **change layout when the topic /
slide changes, and let the face breathe full-screen between topics.** Merge
adjacent split windows (carry the face down across the slide change) so the face
never bobs up-then-down in <1 s.

---

## Inputs (out-of-studio set)

| File | Role |
|------|------|
| **Bottom02.mp4** | face master = `input/bottom.mp4`. **RULE: always Bottom02, never Bottom.mp4.** |
| top.mp4 | screen recording / slides → source for split-top + slide inserts |
| (bg.png) | fallback bg — copy any template's `assets/bg.png` |

Both cams are the same 16:9 take. The face sits **~57 % horizontally** (right of
centre) → must re-centre (see §face-centering).

---

## Step-by-step (what actually worked)

### 0. Scaffold
```bash
ln -sf ".../Bottom02.mp4" raw-media/<slug>/bottom.mp4   # RULE: Bottom02
ln -sf ".../top.mp4"      raw-media/<slug>/top.mp4
cp templates/02-*/assets/bg.png raw-media/<slug>/bg.png
bash tools/new-job.sh 10 <slug> --raw <slug>
# job-spec.json: template "10-multimode-vertical-sweep", topic, inputs.transcript_provided set
```

### 1. Transcribe the face (original) → editorial
```bash
cd jobs/<job>/workspace
export SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())"); set -a; source .env; set +a
python3 scripts/transcribe/transcribe.py assets/input/bottom.mp4 --provider elevenlabs --lang th \
  --save-all ../intermediates/ --words-per-group 2
```

### 2. Run v88-clip → it pauses twice (Step 3 editorial, Step 10 captions)
```bash
bash tools/v88-clip.sh jobs/<job>          # → exits 100 at Step 3
```
- **Step 3 editorial**: pre-curated short → keep full, ONE segment
  (trim ~1 s head silence), let VAD tighten. Write `…/v88-test/edl-rough.json`.
- Re-run → cut + polish + re-transcribe edited audio → pauses at Step 10.
- **Step 10 captions**: segment the *edited* transcript with the helper (below),
  hand-fix artifacts, write `…/transcript/caption-groups.json`.

### 3. Caption segmentation (blue word-sweep)
Use a char-level interpolated segmenter (pythainlp), NOT `words.json` (it shares
one time-window across a merged EL word → captions overlap). Reference:
`scratchpad/segment_captions.py` in the worked job. It does:
- pythainlp tokenize each EL word, distribute the word's [start,end] across
  sub-tokens by char length → no overlap, real per-word timing
- ≤14 visible Thai chars/group, 1–2 display tokens
- **drop politeness particles anywhere** (ครับ/นะครับ/ค่ะ…) — BIZDRIVE style
- gold-flag model/tech/number tokens (Haiku/Sonnet/Opus/Fable/Mythos/Token/coding/Low/High)
- insert a space at Thai↔Latin boundaries; collapse stutters (OpusOpus→Opus)
- hand-fix: stray digit artifacts, awkward merges

### 4. Build captions (manual Step 11 — so you can inject B-roll before render)
```bash
M=<master_dur>   # ffprobe assets/intermediates/bottom_visual_master.mp4
python3 scripts/set-duration.py $M
python3 ../../../tools/01-longform-shorts/apply-caption-offset.py \
  assets/intermediates/transcript/caption-groups.json assets/intermediates/transcript/caption-groups.shifted.json --offset-ms 120
python3 scripts/build-sweep-captions.py assets/intermediates/transcript/caption-groups.shifted.json \
  compositions/captions-sweep.html $M 910
touch assets/intermediates/v88-test/.step11.done
```
> ⚠ **v88-clip.sh has NO B-roll step.** That is why Steps 5–6 are done by hand
> *between* caption-build and render, then v88-clip is re-run for lint/render/mix/thumb.

### 5. Slides → split-top inserts (letterbox to fill the top box)
The top box is 1080×960; slides are 16:9 → **letterbox to 1080×960** so the WHOLE
slide shows (cover-crop would chop slide text):
```bash
PAD="scale=1080:-2,pad=1080:960:(ow-iw)/2:(oh-ih)/2:color=0x02040d,setsar=1,fps=30"
ffmpeg -y -ss <top_time> -t <dur> -i assets/input/top.mp4 -vf "$PAD" -an \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p assets/intermediates/broll/sNN.mp4
```
- First map the slides: `ffmpeg -ss T … -frames:v 1` sample top.mp4, read which
  slide is on screen when.
- Place each split window at the edited-timeline moment that topic is discussed
  (scan the edited transcript for the keyword). Merge windows that touch (e.g.
  Fable+Mythos→summary as ONE long carve straight through the slide change) so
  the face doesn't bob.

### 6. AI inserts via OpenRouter (full-screen, the 3rd beat)
```bash
# edit scripts/generate-broll.js: 2–3 brolls, 9:16, themed prompts, output to a safe dir
set -a; source .env; set +a
node scripts/generate-broll.js     # bytedance/seedance-1-5-pro, ~$0.02/clip, ~1–2 min each
```
Prompt style: `cinematic vertical 9:16 b-roll, <concept>, deep blue with gold
accents, premium tech, no text, no logos, no people`. Place as `full` mode at
transition lines (not tied to a slide).

### 7. Inject all inserts into index.html
Each insert = a `.broll-frame` video after `#bottomVideo`:
`broll-full` (full, `data-display-mode="full"`) or `broll-split`
(`data-display-mode="split-top"`), `data-start/-duration`, transitions 0.3s,
`data-track-index` 4+. For slides: **static** (the JS already disables zoom for
`split-top` so dense slide text stays crisp). `scripts/add-broll.py` does fixed
3 s inserts; for custom durations / mixed modes inject directly (see the worked job).

### 8. Face centering — MEASURE, don't guess
Cover-crop math differs per box, so full and split need **different**
`object-position-x`. For this inbox's framing (face ~57 % of source):
- **full (1080×1920): `60% 50%`**
- **split bottom (1080×960): `64% 50%`** (vertical has no overflow in either box → y is moot)

Verify with a crop preview before rendering (don't trust a single number):
```bash
# full:  crop=608:1080:(P*1308):0   |  split: crop=1215:1080:(P*701):0
ffmpeg -ss T -i bottom_visual_master.mp4 -frames:v 1 \
  -vf "crop=608:1080:$((P*1308/100)):0,scale=270:480,drawbox=x=135:y=0:w=2:h=480:color=red" out.jpg
```
Set the three spots in index.html: `#bottomVideo` CSS, the t0 `tl.set`, and the
split-tween + revert. (Mistake log: 72 % shoved the face hard left — "เบี้ยว".)

### 9. Render + finish
```bash
rm -f assets/intermediates/v88-test/.step12.done ../output/finals/*.mp4 ../output/finals/*.png
bash tools/v88-clip.sh jobs/<job> --keep-intermediates --main "…" --hero "…" --sub "…"
```
v88-clip runs lint → render (~3 min for 115 s) → BGM mix (−16 LUFS) → thumbnail.
Verify: extract frames at a full-face, a split, and an AI-insert moment; confirm
captions white+blue, face centered, slides full. Then `open` it. Log a
`jobs/DELIVERY_LOG.md` row.

---

## Worked example — `2026-06-24-claude-model-t10`
- Bottom02 master, 117.6 → 115.5 s after dead-air; −16.0 LUFS; 3467 frames.
- Captions: 115 groups, 32 gold; particles cut.
- Layout: full-face hook → 6 split windows (overview / Haiku / Sonnet / Opus /
  Fable+Mythos→summary 33 s / summary-close) ≈ 67 % split + 2 full-screen AI
  inserts (neural-net @12 s, energy-core @40 s) → 3 beats, "ไม่น่าเบื่อ" (pi-approved).
- Face: 60 % full / 64 % split.
- Known refinement: the Opus slide only lasts ~6 s in top.mp4 but the Opus window
  is ~11 s → the tail of that window drifts to the next slide. Shorten the window
  or freeze the slide if exact sync matters.
