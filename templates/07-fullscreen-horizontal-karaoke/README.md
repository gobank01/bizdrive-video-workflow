# Template 07 — Full-screen Horizontal with Karaoke Highlight Captions (YouTube cut)

A **1920×1080 (16:9 horizontal)** talking-head edit for YouTube-style
long-form cuts. The face video fills the whole frame. B-roll inserts also fill
the frame. Captions are BIZDRIVE Karaoke — a coloured box sweeps word-by-word
(red for normal words, gold for brand / number / tech tokens), the same caption
system as Template 04 / 05.

Scaffold a job:

```bash
bash tools/new-job.sh 07 <slug> --raw <raw-slug>
```

## What makes it different

|                  | Template 04 (vertical karaoke) | **Template 07 (horizontal YouTube)** |
| ---------------- | ------------------------------ | ------------------------------------ |
| Aspect           | 9:16 (1080×1920)               | **16:9 (1920×1080)**                 |
| Best for         | Reels / TikTok / Shorts        | **YouTube long-form** (5–30 min)     |
| Caption font     | 70 px                          | **80 px** (TV/desktop readable)      |
| Caption position | bottom 330 px                  | **bottom 120 px**                    |
| B-roll duration  | 3 s                            | **4 s**                              |
| B-roll spacing   | ≥ 6 s                          | **≥ 120 s (~1 per 2 minutes)**       |
| Thumbnail        | default ON                     | **default OFF** (use YouTube's own 1280×720 cover) |

## Source media

ONE video — `bottom.mp4` (talking-head face + master audio) — plus a `bg.png`
fallback. Same shape as Template 02 / 04 (no top.mp4).

## Pipeline

Standard v88 — see [`../_shared/docs/V88_PLAYBOOK.md`](../_shared/docs/V88_PLAYBOOK.md).
Step 11 builds captions with `build-highlight-captions.py` (bottom-px arg = 120
for this template), then `add-broll.py` inserts the long-form B-roll.

## Chunked workflow (long-form, resumable)

T07 ships a chunked variant for 10-30 min cuts where a mistake mid-clip would
otherwise force a full re-edit. **Opt in** via the Job Spec
(`chunked: { on: true, chunkMinutes: 5 }`) or by running the scripts directly.

### How it works

The source `bottom.mp4` is sliced into N time-windowed chunks under
`chunks/<NN>/input/bottom.mp4` (default 5 min each, last chunk shorter). You
run v88 Steps 2–13 **per chunk** — transcribe, polish, caption, render — and
the master state at `<job>/chunks.json` tracks where every chunk stands
(`sliced → transcribed → polished → captioned → composed → rendered`). When
all chunks reach `rendered`, `merge-chunks.py` concatenates them, mixes
BGM/SFX, runs the soft lint, and prepends the thumbnail poster frame.

**If chunk 03 is wrong, only chunk 03 has to be redone.** The others stay rendered.

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/split-chunks.py` | Slice source media + init `chunks.json` (run once) |
| `scripts/chunk-status.py` | Print the status table; or update one chunk's status |
| `scripts/merge-chunks.py` | Concat rendered chunks → mix BGM/SFX → soft lint → prepend thumbnail |

### Commands

```bash
# A. Split (run once, from the job workspace)
python3 scripts/split-chunks.py --minutes 5
python3 scripts/chunk-status.py                 # progress table

# B. For each chunk NN, run v88 Step 2–13 against
#    chunks/<NN>/input/bottom.mp4 + bg.png, render into
#    chunks/<NN>/output/chunk.mp4, then mark progress from the workspace:
python3 scripts/chunk-status.py 01 transcribed
python3 scripts/chunk-status.py 01 polished
python3 scripts/chunk-status.py 01 captioned
python3 scripts/chunk-status.py 01 composed
python3 scripts/chunk-status.py 01 rendered

# C. When every chunk is rendered:
python3 scripts/merge-chunks.py                 # → ../output/finals/<clip>.mp4
```

### Lint mode

Default is **soft** — `npm run check` runs ONCE after merge, and a failure is
reported but not fatal (the merge still ships the MP4). Set
`chunked.lintMode: "strict"` in the Job Spec if you want failures to halt merge.

### Trade-offs

- **Per-chunk B-roll cadence:** the long-form rule (≥120s spacing) still
  applies, so each chunk gets ≤2-3 inserts. Cross-chunk spacing is not
  enforced — pick B-roll moments inside each chunk independently.
- **BGM/SFX mix runs at merge time**, not per chunk, so the music bed is
  continuous across chunk boundaries.
- **Concat seam:** `-c copy` works when every chunk's codec params match
  (libx264, yuv420p, 30 fps, 1920×1080). `merge-chunks.py` falls back to
  re-encode if any differ — slower but seamless.

## Features (Template Manager toggles)

dead-air cut · audio polish · captions · B-roll (long-form) · BGM · SFX ·
thumbnail (default OFF) · **chunked workflow (default OFF)**. Build a Job
Spec for this template with `tools/template-manager.html`.

## Status

🆕 Ready 2026-05-22 — composition authored against the proven Template 04
karaoke pattern, rotated to 16:9 with long-form B-roll cadence. Not yet
render-verified against a real long-form clip; the first job becomes the
reference render.
