# Changelog

## v61

Added B-roll spacing guardrail.

```text
Updated current v59/Test 2 B-roll timing so starts are spaced every 6s
Added minimum B-roll start gap and real top footage gap validation to scripts/check-transition-mix.js
Updated WORKFLOW.md, CONFIG.md, QA.md, STEPS.md, AGENTS.md, and NEXT_SESSION.md with the new pacing rule
```

Reason:

```text
The user noticed that rapid B-roll clusters feel confusing, especially patterns like B-roll -> 2s real top footage -> B-roll. The workflow now treats this as a hard QA failure: do not put two B-rolls in the same 6-second viewing window, and keep enough real top footage between inserts so the viewer can settle.
```

## v60

Added required summary and frame edit reporting.

```text
Created scripts/frame-edit-report.js
Added npm script: report:frames
Updated WORKFLOW.md and AGENTS.md so every task summary reports edited frames and removed frames
Frame report separates content dropped, soft-cut overlap, total net removed, B-roll top replacement, and transition mix frames
```

Reason:

```text
The user wants every editing task to end with a clear summary and explicit frame counts: how many frames were edited and how many frames were removed. Making this a command and workflow rule keeps reporting consistent across future sessions.
```

## v59

Added B-roll Transition Mix Engine.

```text
Updated index.html B-roll entry/exit animation from simple opacity fade to transition mix
Added soft transition mode for normal B-roll and bridge transition mode for jump-cover B-roll
Added subtle object-position pan inside B-roll instead of scaling the frame wrapper
Added transitionMix metadata to context/manifest generation
Created scripts/check-transition-mix.js
Added npm script: check:transition
Updated WORKFLOW.md, CONFIG.md, MOTION_BGM.md, QA.md, STEPS.md, AGENTS.md, and final report slot output
```

Reason:

```text
The user wants every edit to feel smoother, especially where B-roll or footage switches in and out. Transition mix makes top footage -> B-roll -> top footage feel more intentional, and bridge mode helps hide jump cuts without moving the bottom face, captions, or gold frame borders.
```

## v58

Added a post-render finalize command.

```text
Created scripts/finalize-video.js
Added npm script: finalize:video
Runs Auto Final BGM and Final Report Generator in one post-render command
Supports explicit final MP4 or auto-picks the latest eligible stacked-output*.mp4
Tested end-to-end on the real v35 final MP4
Updated WORKFLOW.md, STEPS.md, REPORT_TEMPLATE.md, AGENTS.md, and NEXT_SESSION.md
```

Reason:

```text
The workflow now has reliable BGM QA and final report generation, but they still required separate commands. The finalize command makes the post-render delivery step repeatable: pick final, apply 5% speech-first BGM, run loudness QA, and write the final JSON/Markdown report.
```

## v57

Added one-command BGM apply for the latest final MP4.

```text
Created scripts/auto-final-bgm.js
Added npm script: auto:bgm
Auto-picks the newest eligible stacked-output*.mp4 while skipping preview and already-BGM outputs
Runs qa-bgm-final with generated output/report paths
Tested against the real v35 final MP4 and produced a pass BGM QA report
Updated WORKFLOW.md, STEPS.md, BGM_LIBRARY.md, and NEXT_SESSION.md
```

Reason:

```text
After render, the user should not need to copy a long final MP4 path into the BGM QA command. The wrapper reduces mistakes by selecting the latest non-preview/non-BGM final file, keeping BGM at 5%, and still preserving the full final-real-file QA path.
```

## v56

Added automatic final report generation.

```text
Created scripts/final-report.js
Added npm script: report:final
Generated a test report from the real v54/v35 final MP4, context index, B-roll manifest, BGM QA, and key term QA
Updated WORKFLOW.md, REPORT_TEMPLATE.md, and NEXT_SESSION.md
```

Reason:

```text
The workflow needs a single delivery artifact after render/QA. The final report command gathers final MP4 metadata, context cut details, B-roll download/reuse/reject counts, slot keywords, BGM selection/loudness QA, and key term QA into JSON and Markdown so the next session does not depend on memory.
```

## v55

Added a next-session handoff.

```text
Created NEXT_SESSION.md
Recorded v53 tag, v54 commit, latest verified BGM QA test, commands, outputs, and tomorrow's recommended next work
Updated WORKFLOW.md
```

Reason:

```text
The user is pausing for the night and wants the current state saved clearly. The next session should start from a compact handoff instead of re-reading the full conversation.
```

## v54

Added automatic final MP4 BGM QA.

```text
Created scripts/qa-bgm-final.js
Added npm script: qa:bgm
Updated WORKFLOW.md, STEPS.md, BGM_LIBRARY.md, CONFIG.md, QA.md, REPORT_TEMPLATE.md, and AGENTS.md
Tagged v53-auto-bgm-selector before continuing
```

Reason:

```text
The workflow already knows how to select and mix BGM, but final acceptance must happen on the real rendered MP4. This command automates selection, mixing, preview generation, loudness comparison, and JSON reporting in one repeatable step.
```

## v53

Added automatic BGM selection from title/transcript/context.

```text
Created scripts/select-bgm.js
Created bgm-library/style-keywords-v53.json
Added npm script: select:bgm
Added minimumStyleScore fallback behavior for unclear titles/context
Updated WORKFLOW.md, STEPS.md, BGM_LIBRARY.md, CONFIG.md, QA.md, REPORT_TEMPLATE.md, and AGENTS.md
```

Reason:

```text
BGM should be chosen from the meaning of the clip, not by taste or random choice. The selector reads title, transcript, and context index, scores editable style keywords, chooses a stock track, and reports the reasons plus a suggested mix command.
```

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
Set BGM mix limiter default with level=false for safer final peaks without auto-boosting
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
