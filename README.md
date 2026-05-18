# Bizdrive Stacked Video Workflow

Production workflow for building Bizdrive vertical stacked videos in HyperFrames.

## Start Here

Read in this order:

1. `WORKFLOW.md` — overview and current production defaults
2. `STEPS.md` — current practical 62-step edit map
3. `CONFIG.md` — editable settings
4. `QA.md` — QA checklists
5. `REPORT_TEMPLATE.md` — final report format
6. `CHANGELOG.md` — version history

## References

- `SYNC_REPORT.md` — top/bottom sync report template
- `KEYTERM_QA.md` — key term preservation QA
- `MOTION_BGM.md` — zoom motion and BGM loop rules
- `STEPS_PRACTICAL_99.md` — archived 99-step reference
- `STEPS_DETAILED_425.md` — detailed automation reference
- `FULL_WORKFLOW_ARCHIVE.md` — old full workflow archive

## Important Rules

- Bottom audio is the master timeline.
- Top video is the visual screen layer and must stay muted.
- Trim/dead-air cuts must be parallel across top and bottom.
- Notify the user before alignment decisions if top/bottom duration, start offset, or drift mismatches are found.
- B-roll must pass strict text/logo/watermark/brand QA.
- Key spoken terms must not disappear during context cuts.
- BGM is optional and must stay clearly under the voice.

## Local Commands

```bash
npm run check
npm run check:keyterms -- --context assets/context/test2-v35-full-context-index.json --required B-roll,prompt,caption,AI
```

Large media, raw assets, renders, and generated QA images are intentionally ignored by git.
