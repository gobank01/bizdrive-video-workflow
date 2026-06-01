# Template 06 — Design Spec

**Screencast with Corner Cam** — `06-screencast-corner-cam`

## Output

1080×1920, 9:16, 30 fps, H.264 / AAC.

## Layout (z-index in parens)

- **Background** (0) — `bg.png`, full-frame fallback, rarely visible.
- **Screen** (1) — `top_visual_master.mp4`, full-screen `object-fit: cover`,
  slow continuous inner zoom 1.0 → 1.04.
- **B-roll** (4) — full-screen `.fullscreen-media broll-frame` inserts: above
  the screen, **below the corner-cam**.
- **Caption scrim** (9) — 760px lower-third dark gradient.
- **Captions** (10) — particle-burst, `.subtitle-cue` at `top: 1490`.
- **Corner-cam** (11) — `bottom_visual_master.mp4` (the face) as a circular PiP:
  - 408×408 px, `border-radius: 50%`, at `left: 56 / top: 84`
  - 5px gold-gradient border + drop shadow (the standard BIZDRIVE gold frame)
  - pops in at 0.12s (`scale 0.84 → 1`, `back.out`), then holds steady
  - **always on top — never hidden, even while B-roll plays**

## The idea

Template 01 splits the frame 50/50 (screen in a framed top half, face in a
bottom circle). Template 06 makes the **screen the hero** — full-bleed — and
shrinks the presenter to a small corner-cam that stays on screen the entire
clip. This is the modern explainer / "let me show you this" look.

## Colors / type

- Gold gradient (border + caption highlight): `#ffec7a → #ffd93d → #f4c20f → #b8860b`
- Caption active `#ffffff` · highlight/gold `#FFD700` · dim `rgba(255,255,255,.45)`
- IBM Plex Sans Thai weight 900, 64px captions.

## Audio

- `bottom` (corner-cam face) = master voice; `top` (screen) is muted.
- Both `data-volume="0"` in the composition — polished speech is muxed on at
  V88_PLAYBOOK Step 14.
- Target -16 LUFS (±2), true peak ≤ -1.5 dBTP. BGM 5%.

## When to use

- ✅ Vertical / phone-screen / app-demo screencasts with a presenter.
- ❌ 16:9 desktop screen captures — `object-fit: cover` crops the sides hard;
  use **Template 01** (16:9 screen shown at native aspect in a framed top half).
- ❌ No screen recording (face only) — use Template 02 / 04.

## Source media

TWO videos, like Template 01/05: `top.mp4` (screen recording) + `bottom.mp4`
(face + master audio), plus `bg.png`. V88_PLAYBOOK Step 7 trims both in
parallel with the same EDL (lip-sync lock).

## Per-job build (V88_PLAYBOOK Step 11)

```bash
python3 scripts/set-duration.py <seconds>
python3 scripts/build-burst-captions.py
python3 scripts/add-broll.py <start1> <start2> ...
```
