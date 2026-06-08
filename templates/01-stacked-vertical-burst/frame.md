# Template 01 — Design Spec

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical)
- Top frame: 1080 × 607.5, border-radius 30 px, gold gradient border 4 px
- Bottom frame: 607.5 × 607.5 circle, gold gradient border 4 px
- Gap between top and bottom: ~40 px
- Captions: positioned above bottom circle at `bottom: 360px`

## Colors

| Token             | Hex / value                  | Use                            |
| ----------------- | ---------------------------- | ------------------------------ |
| Caption active    | `#ffffff`                    | Token currently being spoken   |
| Caption gold      | `#FFD700`                    | Highlighted token (numbers, brands) — also particle burst color |
| Caption dim       | `rgba(255,255,255,0.45)`     | Token not yet spoken (or after)|
| Frame border      | Gold gradient                | Top + bottom frame edges       |
| Background        | (from bg.png)                | BIZDRIVE blue (#0A1640 → #081032) |
| Caption shadow    | `0 4px 16px rgba(0,0,0,.85), 0 0 28px rgba(0,0,0,.7)` | Readability on busy bg |

Gold gradient (for frame borders): `linear-gradient(180deg, #ffd93d 0%, #f4c20f 50%, #b8860b 100%)`.

Particle burst colors (10 dots per gold token): `#FFD700, #FFC233, #FFD86A, #FFE48E, #ffffff, #FFD700, #FFC233, #FFD86A` (cycled by index).

## Typography

| Element     | Font family           | Weight | Size  |
| ----------- | --------------------- | ------ | ----- |
| Captions    | IBM Plex Sans Thai    | 900    | 64 px |
| (Fallback)  | Inter                 | 900    | -     |

`letter-spacing: 0.01em`, `line-height: 1.1`.

## Layout layers (z-index)

1. background (0) — from `bg.png`
2. top + bottom media (1) — screen recording + face
3. video frames (2) — gold borders (top rounded rect + bottom circle)
4. B-roll (4) — inside the top frame, covers the screen recording while active
5. captions-burst (10) — topmost (particle-burst captions)

## Caption render rules

1. Each caption GROUP holds 1-3 tokens displayed on screen simultaneously.
2. Group container fades + scales in at `group.start` (back.out(1.6), 0.22 s).
3. Tokens reveal sequentially within the group — proportional to character length.
4. Active token: color shifts to white (or gold if highlighted), scale 1.03 (or 1.10 if gold). Returns to scale 1.0 after a brief held window.
5. Gold tokens fire particle burst (10 dots, mulberry32-seeded angles for determinism, 90-250 px radius, varying sizes 4-12 px, easing power3.out).
6. Group fades out 0.20 s before `group.end` (power2.in).
7. Caption gold spacing: any highlighted token MUST be visually separated from adjacent normal text — e.g. `A B C` not `ABC` with B highlighted. Validated via `npm run check:caption-gold`.

## Motion rules

- Top frame inner zoom: slow (1.0 → 1.018 over half the composition, then back to 1.006). Frame shell stays still.
- B-roll inserts: pan slowly (50% 51% → 50% 49% or similar), scale 1.006 → 1.022, fade in 0.22 s / fade out 0.22 s (soft) or 0.26 s (bridge).
- Bottom face: NEVER animate. Static circle. No xfade while visible (lip-sync zero tolerance, see MISTAKES.md v68/v69).

## Audio rules

- Bottom is the master timeline. Top is muted (data-volume="0").
- BGM: 5% gain, never higher. Intent = "barely audible ambient bed", not noticeable song.
- BGM mix uses `amix=normalize=0 + alimiter` (never `-shortest` — frame lock rule).

## What this template is — and is NOT

This template is the **brand layout**. It is not:

- A different aspect (1920×1080, 1080×1080) → make Template 02/03
- A different caption animation style (karaoke, slam, scatter, 3D) → still 01 if layout matches, but document in frame.md as a variant
- A different speaker arrangement (split-screen, PiP overlay, no face) → new template
