# Changelog

## v52

Record the accepted BGM audibility intent.

```text
Documented that BGM 5% should be barely audible
Added rule that BGM should be felt more than heard
Added QA checks for melody not pulling attention from speech
Updated WORKFLOW.md, STEPS.md, MOTION_BGM.md, BGM_LIBRARY.md, CONFIG.md, QA.md, REPORT_TEMPLATE.md, and AGENTS.md
```

Reason:

```text
The user confirmed that the tested 5% BGM is barely audible and that this is desirable. The workflow should preserve this intent: speech clarity comes first, and BGM is only there to keep the clip from feeling dry.
```

## v51

Require BGM QA on the real final MP4.

```text
Added final-real-file BGM QA rule
Required original final MP4 vs BGM final MP4 loudness comparison
Required original/BGM preview clips for listening comparison
Updated WORKFLOW.md, STEPS.md, QA.md, MOTION_BGM.md, REPORT_TEMPLATE.md, and AGENTS.md
```

Reason:

```text
Testing BGM only on the bottom source proves the mix tool, but it does not prove the real viewer experience after top, bottom, captions, B-roll, and final render are combined. Final BGM acceptance must happen on the actual final MP4.
```

## v50

Set the default BGM fallback and test policy.

```text
Set default fallback to mixkit-480 Curiosity
Set tech fallback to mixkit-1167 Close Up
Set calm fallback to mixkit-441 Meditation
Updated BGM index validation to require the fallback IDs
Fixed BGM mix to use amix normalize=0 so voice loudness is preserved
Set BGM mix limiter default to 0.84 with level=false for safer final peaks without auto-boosting
Updated WORKFLOW.md, BGM_LIBRARY.md, CONFIG.md, MOTION_BGM.md, STEPS.md, QA.md, and AGENTS.md
```

Reason:

```text
When title/transcript/context is unclear, the workflow needs a safe default instead of stalling or choosing a random song. Curiosity is the least risky general-purpose stock track because it is corporate, relaxed, positive, and low-medium energy.
The 5% test also showed that amix normalization was lowering the main voice, so the mix now preserves voice loudness and only adds BGM underneath.
```

## v49

Added a reusable royalty-free BGM stock library.

```text
Downloaded 15 Mixkit starter BGM tracks to assets/bgm/stock/mixkit
Created BGM_LIBRARY.md
Created initial bgm-library Mixkit stock index with style tags and usage guidance
Created scripts/check-bgm-library.js
Added npm script: check:bgm
Updated WORKFLOW.md, STEPS.md, CONFIG.md, MOTION_BGM.md, QA.md, REPORT_TEMPLATE.md, and AGENTS.md
```

Reason:

```text
The workflow should not generate or hunt for music every time. It should reuse a verified local stock library first, choose by clip style, keep source/license metadata, and mix under speech at 5%.
```

## v48

Set the BGM workflow to voice-first 5% by default.

```text
Changed scripts/mix-bgm.js default BGM level to 5%
Added --gain-percent for human-readable mix control
Recorded source/license policy for BGM
Updated WORKFLOW.md, MOTION_BGM.md, CONFIG.md, STEPS.md, QA.md, REPORT_TEMPLATE.md, and AGENTS.md
```

Reason:

```text
Speech clarity is the priority. BGM should be ambience only, and no workflow should imply that arbitrary music is copyright-free without documented usage rights.
```

## v47

Implemented BGM mix tooling.

```text
Created scripts/mix-bgm.js
Added npm script: mix:bgm
Updated MOTION_BGM.md with runnable commands
Updated WORKFLOW.md, CONFIG.md, STEPS.md, QA.md, REPORT_TEMPLATE.md, and AGENTS.md
```

Reason:

```text
BGM loop should be more than a rule. The workflow now has a repeatable ffmpeg-based command to loop, fade, optionally duck, mix, limit, and report BGM under the bottom voice.
```

## v46

Added Zoom Motion and BGM Loop production options.

```text
Created MOTION_BGM.md
Added Motion Zoom defaults to CONFIG.md
Added BGM Loop defaults to CONFIG.md
Updated STEPS.md, QA.md, REPORT_TEMPLATE.md, WORKFLOW.md, and AGENTS.md
```

Reason:

```text
The user wants the workflow to support interesting zoom in/out motion and background music loops while preserving speech clarity and professional visual restraint.
```

## v45

Added Key Term QA documentation and a runnable key term checker.

```text
Created KEYTERM_QA.md
Created scripts/check-keyterms.js
Added npm script: check:keyterms
Updated REPORT_TEMPLATE.md, QA.md, WORKFLOW.md, and AGENTS.md
```

Reason:

```text
Key spoken terms such as B-roll, prompt, caption, and Dead Air must not disappear during context cuts. This checker gives the workflow a repeatable QA gate.
```

## v44

Added context index schema.

```text
Created schemas/context-index.schema.json
Documented required top-level fields, segment fields, and B-roll slot fields
Updated workflow defaults to reference the schema
```

Reason:

```text
Context index is the central brain for cut plans, captions, B-roll, and QA. It needs a stable structure before deeper automation.
```

## v43

Added Sync Report template.

```text
Created SYNC_REPORT.md
Defined bottom audio as master timeline in sync reports
Added required fields for duration mismatch, start offset, drift, user notification, and sync decisions
```

Reason:

```text
Top/bottom sync issues can ruin the final video. Sync decisions need a documented report, especially when top and bottom do not start or end together.
```

## v42

Added bottom-master sync policy.

```text
Bottom audio is the master timeline because it contains the real speech
Top remains the visual screen layer and must stay muted
If top/bottom duration, start offset, or drift mismatch is found, the user must be notified before alignment/cutting decisions
If mismatch exists, inspect sync first and align top to bottom rather than trusting top timing
Updated WORKFLOW.md, CONFIG.md, STEPS.md, and QA.md
```

Reason:

```text
The workflow must handle cases where top and bottom are not the same length or do not start at the same time. Bottom is more important because it carries the final audio, but the user should know before the system changes alignment.
```

## v41

Changed `STEPS.md` into the latest preferred practical 62-step edit map.

```text
Kept the 99-step version as `STEPS_PRACTICAL_99.md`
Kept the detailed 425-step version as `STEPS_DETAILED_425.md`
Made `STEPS.md` the concise 62-step source for step-by-step workflow editing
Updated `WORKFLOW.md` and `AGENTS.md` references
```

Reason:

```text
The user clarified that the latest workflow base to edit from should be the nearly 62-step version, not the 99-step or 425-step reference.
```

## v40

Changed `STEPS.md` from the 425-step automation map into a practical 99-step edit map.

```text
Kept the detailed 425-step version as `STEPS_DETAILED_425.md`
Made `STEPS.md` easier to edit and discuss step-by-step
Updated `WORKFLOW.md` to point to both step documents
```

Reason:

```text
The user wants to begin editing from a workflow with almost 100 steps, not the very detailed 425-step automation reference.
```

## v39

Expanded `STEPS.md` into a detailed 425-step execution map.

```text
Added phases for project intake, input discovery, raw media inspection, trim, dead air, audio polish, transcription, key terms, context index, cut plan, soft cuts, B-roll, captions, composition, QA, render, reporting, versioning, artifacts, and future automation targets.
```

Reason:

```text
The workflow is now ready for deeper development. The next work should happen step-by-step against a detailed roadmap instead of adding broad rules to one long document.
```

## v38

Restructured the workflow docs for long-term development and sharing.

```text
Created WORKFLOW.md as concise overview
Moved old full v37 workflow to FULL_WORKFLOW_ARCHIVE.md
Created STEPS.md for agent step-by-step execution
Created CONFIG.md for editable settings
Created QA.md for checklists
Created PROMPT_TEMPLATE.md for new sessions
Created REPORT_TEMPLATE.md for final reports
Created CHANGELOG.md for version history
```

Reason:

```text
Workflow is growing toward 150+ steps and should be modular now instead of staying as one long file.
```

## v37

Separated editable key terms into their own workflow section so future users can customize project-specific terms.

## v36

Added key spoken term preservation after QA found the spoken word "B-roll" should not be cut from the final video.

## v35

Full context test succeeded with Full context index, Medium cut, soft cuts, fresh Pexels B-roll, and B-roll cover jump cuts.

## v34

Validated context-based shortening from about 85s to about 60s while preserving meaning.

## v33

Created reusable `bizdrive-video` skill.

## v32

Downloaded fresh context-matched B-roll candidates and selected 10 final QA-passed B-roll clips.

## v31

Added mandatory B-roll reporting rule.

## v29

Added strict B-roll QA rule: reject text, logo, watermark, other brand, distracting graphic.

## v25-v28

Established Pexels stock B-roll library, index, reuse behavior, and saved baseline.

## v23-v24

Added OpenRouter B-roll generation and stock B-roll strategy.

## Earlier

Built stacked video layout, trim/dead-air rules, audio polish, Thai captions, gold highlight styling, and render QA.
