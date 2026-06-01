# Template 06 — Screencast with Corner Cam + Particle-Burst Captions

A screen recording fills the whole 1080×1920 vertical frame; the presenter's
face rides along as a small circular **corner-cam** in the upper-left that
stays visible the entire clip — even while full-screen B-roll plays.

Scaffold a job:

```bash
bash tools/new-job.sh 06 <slug> --raw <raw-slug>
```

## What makes it different

|                  | Template 01                  | **Template 06**               |
| ---------------- | ----------------------------- | ----------------------------- |
| Screen recording | framed top half (16:9 native) | **full-screen**               |
| Face             | bottom circle, ~50% of frame  | **small corner-cam**          |
| Hero of the shot | balanced screen + face        | **the screen**                |
| Best for         | 16:9 desktop captures         | vertical / phone-screen demos |

The corner-cam never disappears — when B-roll cuts in full-screen, the
presenter stays in the corner, so the clip always has a face on it.

## Source media

Two videos — `top.mp4` (screen recording) + `bottom.mp4` (face + master
audio) — plus `bg.png`. Same inputs as Template 01 / 05.

## Captions

Particle-burst (white/gold text + gold dot burst on key tokens) over a
lower-third dark scrim.

## Pipeline

Standard v88 — see [`../_shared/docs/V88_PLAYBOOK.md`](../_shared/docs/V88_PLAYBOOK.md).
Step 11 is the 3-script flow: `set-duration.py` → `build-burst-captions.py` →
`add-broll.py`.

## Features (Template Manager toggles)

dead-air cut · audio polish · captions · B-roll · BGM · SFX · thumbnail.
Build a Job Spec for this template with `tools/template-manager.html`.

## Status

🆕 Ready 2026-05-21 — composition authored against the proven Template 02/05
patterns. Not yet render-verified against a real clip; the first job becomes
the reference render.
