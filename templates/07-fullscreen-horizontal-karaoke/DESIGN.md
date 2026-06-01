# Template 07 — Design Spec

**Full-screen Horizontal with Karaoke Highlight Captions (YouTube cut)** — `07-fullscreen-horizontal-karaoke`

## Output

1920×1080, 16:9 horizontal, 30 fps, H.264 / AAC. YouTube-native dimensions.

## Layout (z-index in parens)

- **Background** (0) — `bg.png`, full-frame fallback, rarely visible.
- **Face video** (1) — `bottom_visual_master.mp4`, full-screen `object-fit: cover`,
  slow continuous inner zoom 1.0 → 1.04.
- **B-roll** (4) — full-screen `.fullscreen-media broll-frame` inserts.
- **Caption scrim** (9) — lower-third dark gradient, **400px tall** (T04/T05 use
  760 on a 1920-tall frame; the 400px scales proportionally to a 1080-tall frame).
- **Captions** (10) — caption-highlight karaoke, mounted with
  `data-width=1920 data-height=1080`, captions sit at **bottom: 120px**.

## The idea

The horizontal cousin of Template 04. Same fullscreen-face + fullscreen-B-roll
+ karaoke layout, but rotated to **16:9** for YouTube long-form. B-roll cadence
is long-form (≥120s spacing, 4s inserts) instead of the 9:16 sparse-4/60s rule.

## Colors / type

Same BIZDRIVE karaoke palette as T04/T05:
- Text `#ffffff` (flips to `#1c1206` while a gold box is active — WCAG)
- Normal box: linear-gradient `#ff2d55 → #d11138` (red)
- Gold box: linear-gradient `#ffd93d → #f4c20f → #d99a06`
- IBM Plex Sans Thai 800, **80px** (slightly bigger than T04/T05's 70px for
  horizontal/desktop readability).

## Audio

- `bottom` (face) = master voice. No `top` track.
- `data-volume="0"` in the composition; polished speech is muxed at V88_PLAYBOOK Step 14.
- Target -16 LUFS (±2), true peak ≤ -1.5 dBTP. BGM 5%.

## B-roll — long-form rules

Different from the 9:16 templates:

| | 9:16 (T01–T06) | **T07 (16:9 long-form)** |
| --- | --- | --- |
| Duration each | 3 s | **4 s** |
| Min spacing | 6 s | **120 s** (~1 per 2 minutes) |
| Hard cap | 4 per 60 s of final video | **No hard cap** — depends on length (10-min cut ≈ 5, 20-min ≈ 10) |
| Aspect generated | 9:16 | **16:9** |

`add-broll.py` constants are `BROLL_DURATION = 4` and `MIN_SPACING = 120`.
`generate-broll.js` uses `aspect_ratio: "16:9"`.

## When to use

- ✅ YouTube long-form talking-head (5–30 min)
- ✅ Desktop/TV-first content
- ❌ Reels / TikTok / Shorts — use T01–T06 (9:16 vertical)
- ❌ Multi-source (face + screen) — use T01 (vertical stacked) or T06 (corner-cam)

## Source media

ONE video — `bottom.mp4` (talking-head face + master audio) — plus `bg.png`
fallback. Same shape as T02/T04 (no top.mp4). V88_PLAYBOOK Step 7 trims bottom
only — skip the parallel top trim.

## Thumbnail — default OFF

The shared `build-thumbnail.py` is currently hardcoded for the 9:16 BIZDRIVE
cover (1080×1920). For YouTube, prefer a separate 1280×720 cover designed
elsewhere. T07's `features.thumbnail.default = false` reflects this. You can
turn it on via the Job Spec, but you'll get a vertical thumbnail unless the
script grows a horizontal mode later.

## Per-job build (V88_PLAYBOOK Step 11)

```bash
python3 scripts/set-duration.py <seconds>
python3 scripts/build-highlight-captions.py assets/intermediates/transcript/caption-groups.json compositions/captions-highlight.html <seconds> 120
python3 scripts/add-broll.py <start1> <start2> ...     # ≥120s apart, 4s each
```
