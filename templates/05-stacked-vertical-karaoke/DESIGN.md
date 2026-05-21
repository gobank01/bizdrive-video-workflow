# Template 05 — Design Spec

Stacked vertical talking-head with **BIZDRIVE Karaoke** captions.
Same layout as Template 01 — the only difference is the caption system
(Template 01 = particle-burst, Template 05 = karaoke box sweep).

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical)
- Top frame: 1080 × 607.5, border-radius 30 px, gold gradient border 4 px — holds the screen recording
- Bottom frame: 607.5 × 607.5 circle, gold gradient border 4 px — holds the face
- Gap between top and bottom: ~40 px
- Captions: in the band below the bottom circle, `bottom: 360px` (arg 4 of `build-highlight-captions.py`)

## Caption system — BIZDRIVE Karaoke (caption-highlight)

A coloured box **sweeps word-by-word** in sync with the speech. As each word is
spoken its box scales in from the left (`scaleX 0→1`, transform-origin left) and
the word pops (`scale 1.0 → 1.07` then settles). Generated per job by
`scripts/build-highlight-captions.py` into `compositions/captions-highlight.html`.

### Two-colour box system (automatic from `token.gold`)

| Token kind | Box | Text |
|------------|-----|------|
| Normal word | red `linear-gradient(135deg,#ff2d55,#d11138)` | white `#ffffff` |
| Gold token (number / brand / tech) | gold `linear-gradient(135deg,#ffd93d,#f4c20f,#d99a06)` | **dark `#1c1206`** |

The text flips to dark **only while the gold box is on** — white-on-gold fails
WCAG contrast (1.65:1), dark-on-gold passes (~10:1). This flip is load-bearing.

### Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Captions | IBM Plex Sans Thai | 800 | 70 px (auto-fit down if a group overflows) |

`line-height: 1.12`. Word padding `10px 20px 16px`, box `border-radius: 14px`.

### Grouping

Each group shows 1-3 phrase tokens, ≤32 chars, reads in ~1-2.5 s. Per-token
timing is interpolated inside the group by character weight (the
`caption-groups.json` schema only carries group `start`/`end` + token text+gold).

## Colors (layout)

| Token         | Hex / value                       | Use                         |
| ------------- | --------------------------------- | --------------------------- |
| Frame border  | Gold gradient                     | Top + bottom frame edges    |
| Background    | (from bg.png)                     | BIZDRIVE blue (#0A1640 → #081032) |

Gold gradient (frame borders): `linear-gradient(180deg, #ffd93d 0%, #f4c20f 50%, #b8860b 100%)`.

## Motion rules

- Top frame inner zoom: slow (1.0 → 1.018 over half the composition, then back to 1.006). Frame shell stays still.
- B-roll inserts (in the top frame): pan slowly, scale 1.006 → 1.022, fade in/out 0.22 s (soft) or 0.26 s (bridge).
- Bottom face: NEVER animate. Static circle. No xfade while visible (lip-sync zero tolerance).
- Captions: per-word box sweep + word pop; group fades up on enter.

## Audio rules

- Bottom is the master timeline. Top is muted (`data-volume="0"`).
- BGM: 5% gain, never higher. Intent = "barely audible ambient bed".
- BGM mix uses `amix=normalize=0 + alimiter` (never `-shortest` — frame lock rule).

## Layout layers (z-index)

```
z-index 10  captions-highlight (topmost)
z-index 4   B-roll (inside the top frame, covers the screen recording while active)
z-index 2   video frames (gold borders)
z-index 1   top + bottom media
z-index 0   background
```

## What this template is — and is NOT

**Is:** the Template 01 stacked layout (screen recording on top, face circle on
bottom) with karaoke word-sweep captions instead of particle-burst.

**Is NOT:**
- Template 01 (same layout, **particle-burst** captions — gold text + dot burst).
  Pick 01 for a calmer premium feel, 05 for punchy CapCut-style karaoke.
- Template 04 (full-screen single talking-head + karaoke — no top frame, no circle).
- A different aspect, or a no-face / split-screen arrangement → new template.
