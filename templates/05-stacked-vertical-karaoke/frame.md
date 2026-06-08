# Template 05 — frame.md (design / frame spec)

Stacked vertical talking-head with **BIZDRIVE Karaoke** captions.
Same layout as Template 01 — the only difference is the caption system
(Template 01 = particle-burst, Template 05 = karaoke box sweep).

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical, 30fps)
- Primary frame (top): 1080 × 607.5, border-radius 30px, gold gradient border
  4px — holds the screen recording.
- Secondary frame (bottom): 607.5 × 607.5 circle, gold gradient border 4px —
  holds the face. Gap between top and bottom: ~40px.
- Caption band: below the bottom circle, `bottom: 360px` (arg 4 of
  `build-highlight-captions.py`).

## Colors

Layout tokens + the two-colour karaoke box system (automatic from `token.gold`):

| Token         | Hex / value                       | Use                         |
| ------------- | --------------------------------- | --------------------------- |
| Frame border  | gold gradient                     | Top + bottom frame edges    |
| Background    | from `bg.png`                     | BIZDRIVE blue (#0A1640 → #081032) |
| Normal box    | red `#ff2d55 → #d11138`           | active token bg, white text |
| Gold box      | `#ffd93d → #f4c20f → #d99a06`     | number/brand token, **dark `#1c1206`** text |

Frame gold gradient: `linear-gradient(180deg, #ffd93d 0%, #f4c20f 50%, #b8860b 100%)`.
Text flips to dark **only while the gold box is on** — white-on-gold fails WCAG
(1.65:1), dark-on-gold passes (~10:1). This flip is load-bearing.

## Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Captions | IBM Plex Sans Thai | 800 | 70 px (auto-fit down if a group overflows) |

`line-height: 1.12`. Word padding `10px 20px 16px`, box `border-radius: 14px`.

## Layout layers (z-index)

1. background (0)
2. top + bottom media (1)
3. video frames (2) — gold borders
4. B-roll (4) — inside the top frame, covers the screen recording while active
5. captions-highlight (10) — topmost

## Caption render rules

**BIZDRIVE Karaoke (caption-highlight).** A coloured box sweeps word-by-word in
sync with speech: each word's box scales in from the left (`scaleX 0→1`,
transform-origin left) and the word pops (`scale 1.0 → 1.07` then settles).
Generated per job by `scripts/build-highlight-captions.py` →
`compositions/captions-highlight.html`.

Grouping: 1-3 phrase tokens per group, ≤32 chars, reads in ~1-2.5s. Per-token
timing interpolated inside the group by character weight (the `caption-groups.json`
schema carries group `start`/`end` + token text+gold).

## Motion rules

- Top frame inner zoom: slow (1.0 → 1.018 over half the composition, then back to
  1.006). Frame shell stays still.
- B-roll inserts (in the top frame): pan slowly, scale 1.006 → 1.022, fade in/out
  0.22s (soft) / 0.26s (bridge).
- Bottom face: NEVER animate. Static circle. No xfade while visible (lip-sync
  zero tolerance).
- Captions: per-word box sweep + word pop; group fades up on enter.

## Audio rules

- Bottom is the master timeline. Top is muted (`data-volume="0"`).
- BGM: 5% gain, never higher — "barely audible ambient bed".
- BGM mix uses `amix=normalize=0 + alimiter` (never `-shortest` — frame lock rule).
- Target -16 LUFS (±2), true peak ≤ -1.5 dBTP.

## What this template is — and is NOT

**Is:** the Template 01 stacked layout (screen recording on top, face circle on
bottom) with karaoke word-sweep captions instead of particle-burst.

**Is NOT:**
- Template 01 (same layout, **particle-burst** captions — gold text + dot burst).
  Pick 01 for a calmer premium feel, 05 for punchy CapCut-style karaoke.
- Template 04 (full-screen single talking-head + karaoke — no top frame, no circle).
- A different aspect, or a no-face / split-screen arrangement → new template.
