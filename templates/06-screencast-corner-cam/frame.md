# Template 06 — frame.md (design / frame spec)

**Screencast with Corner Cam** — `06-screencast-corner-cam`

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16, 30fps), H.264 / AAC.
- Primary frame (the hero): the screen recording, full-bleed `object-fit: cover`,
  slow continuous inner zoom 1.0 → 1.04.
- Secondary frame: circular corner-cam (the face) — 408 × 408 px,
  `border-radius: 50%`, at `left: 56 / top: 84`, 5px gold-gradient border +
  drop shadow. Pops in at 0.12s (`scale 0.84 → 1`, `back.out`), then holds.
- Caption band: `.subtitle-cue` at `top: 1490`, over a 760px lower-third scrim.

## Colors

| Token             | Hex / value                  | Use                            |
| ----------------- | ---------------------------- | ------------------------------ |
| Caption active    | `#ffffff`                    | Token currently being spoken   |
| Caption highlight | `#FFD700`                    | Highlighted token              |
| Caption dim       | `rgba(255,255,255,0.45)`     | Token not yet spoken           |
| Frame border      | gold gradient                | Corner-cam ring                |
| Background        | from `bg.png`                | full-frame fallback, rarely visible |

Gold gradient (corner-cam border + caption highlight): `#ffec7a → #ffd93d → #f4c20f → #b8860b`.

## Typography

| Element     | Font family           | Weight | Size  |
| ----------- | --------------------- | ------ | ----- |
| Captions    | IBM Plex Sans Thai    | 900    | 64 px |

## Layout layers (z-index)

1. Background (0) — `bg.png`, full-frame fallback, rarely visible.
2. Screen (1) — `top_visual_master.mp4`, full-screen, slow inner zoom.
3. B-roll (4) — full-screen `.fullscreen-media broll-frame` inserts: above the
   screen, below the corner-cam.
4. Caption scrim (9) — 760px lower-third dark gradient.
5. Captions (10) — particle-burst, `.subtitle-cue` at `top: 1490`.
6. Corner-cam (11) — circular PiP face, **always on top — never hidden, even
   while B-roll plays**.

## Caption render rules

Particle-burst captions (same system as Template 01). Gold-highlight numbers /
brands. Captions sit in the lower third over the scrim.

## Motion rules

- Screen: slow continuous inner zoom 1.0 → 1.04 (the only background motion).
- Corner-cam: one pop-in at 0.12s (`scale 0.84 → 1`, `back.out`), then steady.
- Everything seek-driven; nothing loops independently of the master timeline.

## Audio rules

- `bottom` (corner-cam face) = master voice; `top` (screen) is muted.
- Both `data-volume="0"` in the composition — polished speech is muxed on at
  V88_PLAYBOOK Step 14.
- Target -16 LUFS (±2), true peak ≤ -1.5 dBTP. BGM 5%.

## What this template is — and is NOT

The screen is the HERO (full-bleed); the presenter shrinks to a corner-cam that
stays on the entire clip — the modern explainer / "let me show you this" look.

- ✅ Vertical / phone-screen / app-demo screencasts with a presenter.
- ❌ 16:9 desktop screen captures — `object-fit: cover` crops the sides hard;
  use **Template 01** (16:9 screen at native aspect in a framed top half).
- ❌ No screen recording (face only) — use Template 02 / 04.

Source media: TWO videos like Template 01/05 — `top.mp4` (screen) + `bottom.mp4`
(face + master audio) + `bg.png`. V88_PLAYBOOK Step 7 trims both in parallel with
the same EDL (lip-sync lock).

Per-job build (V88_PLAYBOOK Step 11):

```bash
python3 scripts/set-duration.py <seconds>
python3 scripts/build-burst-captions.py
python3 scripts/add-broll.py <start1> <start2> ...
```
