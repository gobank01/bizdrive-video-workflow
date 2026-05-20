# Template 02 — Design Spec

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical)
- Main video: full-screen — `inset: 0; width: 100%; height: 100%; object-fit: cover`
- B-roll: full-screen, same fill as the main video
- No top frame, no circle crop, no gold border — the video IS the frame

## Colors

| Token | Hex / value | Use |
|-------|-------------|-----|
| Caption active | `#ffffff` | Token currently being spoken |
| Caption gold | `#FFD700` | Highlighted token + particle burst |
| Caption dim | `rgba(255,255,255,0.45)` | Token not yet spoken |
| Background | (from bg.png) | Fallback only — rarely visible |
| Caption shadow | `0 4px 16px rgba(0,0,0,.85), 0 0 28px rgba(0,0,0,.7)` | Readability over the video |

Particle burst colors (10 dots per gold token): `#FFD700, #FFC233, #FFD86A, #FFE48E, #ffffff` cycled.

## Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Captions | IBM Plex Sans Thai | 900 | 64 px |

`letter-spacing: 0.01em`, `line-height: 1.1`. Same as Template 01.

## Caption render rules

Identical to Template 01 — the `captions-burst.html` sub-composition is shared.
Each cue is a `bs-group` of 1-3 tokens, positioned `bottom: 360px` (lower third).
Tokens reveal sequentially; gold tokens fire a 10-dot particle burst.

Captions sit on top of everything (`#captions-mount` z-index 10), so they stay
readable over both the face video and full-screen B-roll.

## Motion rules

- Main video (`#bottomVideo`): one continuous gentle inner zoom, 1.0 → 1.05
  over the whole composition. `object-fit: cover` so the zoom never reveals edges.
- B-roll: each insert pans slightly (object-position) + zooms 1.02 → 1.06,
  soft 0.22s fade in/out.
- No frame shell to keep still — the whole canvas is the video.

## Audio rules

- The single video (`bottomVideo`) carries the master audio but is rendered
  muted (`data-volume="0"`); the polished speech master is muxed back after the
  visual-only render (edit-first architecture).
- BGM: 5% gain, barely-audible bed.

## Layout layers (z-index)

```
z-index 10  captions (topmost)
z-index 4   B-roll (full-screen, covers the face video while active)
z-index 1   bottomVideo (full-screen face)
z-index 0   background (fallback)
```

## What this template is — and is NOT

**Is:** a single full-screen talking-head vertical video with kinetic captions
and full-screen B-roll cutaways. Input is ONE video (the person).

**Is NOT:**
- Template 01 (stacked: screen recording on top + face circle on bottom) — use 01
  when there's a screen recording to show.
- A horizontal / square format — that would be Template 03+.
