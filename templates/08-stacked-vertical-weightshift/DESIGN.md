# Template 08 — Design Spec

Stacked vertical talking-head with **Weight-Shift** captions.
Same layout as Template 05 — two differences: the caption system (font-weight
travels word-by-word instead of a karaoke box sweep) and the default background
(the **EV Car** brand bg, `assets/bg.png`).

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical)
- Top frame: 1080 × 607.5, border-radius 30 px, gold gradient border 4 px — holds the screen recording
- Bottom frame: 607.5 × 607.5 circle, gold gradient border 4 px — holds the face
- Gap between top and bottom: ~40 px
- Captions: in the band below the bottom circle, `bottom: 360px` (arg 4 of `build-weightshift-captions.py`)

## Caption system — Weight-Shift (caption-weightshift)

Minimal typography where the **font-weight travels word-by-word** in sync with
the speech — no box, no colour fill. Every word renders **light (300)**; at each
word's `start` it tweens to **bold (700)** + a slight scale (`1.0 → 1.08`), then
settles back to 300 as the next word takes over. The emphasis is carried by
weight + scale alone. Generated per job by `scripts/build-weightshift-captions.py`
into `compositions/captions-weightshift.html`.

Adapted from the HyperFrames catalog component
[`caption-weight-shift`](https://hyperframes.heygen.com/catalog/components/caption-weight-shift)
— ported from 1920×1080 / Montserrat / lowercase-English to 1080×1920 /
IBM Plex Sans Thai, and from line-level to **word-level** weight travel so it
syncs to our per-word timing.

### Gold tokens (automatic from `token.gold`)

| Token kind | Weight travel | Colour |
|------------|---------------|--------|
| Normal word | 300 → 700 → 300 as spoken | white `#ffffff` |
| Gold token (number / brand / tech) | 300 → 700 → 300 as spoken | **persistent gold `#f4c20f`** + soft glow |

Gold tokens keep their gold colour for the whole group (not only while spoken),
so keywords always pop. There is **no box** and **no text-colour flip** — unlike
Template 05's karaoke, contrast is never an issue because the caption sits on the
lower-third scrim, not on a coloured fill.

### Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Captions | IBM Plex Sans Thai | 300 (rest) ↔ 700 (spoken word) | 70 px (auto-fit down if a group overflows) |

`line-height: 1.12`. The spoken word also scales to ~1.08 then eases back; the
transition is short (≈ matches the word's spoken span) so the bold "weight" reads
as travelling across the line.

### Grouping

Each group shows 1-3 phrase tokens, ≤32 chars, reads in ~1-2.5 s. Per-token
timing is interpolated inside the group by character weight (the
`caption-groups.json` schema only carries group `start`/`end` + token text+gold).
This is the **same `caption-groups.json`** that feeds Templates 01 (burst) and
05 (karaoke) — switching templates does not require re-running the post-process
subagent.

## Colors (layout)

| Token         | Hex / value                       | Use                         |
| ------------- | --------------------------------- | --------------------------- |
| Frame border  | Gold gradient                     | Top + bottom frame edges    |
| Background    | (from bg.png — EV Car brand)      | brand background            |
| Gold token    | `#f4c20f`                         | persistent gold caption word |

Gold gradient (frame borders): `linear-gradient(180deg, #ffd93d 0%, #f4c20f 50%, #b8860b 100%)`.

## Motion rules

- Top frame inner zoom: slow (1.0 → 1.018 over half the composition, then back to 1.006). Frame shell stays still.
- B-roll inserts (in the top frame): pan slowly, scale 1.006 → 1.022, fade in/out 0.22 s (soft) or 0.26 s (bridge).
- Bottom face: NEVER animate. Static circle. No xfade while visible (lip-sync zero tolerance).
- Captions: per-word weight travel (300 → 700 → 300) + a slight scale on the spoken word; group fades up on enter.

## Audio rules

- Bottom is the master timeline. Top is muted (`data-volume="0"`).
- BGM: 5% gain, never higher. Intent = "barely audible ambient bed".
- BGM mix uses `amix=normalize=0 + alimiter` (never `-shortest` — frame lock rule).

## Layout layers (z-index)

```
z-index 10  captions-weightshift (topmost)
z-index 4   B-roll (inside the top frame, covers the screen recording while active)
z-index 2   video frames (gold borders)
z-index 1   top + bottom media
z-index 0   background
```

## What this template is — and is NOT

**Is:** the Template 05 stacked layout (screen recording on top, face circle on
bottom) with **weight-shift typographic** captions instead of the karaoke box
sweep, on the EV Car brand background.

**Is NOT:**
- Template 05 (same layout, **karaoke** captions — red/gold box word-sweep).
  Pick 05 for punchy CapCut-style karaoke, 08 for the clean premium typographic look.
- Template 01 (same layout, **particle-burst** captions — gold text + dot burst).
- Template 04 (full-screen single talking-head — no top frame, no circle).
- A different aspect, or a no-face / split-screen arrangement → new template.
