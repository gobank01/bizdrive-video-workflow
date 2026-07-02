# Template 11 — frame.md (design / frame spec)

Stacked vertical talking-head with **Weight-Shift** captions.
Same layout as Template 05 — two differences: the caption system (font-weight
travels word-by-word instead of a karaoke box sweep) and the default background
(the **EV Car** brand bg, `assets/bg.png`).

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical, 30fps)
- Primary frame (top): 1080 × 607.5, border-radius 30px, gold gradient border
  4px — holds the screen recording.
- Secondary frame (bottom): 607.5 × 607.5 circle, gold gradient border 4px —
  holds the face. Gap between top and bottom: ~40px.
- Caption band: below the bottom circle, `bottom: 360px` (arg 4 of
  `build-weightshift-captions.py`).

## Colors

Layout tokens + caption colour (no box, no fill — weight carries the emphasis):

| Token         | Hex / value                       | Use                         |
| ------------- | --------------------------------- | --------------------------- |
| Frame border  | gold gradient                     | Top + bottom frame edges    |
| Background    | from `bg.png` (EV Car brand)      | brand background            |
| Caption word  | white `#ffffff`                   | normal word                 |
| Gold token    | persistent `#f4c20f` + soft glow  | number/brand word — gold for the whole group |

Frame gold gradient: `linear-gradient(180deg, #ffd93d 0%, #f4c20f 50%, #b8860b 100%)`.
There is **no box** and **no text-colour flip** (unlike Template 05's karaoke) —
contrast is never an issue because the caption sits on the lower-third scrim.

## Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Captions | IBM Plex Sans Thai | 300 (rest) ↔ 700 (spoken word) | 70 px (auto-fit down if a group overflows) |

`line-height: 1.12`. The spoken word scales to ~1.08 then eases back; the
transition is short (≈ the word's spoken span) so the bold "weight" reads as
travelling across the line.

## Layout layers (z-index)

1. background (0)
2. top + bottom media (1)
3. video frames (2) — gold borders
4. B-roll (4) — inside the top frame, covers the screen recording while active
5. captions-weightshift (10) — topmost

## Caption render rules

**Weight-Shift (caption-weightshift).** Minimal typography where the font-weight
travels word-by-word in sync with speech — no box, no colour fill. Every word
renders **light (300)**; at each word's `start` it tweens to **bold (700)** + a
slight scale (`1.0 → 1.08`), then settles back to 300 as the next word takes
over. Gold tokens keep their gold colour for the whole group (not only while
spoken). Generated per job by `scripts/build-weightshift-captions.py` →
`compositions/captions-weightshift.html`.

Adapted from the HyperFrames catalog component
[`caption-weight-shift`](https://hyperframes.heygen.com/catalog/components/caption-weight-shift)
— ported from 1920×1080 / Montserrat / lowercase-English to 1080×1920 / IBM Plex
Sans Thai, and from line-level to **word-level** weight travel.

Grouping: 1-3 phrase tokens per group, ≤32 chars, ~1-2.5s. Uses the **same
`caption-groups.json`** as Templates 01 (burst) and 05 (karaoke) — switching
templates does not require re-running the post-process subagent.

## Motion rules

- Top frame inner zoom: slow (1.0 → 1.018 over half the composition, then back to
  1.006). Frame shell stays still.
- B-roll inserts (in the top frame): pan slowly, scale 1.006 → 1.022, fade in/out
  0.22s (soft) / 0.26s (bridge).
- Bottom face: NEVER animate. Static circle. No xfade while visible (lip-sync
  zero tolerance).
- Captions: per-word weight travel (300 → 700 → 300) + a slight scale on the
  spoken word; group fades up on enter.

## Audio rules

- Bottom is the master timeline. Top is muted (`data-volume="0"`).
- BGM: 5% gain, never higher — "barely audible ambient bed".
- BGM mix uses `amix=normalize=0 + alimiter` (never `-shortest` — frame lock rule).
- Target -16 LUFS (±2), true peak ≤ -1.5 dBTP.

## What this template is — and is NOT

**Is:** the Template 05 stacked layout (screen recording on top, face circle on
bottom) with **weight-shift typographic** captions instead of the karaoke box
sweep, on the EV Car brand background.

**Is NOT:**
- Template 05 (same layout, **karaoke** captions — red/gold box word-sweep).
  Pick 05 for punchy CapCut karaoke, 08 for the clean premium typographic look.
- Template 01 (same layout, **particle-burst** captions — gold text + dot burst).
- Template 04 (full-screen single talking-head — no top frame, no circle).
- A different aspect, or a no-face / split-screen arrangement → new template.
