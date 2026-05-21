# Template 04 — Design Spec

Full-screen vertical talking-head with **BIZDRIVE Karaoke** captions.
Same layout as Template 02 — the only difference is the caption system.

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical)
- Main video: full-screen — `inset: 0; width: 100%; height: 100%; object-fit: cover`
- B-roll: full-screen, same fill as the main video
- No top frame, no circle crop, no gold border — the video IS the frame

## Caption system — BIZDRIVE Karaoke (caption-highlight)

A coloured box **sweeps word-by-word** in sync with the speech. As each word is
spoken its box scales in from the left (`scaleX 0→1`) and the word pops
(`scale 1.0 → 1.07` then settles). It is generated per job by
`scripts/build-highlight-captions.py` into `compositions/captions-highlight.html`.

### Two-colour box system (automatic)

| Token kind | Box | Text |
|------------|-----|------|
| Normal word | red `linear-gradient(135deg,#ff2d55,#d11138)` | white `#ffffff` |
| Gold token (number / brand / tech) | gold `linear-gradient(135deg,#ffd93d,#f4c20f,#d99a06)` | **dark `#1c1206`** |

Gold tokens come from `token.gold` in `caption-groups.json`. The text flips to
dark **only while the gold box is on** — white-on-gold fails WCAG contrast
(1.65:1), dark-on-gold passes (~10:1). Normal red boxes keep white text.

### Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Captions | IBM Plex Sans Thai | 800 | 70 px (auto-fit down if a group overflows) |

`line-height: 1.12`. Word padding `10px 20px 16px`, box `border-radius: 14px`
with a 1px inner highlight. Strong text-shadow for legibility.

### Grouping

Each group shows 1-3 phrase tokens, ≤32 chars, reads in ~1-2.5 s. Per-token
timing is interpolated inside the group by character weight (the
`caption-groups.json` schema only carries group `start`/`end` + token text+gold).
Position: lower third, `bottom: 330px` (arg 4 of the build script).

## Motion rules

- Main video (`#bottomVideo`): one continuous gentle inner zoom, 1.0 → 1.05
  over the whole composition. `object-fit: cover` so the zoom never reveals edges.
- B-roll: each insert pans slightly (object-position) + zooms 1.02 → 1.06,
  soft 0.22s fade in/out.
- Captions: per-word box sweep + word pop, group fade-up on enter.

## Audio rules

- The single video (`bottomVideo`) carries the master audio but is rendered
  muted (`data-volume="0"`); the polished speech master is muxed back after the
  visual-only render (edit-first architecture).
- BGM: 5% gain, barely-audible bed. Mix with `amix ... normalize=0` so the voice
  keeps its polished level.

## Layout layers (z-index)

```
z-index 10  captions-highlight (topmost)
z-index 9   caption-scrim (lower-third dark gradient — keeps captions readable)
z-index 4   B-roll (full-screen, covers the face video while active)
z-index 1   bottomVideo (full-screen face)
z-index 0   background (fallback)
```

## What this template is — and is NOT

**Is:** a single full-screen talking-head vertical video with karaoke
word-sweep captions and full-screen B-roll cutaways. Input is ONE video.

**Is NOT:**
- Template 02 (same layout, but **particle-burst** captions — gold text + dot
  burst instead of the karaoke box sweep). Pick 02 for a calmer premium feel,
  04 for the punchy CapCut-style karaoke.
- Template 01 (stacked: screen recording on top + face circle on bottom).
- Template 03 (full-screen + floating 16:9 top-insert B-roll card).
