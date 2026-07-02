# Template 10 — Multi-mode Vertical (Full + Split) + Blue Word-Sweep

Single-presenter 9:16 talking-head that **cuts between two display states** over
one full-screen face master, with clean **white + blue** centered captions.
Modelled on the Top1% / อาจารย์อริน reference screenshots.

## Output
- 1080 × 1920, 9:16, 30 fps, h264 / aac 48k / 192k
- One input: `bottom_visual_master.mp4` (the face) = audio master. B-roll inserts are muted.
- **Locked v88 pipeline unchanged** — the layout switch is a per-insert B-roll display mode, not a pipeline change.

## Display states (driven per insert by `scripts/add-broll.py`)
| Mode | Geometry | Face |
|------|----------|------|
| `full` | B-roll fills 1080×1920, z 4 | hidden behind B-roll |
| `split-top` | B-roll top half: `left 0 / top 0 / 1080×960`, object-fit cover, object-position 50% 45% | animates DOWN to bottom rectangle `top 960 / height 960`, object-position 50% 30%, reverts when insert ends |

- Split is **full-bleed 50/50, no frames** — the caption sits on the seam (≈ y960).
- Face box moves spatially only (top/height/object-position); playback timing is never
  touched, so **lip-sync is preserved**. The gentle inner-zoom (scale 1.0→1.05) runs throughout.
- `mixed` (default) alternates split-top → full so a clip naturally cuts between layouts.

## Captions — BIZDRIVE Blue Word-Sweep (`compositions/captions-sweep.html`)
- Built by `scripts/build-sweep-captions.py` from `caption-groups.json` (same schema as T04/T09).
- Every word **solid white** from the moment the group appears. The spoken word pops to
  **blue `#2EA8FF`** with a small scale bump, then settles back to white → exactly one blue word at a time.
- **No coloured box, no particles, no backing pill** — bare bold text + heavy shadow for legibility.
- Font: IBM Plex Sans Thai 900, 100px. Centered, `bottom: 910px` (over the seam in split, mid-low over the face otherwise).
- `gold` token flag (numbers/brand/tech) only adds a slightly stronger pop; active colour is always blue.
- Blue value is tunable — edit `BLUE` in `build-sweep-captions.py` and `colors.active` in `manifest.json`.

## Audio / BGM / SFX
- Same as Template 04: polish chain to −16 LUFS (tol −18…−14), true-peak −1.5; BGM 5% ambient bed; ≤5 context-matched SFX (whoosh on layout switches).

## Per-job build (V88_PLAYBOOK Step 11)
```bash
python3 scripts/set-duration.py <seconds>
python3 scripts/add-broll.py 14:split 30:full 52:split         # or: --display mixed 14 30 52
python3 scripts/build-sweep-captions.py assets/intermediates/transcript/caption-groups.json compositions/captions-sweep.html <seconds> 910
```

## Status
Created 2026-06-24. No golden-reference clip yet — validate + lock on the first
purpose-built clip (lint 0/0, final.mp4 −16 LUFS, captions centered, split face framed on the head).
