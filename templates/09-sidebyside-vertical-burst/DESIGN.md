# Template 09 — Design Spec (Side-by-Side Two-Person · Vertical · Particle-Burst)

A new **side-by-side** layout family: two talking-head cams sit next to each
other (left + right rectangles) in a 1080×1920 vertical frame — an
**interview / conversation / 2-cam podcast** look. Captions use the BIZDRIVE
**particle-burst** system — identical to Template 01: each group pops
word-by-word with a particle burst, **white** words and **gold (#FFD700)**
brand / number / tech tokens — placed **centered over the seam between the two
cams** (horizontally and vertically centered, like Template 08's centered
captions but in the burst style).

The pipeline contract is the same as Template 08, so the locked v88 16-step
flow is unchanged: `bottom.mp4` is the audio master, `top.mp4` is the muted
second cam. Only the composition geometry (left/right) and caption position
differ.

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical)
- **Left frame (cam A / top.mp4):** left 15, top 360, 510 × 1020, border-radius 30 px, gold gradient border 4 px, `object-fit: cover` (face), object-position 50% 30%. Also the **B-roll insert host**.
- **Right frame (cam B / bottom.mp4 = audio master):** left 555, top 360, 510 × 1020, border-radius 30 px, gold gradient border 4 px, `object-fit: cover`, object-position 50% 30%.
- Seam: 30 px gap at x = 525 (frame edges 525 / 555); symmetric 15 px outer margins.
- **Captions: particle-burst, centered over the seam between the two cams at `bottom: 910px`.** This position is **hardcoded** in `scripts/build-burst-captions.py` (lines `bottom: 910px` / particle `bottom: 970px`) — the burst builder reads the groups JSON + duration from fixed paths and does **not** read CLI args. `tools/v88-clip.sh` sets `CAPTION_BOTTOM=910` for T09 to match, but that value only takes effect for the *highlight* builder; for burst, edit the literal in `build-burst-captions.py` to move the captions.

## Why ids/classes are kept from Template 08

`scripts/add-broll.py` finds `#topVideo` and injects each B-roll as a
`.broll-frame` clip that inherits `.top-media` geometry (inset inside the LEFT
frame shell). So the element **ids and classes stay** `topVideo` / `bottomVideo`
/ `top-frame-shell` / `top-media` / `bottom-frame` — only the CSS coordinates
change to left/right. This keeps `add-broll.py` working unmodified; B-roll
inserts cover **cam A (left)** while cam B keeps talking.

## Colors (same as Template 01 burst)

| Token              | Hex / value                | Use                                   |
| ------------------ | -------------------------- | ------------------------------------- |
| Caption word       | `#ffffff`                  | Normal spoken word                    |
| Gold token         | `#FFD700`                  | Highlighted token (numbers, brands, tech) |
| Dim word           | `rgba(255,255,255,0.45)`   | Pre/post-spoken word in the group     |
| Frame border       | Gold gradient              | Both cam frame edges                  |
| Background         | (from bg.png)              | BIZDRIVE blue (#0A1640 → #081032)     |

Gold gradient (frame borders): `linear-gradient(135deg, #ffec7a 0%, #ffd93d 28%, rgba(244,194,15,.95) 56%, rgba(184,134,11,.9) 78%, #ffec7a 100%)`.

## Typography

| Element  | Font family        | Weight | Size                        |
| -------- | ------------------ | ------ | --------------------------- |
| Captions | IBM Plex Sans Thai | 900    | 64 px (burst default)       |

## Caption render rules (particle-burst)

1. Each caption GROUP holds 1–3 tokens (≤ 22 visible Thai chars).
2. Group fades/pops up at `group.start`; each word pops in with a 10-particle burst as it is spoken.
3. Normal word = white; gold token = `#FFD700` (numbers, brands, tech).
4. Captions are centered horizontally (container is full-width, `justify-content: center`) and anchored at `bottom: 910px` — vertically centered over the seam between the two cams. Text overlays the lower-middle of the faces, so the burst text-shadow carries readability; on very bright frames expect an occasional WCAG-contrast warning (acceptable, same as Template 08).
5. Gold spacing: a highlighted token MUST be visually separated from adjacent normal text. Validated via `npm run check:caption-gold`.

## Motion rules

- **Both cams are faces → NEVER animate** scale or position while visible (lip-sync zero tolerance — see MISTAKES.md v68/v69). Only a 0.35 s opacity fade-in on the LEFT cam at t = 0; the RIGHT cam (audio master) stays fully static.
- B-roll inserts (in the LEFT frame): pan slowly, scale 1.006 → 1.022, fade in 0.22 s / fade out 0.22 s (soft) or 0.26 s (bridge).

## Audio rules

- `bottom.mp4` (RIGHT cam) is the master timeline and carries the **combined
  interview audio (both voices)** — for a 2-person recording captured on one
  device / room mic this is a single track. Both video divs are muted
  (`data-volume="0"`); final audio = polished `speech_polished.wav` derived from
  `bottom_visual_master.mp4`.
- BGM: 5 % gain, never higher. Intent = "barely audible ambient bed".
- BGM mix uses `amix=normalize=0 + alimiter` (never `-shortest` — frame lock rule).

## What this design is NOT

- A different aspect (1920×1080, 1080×1080) → make a horizontal / square template.
- A different caption animation (karaoke word-sweep) → that is Template 04/05/08.
- A top/bottom split (stacked or screen-over-face) → that is Template 01/05/08.
- A separate-mic two-track mixdown → out of scope; this template assumes one
  combined audio track on `bottom.mp4`. If you need per-speaker mic mixing, that
  is a pipeline change, not a layout toggle.
