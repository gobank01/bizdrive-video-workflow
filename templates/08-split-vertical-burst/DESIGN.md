# Template 08 — Design Spec (Split Vertical · Rectangle · Karaoke Highlight Centered)

Layout cousin of Template 01/05 (stacked top/bottom), but the bottom person is a
full-width **rectangle (no circle crop)** — a clean top/bottom split — and the
**BIZDRIVE Karaoke captions (caption-highlight word-sweep)** sit **centered over
the seam**. Caption system is identical to Template 04/05
(`scripts/build-highlight-captions.py`): a coloured box sweeps in word-by-word —
**red box** for normal words, **gold box** for brand / number / tech tokens.

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical)
- **Top frame (screen / top.mp4):** left 0, top 40, 1080 × 900, border-radius 30 px, gold gradient border 4 px
- **Bottom frame (person / bottom.mp4):** left 0, top 980, 1080 × 900 **rectangle**, border-radius 30 px, gold gradient border 4 px, `object-fit: cover` (NO circle)
- Seam: 40 px gap at y = 960 (frame edges 940 / 980)
- **Captions: caption-highlight karaoke, centered over the seam at `bottom: 910px`** (`.hl-group` in `scripts/build-highlight-captions.py`, where `bottom` is `argv[4]`). In `tools/v88-clip.sh` T08 → `build-highlight-captions.py` + `CAPTION_BOTTOM=910`.
- ⚠️ Because captions sit over video (not the bg margin), expect occasional WCAG-contrast warnings on bright frames — the dark text-shadow carries readability; add a backing strip if a clip is very bright.

## Colors

| Token             | Hex / value                  | Use                            |
| ----------------- | ---------------------------- | ------------------------------ |
| Caption word text | `#ffffff`                    | Word text (all words)          |
| Normal word box   | `linear-gradient(135deg, #ff2d55 0%, #d11138 100%)` | Red box that sweeps behind a normal word as it is spoken |
| Gold word box     | `linear-gradient(135deg, #ffd93d 0%, #f4c20f 55%, #d99a06 100%)` | Gold box for highlighted tokens (numbers, brands, tech) |
| Gold word text    | `#1c1206`                    | Word text flips dark while the gold box is active (contrast) |
| Frame border      | Gold gradient                | Top + bottom frame edges       |
| Background        | (from bg.png)                | BIZDRIVE blue (#0A1640 → #081032) |
| Caption shadow    | `0 4px 16px rgba(0,0,0,.55), 0 2px 5px rgba(0,0,0,.6)` | Word readability on busy bg |

Gold gradient (for frame borders): `linear-gradient(180deg, #ffd93d 0%, #f4c20f 50%, #b8860b 100%)`.

## Typography

| Element     | Font family           | Weight | Size                          |
| ----------- | --------------------- | ------ | ----------------------------- |
| Captions    | IBM Plex Sans Thai    | 800    | 70 px (auto-shrinks to fit)   |

`line-height: 1.12`. Each group auto-fits its font size down to ~60% if the
joined text would exceed the 1820 px usable width.

## Caption render rules

1. Each caption GROUP is rendered as wrapped word boxes (flex-wrap) — one box per word.
2. Group container fades up (`opacity 0→1`, `y 24→0`, 0.18 s, power3.out) at `group.start`.
3. As each word is spoken, its coloured box sweeps in from the left (`scaleX 0→1`, 0.16 s, power3.out) and the word pops (`scale →1.07` then settles to 1.0).
4. Normal word = red box; gold token = gold box, with the word text flipping to `#1c1206` while the gold box is active for contrast.
5. Each box exits with a slight overshoot (`scaleX →1.03`, fade out) as the word ends.
6. Group fades out 0.14 s before `group.end` (power2.in).
7. Caption gold spacing: any highlighted token MUST be visually separated from adjacent normal text — e.g. `A B C` not `ABC` with B highlighted. Validated via `npm run check:caption-gold`.

## Motion rules

- Top frame inner zoom: slow (1.0 → 1.018 over half the composition, then back to 1.006). Frame shell stays still.
- B-roll inserts: pan slowly (50% 51% → 50% 49% or similar), scale 1.006 → 1.022, fade in 0.22 s / fade out 0.22 s (soft) or 0.26 s (bridge).
- Bottom face: NEVER animate. Static circle. No xfade while visible (lip-sync zero tolerance, see MISTAKES.md v68/v69).

## Audio rules

- Bottom is the master timeline. Top is muted (data-volume="0").
- BGM: 5% gain, never higher. Intent = "barely audible ambient bed", not noticeable song.
- BGM mix uses `amix=normalize=0 + alimiter` (never `-shortest` — frame lock rule).

## What this design is NOT

This template is the **brand layout**. It is not:

- A different aspect (1920×1080, 1080×1080) → make Template 02/03
- A different caption animation style (karaoke, slam, scatter, 3D) → still 01 if layout matches, but document in DESIGN.md as a variant
- A different speaker arrangement (split-screen, PiP overlay, no face) → new template
