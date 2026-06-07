# Template 03 — Design Spec

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical)
- Main video: full-screen — `inset: 0; width: 100%; height: 100%; object-fit: cover`
- B-roll: a floating **16:9 insert card** — `984 × 554 px`, `left: 48px`,
  `top: 24px`, `border-radius: 30px`, `border: 4px solid #f4c20f`
- No top frame, no circle crop — the face video IS the frame; the insert
  floats near the top of the frame while active

## Colors

| Token | Hex / value | Use |
|-------|-------------|-----|
| Caption active | `#ffffff` | Token currently being spoken |
| Caption gold | `#FFD700` | Highlighted token + particle burst |
| Caption dim | `rgba(255,255,255,0.45)` | Token not yet spoken |
| Background | (from bg.png) | Fallback only — rarely visible |
| Insert border | `#f4c20f` (gold) | 4px frame around the B-roll card |
| Insert shadow | `0 28px 64px rgba(0,0,0,.62)` | Lifts the card off the face video |
| Caption shadow | `0 4px 16px rgba(0,0,0,.85), 0 0 28px rgba(0,0,0,.7)` | Readability over the video |

Particle burst colors (10 dots per gold token): `#FFD700, #FFC233, #FFD86A, #FFE48E, #ffffff` cycled.

## Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Captions | IBM Plex Sans Thai | 900 | 64 px |

`letter-spacing: 0.01em`, `line-height: 1.1`. Same as Template 01 / 02.

## Layout layers (z-index)

1. background (0) — fallback
2. bottomVideo (1) — full-screen face
3. B-roll top-insert card (5) — near the top, over the face video
4. caption scrim (9) — lower-third gradient
5. captions (10) — topmost

**The top-insert card** (the distinctive frame of this template): a 16:9 rounded
card, `984 × 554 px`, centred horizontally (48px side margins), `top: 24px` —
near the top of the frame, clear of the captions and the speaker's face below.
4px gold border + soft drop shadow so it reads as a distinct overlay card. B-roll
fills it with `object-fit: cover`; clips are generated at **16:9** so there is no
letterboxing inside the card. The card only exists while a B-roll clip is active —
between clips the frame is just the full-screen face video.

## Caption render rules

Identical to Template 01 / 02 — the `captions-burst.html` sub-composition is
shared. Each cue is a `bs-group` of 1-3 tokens, positioned `bottom: 360px`
(lower third). Tokens reveal sequentially; gold tokens fire a 10-dot particle
burst.

Captions sit on top of everything (`#captions-mount` z-index 10), so they stay
readable over the face video and never collide with the upper-third insert.

## Motion rules

- Main video (`#bottomVideo`): one continuous gentle inner zoom, 1.0 → 1.05
  over the whole composition. `object-fit: cover` so the zoom never reveals edges.
- B-roll insert: the card **pops in** (scale 0.9 → 1 + fade, `back.out`), its
  inner footage pans slightly (object-position) while live, then it **pops out**
  (scale 1 → 0.94 + fade). Soft 0.26s transitions.
- The card box stays anchored — only the footage inside drifts; the box itself
  is never panned across the frame.

## Audio rules

- The single video (`bottomVideo`) carries the master audio but is rendered
  muted (`data-volume="0"`); the polished speech master is muxed back after the
  visual-only render (edit-first architecture).
- BGM: 5% gain, barely-audible bed.

## What this template is — and is NOT

**Is:** a single full-screen talking-head vertical video with kinetic captions
and B-roll shown in a floating 16:9 card above the speaker. Input is ONE video
(the person).

**Is NOT:**
- Template 02 (full-screen B-roll covering the whole frame) — use 02 when the
  B-roll should take over the screen.
- Template 01 (stacked: screen recording on top + face circle on bottom) — use
  01 when there's a screen recording to show the whole clip.
- A horizontal / square format — that would be Template 04+.
