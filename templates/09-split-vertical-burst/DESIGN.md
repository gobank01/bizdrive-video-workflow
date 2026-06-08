# Template 09 — Design Spec (Split Vertical · Screen + Person · Particle-Burst)

Clean top/bottom split: **top frame is the screen recording** (top.mp4),
**bottom frame is the person** as a full-width rectangle (bottom.mp4). Captions
use the BIZDRIVE **particle-burst** system — identical to Template 01: each group
pops word-by-word with a 10-particle burst, **white** words and **gold (#FFD700)**
brand / number / tech tokens — placed **centered over the seam**.

This is the **particle-burst sibling of Template 08**: same split layout, only
the caption renderer differs (T08 = karaoke word-sweep, T09 = particle-burst) —
the same relationship as Template 01 ↔ 05. Single-presenter audio: `bottom.mp4`
is the master, `top.mp4` (screen) is muted.

## Aspect / dimensions

- Canvas: 1080 × 1920 (9:16 vertical)
- **Top frame (screen / top.mp4):** left 0, top 40, 1080 × 900, border-radius 30 px, gold gradient border 4 px, `object-fit: contain` (screen never crops)
- **Bottom frame (person / bottom.mp4):** left 0, top 980, 1080 × 900 **rectangle**, border-radius 30 px, gold gradient border 4 px, `object-fit: cover` (NO circle)
- Seam: 40 px gap at y = 960 (frame edges 940 / 980)
- **Captions: particle-burst, centered over the seam at `bottom: 910px`.** This position is **hardcoded** in `scripts/build-burst-captions.py` (`bottom: 910px` / particle `bottom: 970px`) — the burst builder reads the groups JSON + duration from fixed paths and does **not** read CLI args. `tools/v88-clip.sh` sets `CAPTION_BOTTOM=910` for T09 to match, but that value only takes effect for the *highlight* builder; to move the burst captions, edit the literal in `build-burst-captions.py`.

## Colors (same as Template 01 burst)

| Token              | Hex / value                | Use                                   |
| ------------------ | -------------------------- | ------------------------------------- |
| Caption word       | `#ffffff`                  | Normal spoken word                    |
| Gold token         | `#FFD700`                  | Highlighted token (numbers, brands, tech) |
| Dim word           | `rgba(255,255,255,0.45)`   | Pre/post-spoken word in the group     |
| Frame border       | Gold gradient              | Both frame edges                      |
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
4. Captions are centered horizontally (container full-width, `justify-content: center`) and anchored at `bottom: 910px` — vertically centered over the seam between the screen (top) and the person (bottom).
5. **Caption backing (`.bs-pill`):** the words sit inside a rounded pill — BIZDRIVE-blue gradient `linear-gradient(180deg, rgba(10,22,64,.82), rgba(8,16,50,.92))` with a 2 px gold border `rgba(244,194,15,.5)` and `backdrop-filter: blur(8px)` — so white/gold text stays readable over busy video. The pill is an inner wrapper so GSAP's group transform (opacity/scale/y pop) animates pill + text together. (Chosen from a 6-variant readability comparison, 2026-06-08.)
6. Gold spacing: a highlighted token MUST be visually separated from adjacent normal text. Validated via `npm run check:caption-gold`.

## Motion rules

- Top frame (screen) inner zoom: slow (1.0 → 1.018 over half the composition, then back to 1.006). Frame shell stays still.
- B-roll inserts (in the TOP frame): pan slowly, scale 1.006 → 1.022, fade in 0.22 s / fade out 0.22 s (soft) or 0.26 s (bridge).
- Bottom face: **NEVER animate** — static rectangle, no xfade while visible (lip-sync zero tolerance, see MISTAKES.md v68/v69).

## Audio rules

- Bottom is the master timeline. Top (screen) is muted (`data-volume="0"`).
- BGM: 5 % gain, never higher. Intent = "barely audible ambient bed".
- BGM mix uses `amix=normalize=0 + alimiter` (never `-shortest` — frame lock rule).

## What this design is NOT

- A different aspect (1920×1080, 1080×1080) → make a horizontal / square template.
- The **karaoke** word-sweep version of this exact layout → that is Template 08.
- A circle face bottom → that is Template 01 (burst) / Template 05 (karaoke).
- A two-person side-by-side or stacked-people interview → not this template (this is screen + one person).
