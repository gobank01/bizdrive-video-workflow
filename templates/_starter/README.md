# Template __TEMPLATE_NUMBER__ — __TEMPLATE_SLUG__

> **Skeleton template.** Customize this file with the new template's specifics.

## When to use

Describe the pattern: aspect ratio, layout shape, talking-head vs no-face, caption style, target platform.

## When NOT to use

Cases that look similar but belong in a different template.

## What this template produces

```
Output:  {WIDTH}×{HEIGHT}, {FPS} fps, H.264 / AAC
Layout:  describe the visual composition
Captions: describe the caption render approach
Audio:   describe the audio rules
```

Reference render: `../../jobs/<reference-job-folder>/output/finals/final.mp4`

## How to start a new clip

```bash
bash tools/new-job.sh __TEMPLATE_NUMBER__ my-clip-slug
```

Follow the 15-step pipeline in `templates/_shared/docs/V88_PLAYBOOK.md`.

## Files in this template

```
manifest.json   machine-readable spec
README.md       this file
DESIGN.md       colors / fonts / position
index.html      composition source-of-truth
hyperframes.json
meta.json
package.json
compositions/
scripts/        per-template build scripts
assets/         template default assets
prompts/        subagent slot defaults
reference/      golden test
```

## Golden test

Document tolerances against the reference render.
