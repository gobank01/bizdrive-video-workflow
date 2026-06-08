# Template __TEMPLATE_NUMBER__ — frame.md (design / frame spec)

<!--
  This is the per-template frame.md — the "frame spec" for this template.
  It is the design-system source of truth an AI agent reads BEFORE composing a
  clip: tokens stay fixed, the script fills the words, the agent never guesses.
  Name follows HeyGen HyperFrames' frame.md convention; ours is per-template.

  Fill EVERY section below, in this order, so every template reads the same way
  (see AGENTS.md RULE 4). Delete a section only if it truly does not apply, and
  leave one line saying why where it would have been.
-->

## Aspect / dimensions

- Canvas: {WIDTH} × {HEIGHT} ({ASPECT_RATIO}, {FPS}fps)
- Primary frame: size, position, border-radius, border
- Secondary frame: if applicable (shape, diameter, position)
- Caption band: where captions sit (e.g. `bottom: 360px`, above the circle)

## Colors

| Token             | Hex / value                  | Use                            |
| ----------------- | ---------------------------- | ------------------------------ |
| Caption active    | `#ffffff`                    | Token currently being spoken   |
| Caption highlight | `#FFD700`                    | Highlighted token (numbers, brands) |
| Caption dim       | `rgba(255,255,255,0.45)`     | Token not yet spoken           |
| Frame border      | gold gradient                | Frame edges                    |
| Background        | TBD                          | from bg.png / solid            |

Gradients / particle palettes (if any): describe here.

## Typography

| Element     | Font family           | Weight | Size  |
| ----------- | --------------------- | ------ | ----- |
| Captions    | IBM Plex Sans Thai    | 900    | 64 px |

## Layout layers (z-index)

List the stack bottom→top so the compositor order is unambiguous:

1. background (z 0)
2. ...
3. captions (top)

## Caption render rules

How captions enter, hold, transition between groups, and exit. Tokens per group,
max chars, highlight policy.

## Motion rules

What animates and what stays still. Easing, durations, what is seek-driven.

## Audio rules

Master timeline, muting policy, loudness target (e.g. `-16 LUFS`), BGM, SFX.

## What this template is — and is NOT

List similar-looking patterns that belong in a DIFFERENT template, so nobody
clones this one for the wrong job. (The anti-pattern guard.)
