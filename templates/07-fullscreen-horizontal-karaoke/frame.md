# Template 07 — frame.md (design / frame spec)

**Full-screen Horizontal with Karaoke Highlight Captions (YouTube cut)** — `07-fullscreen-horizontal-karaoke`

## Aspect / dimensions

- Canvas: 1920 × 1080 (16:9 horizontal, 30fps), H.264 / AAC. YouTube-native.
- Primary frame (the hero): `bottom_visual_master.mp4` face, full-screen
  `object-fit: cover`, slow continuous inner zoom 1.0 → 1.04.
- Secondary frame: none (single source). Full-screen B-roll inserts replace the
  face temporarily.
- Caption band: captions sit at `bottom: 120px`, over a 400px lower-third scrim
  (T04/T05 use 760 on a 1920-tall frame; 400 scales to the 1080-tall frame).

## Colors

| Token             | Hex / value                          | Use                       |
| ----------------- | ------------------------------------ | ------------------------- |
| Caption text      | `#ffffff` (→ `#1c1206` over gold box)| Readable token (WCAG)     |
| Normal box        | `#ff2d55 → #d11138` (red gradient)   | Active token background   |
| Gold box          | `#ffd93d → #f4c20f → #d99a06`        | Highlighted token (numbers, brands) |
| Background        | from `bg.png`                        | full-frame fallback       |

## Typography

| Element     | Font family           | Weight | Size  |
| ----------- | --------------------- | ------ | ----- |
| Captions    | IBM Plex Sans Thai    | 800    | 80 px (bigger than T04/T05's 70px for desktop) |

## Layout layers (z-index)

1. Background (0) — `bg.png`, full-frame fallback, rarely visible.
2. Face video (1) — `bottom_visual_master.mp4`, full-screen, slow inner zoom.
3. B-roll (4) — full-screen `.fullscreen-media broll-frame` inserts.
4. Caption scrim (9) — 400px lower-third dark gradient.
5. Captions (10) — caption-highlight karaoke, mounted `data-width=1920
   data-height=1080`, at `bottom: 120px`.

## Caption render rules

caption-highlight karaoke (same as T04/T05). Each token gets a colored box;
gold box for numbers/brands (text flips to dark for WCAG contrast).

## Motion rules

- Face: slow continuous inner zoom 1.0 → 1.04 (the only background motion).
- B-roll inserts: long-form cadence (see Audio/B-roll below).
- Seek-driven; nothing loops independently of the master timeline.

## Audio rules

- `bottom` (face) = master voice. No `top` track.
- `data-volume="0"` in the composition; polished speech is muxed at V88_PLAYBOOK Step 14.
- Target -16 LUFS (±2), true peak ≤ -1.5 dBTP. BGM 5%.

**B-roll cadence (long-form, differs from 9:16 templates):**

| | 9:16 (T01–T06) | **T07 (16:9 long-form)** |
| --- | --- | --- |
| Duration each | 3 s | **4 s** |
| Min spacing | 6 s | **120 s** (~1 per 2 minutes) |
| Hard cap | 4 per 60 s | **No hard cap** (10-min ≈ 5, 20-min ≈ 10) |
| Aspect generated | 9:16 | **16:9** |

`add-broll.py`: `BROLL_DURATION = 4`, `MIN_SPACING = 120`. `generate-broll.js`
uses `aspect_ratio: "16:9"`.

## What this template is — and is NOT

The horizontal cousin of Template 04 — fullscreen face + fullscreen B-roll +
karaoke, rotated to 16:9 for YouTube long-form.

- ✅ YouTube long-form talking-head (5–30 min); desktop/TV-first.
- ❌ Reels / TikTok / Shorts — use T01–T06 (9:16 vertical).
- ❌ Multi-source (face + screen) — use T01 (stacked) or T06 (corner-cam).

Source media: ONE video — `bottom.mp4` (face + master audio) + `bg.png`. Same
shape as T02/T04 (no `top.mp4`). V88_PLAYBOOK Step 7 trims bottom only.

**Thumbnail — default OFF:** `build-thumbnail.py` is hardcoded for the 9:16
cover (1080×1920). For YouTube prefer a separate 1280×720 cover.
`features.thumbnail.default = false`; turning it on via Job Spec yields a
vertical thumbnail until the script grows a horizontal mode.

Per-job build (V88_PLAYBOOK Step 11):

```bash
python3 scripts/set-duration.py <seconds>
python3 scripts/build-highlight-captions.py assets/intermediates/transcript/caption-groups.json compositions/captions-highlight.html <seconds> 120
python3 scripts/add-broll.py <start1> <start2> ...     # ≥120s apart, 4s each
```
