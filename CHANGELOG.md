# Changelog

## v82

Built and QA'd the final BGM candidate from the v81 golden proof, then fixed the BGM mixer so it cannot shorten the video stream.

```text
Updated WORKFLOW.md
Updated STEPS.md
Updated AGENTS.md
Updated NEXT_SESSION.md
Updated MISTAKES.md
Updated scripts/mix-bgm.js
Updated scripts/qa-bgm-final.js
Created local final candidate: ../preview-v80/v81-setB-final-bgm.mp4
Created local reports under reports/phase11/
```

Result:

```text
BGM selected style: tech_explainer
BGM selected track: mixkit-175 Digital Clouds
Provider/license: Mixkit / https://mixkit.co/license/
Gain: 5% (-26.0206 dB)
Base video frames: 2423
BGM final video frames: 2423
Frame delta: 0
Video duration: 80.766667s
Video/audio start_time: 0.000000 / 0.000000
Loudness: -16.3 LUFS
True peak: -1.7 dBFS
BGM QA: pass
Timestamp QA: reports/phase11/timestamps/timestamp-qa-sheet.jpg
```

Reason:

```text
The first BGM candidate used `-shortest` and silently shortened video from 2423 to 2421 frames. That violates the golden proof timing contract. v82 removes `-shortest`, pads/trims mixed audio to the source duration, and adds automatic frameLock QA so future BGM mixes fail/review if frame count, video duration, or stream start_time changes.
```

## v81

Saved the Set B Phase 10 proof as the golden checkpoint after human review.

```text
Updated WORKFLOW.md
Updated STEPS.md
Updated AGENTS.md
Updated NEXT_SESSION.md
Updated index.html for the v80 Set B Phase 10 composition
Saved golden proof locally: ../preview-v80/v80-setB-golden-phase10-proof.mp4
```

Result:

```text
User reviewed ../preview-v80/v80-setB-phase10-proof.mp4 and confirmed: "สมบูรณ์ แบบไม่ผิดเลย นี้แหละ ที่ต้องการ"
Golden proof metadata: 1080x1920, 30fps, 80.766667s, 2423 frames
Video/audio start_time: 0.000000 / 0.000000
Start delta: 0ms
Audio: -16.2 LUFS, true peak -1.5 dBFS
B-roll: 27 fresh Pexels downloads, 5 selected, 0 reused, 22 rejected, 5 optimized
Phase 10 main video frames removed: 0
Phase 10 top/bottom/audio timing shifted: 0 frames
```

Reason:

```text
This is the first phase-gated proof in the rebuilt Set B flow that the user explicitly accepted as exactly correct. Future final/BGM steps must preserve this file's timing and visual/caption/B-roll behavior as the baseline.
```

## v80

Cleaned generated artifacts and rebuilt Set B through Phase 5.

```text
Updated WORKFLOW.md
Updated STEPS.md
Updated AGENTS.md
Updated NEXT_SESSION.md
Created local report reports/phase5/v80-setB-clean-test.md
Created preview files outside repo under ../preview-v80/
```

Result:

```text
Cleaned assets/, reports/phase4/, reports/phase5/, ../preview-v78/, and ../preview-v80/
Rebuilt Set B only from raw test 2 top/bottom files
Created bottom lip-sync proof MP4 and stacked phase preview MP4
Frame/duration/start_time QA passed
Silence >0.5s after Phase 5 cut passed
Human lip-sync review is still required before Phase 6
```

## v79

Added the raw bottom lip-sync human gate.

```text
Updated WORKFLOW.md
Updated STEPS.md
Updated AGENTS.md
Updated CONFIG.md
Updated QA.md
Updated MISTAKES.md
Updated LIPSYNC_QA.md
Updated NEXT_SESSION.md
Updated local bizdrive-video skill
```

Reason:

```text
During v78 phase-gated testing, Set A and Set B both passed metadata checks, but human review found Set A mouth/audio out of sync and Set B exact. This proves ffprobe duration, frame count, fps, and stream start_time are necessary but not sufficient. v79 requires a bottom-face + bottom-audio human/visual lip-sync gate before an input set can continue past Phase 5.
```

## v78

Added phase-gated testing.

```text
Updated WORKFLOW.md
Updated STEPS.md
Updated AGENTS.md
Updated NEXT_SESSION.md
Updated local bizdrive-video skill
```

Reason:

```text
The user wants future workflow tests to proceed one Phase at a time. v78 makes every Phase boundary a user gate: show artifact, QA, and remaining risk; then wait for pass/revise/more-evidence before continuing. This prevents the editor from skipping ahead after a weak or failed Phase.
```

## v77

Added the rough direction trim gate for Step 20.1-21.

```text
Updated WORKFLOW.md
Updated STEPS.md
Updated AGENTS.md
Updated NEXT_SESSION.md
Updated local bizdrive-video skill
```

Reason:

```text
The user pointed out that the Phase 4 trim lock still did not explicitly require user rough direction, start/end candidates, evidence, and conflict reporting. v77 makes Step 20.1-21 a real decision gate: user hint becomes the anchor, AI must build candidates from evidence, and trimStart/trimEnd cannot be locked from guessing alone.
```

## v76

Added choice-based user decision gates.

```text
Updated WORKFLOW.md
Updated STEPS.md
Updated AGENTS.md
Updated NEXT_SESSION.md
Updated local bizdrive-video skill
```

Reason:

```text
The user wants important workflow questions to be easy to answer with clicks/options instead of long typing. Future editorial and creative gates should present 2-3 simple choices, recommended first, and use the user's initial direction as the anchor when already provided.
```

## v75

Added the single final output delivery rule.

```text
Updated WORKFLOW.md
Updated STEPS.md
Updated AGENTS.md
Updated NEXT_SESSION.md
Updated local bizdrive-video skill
```

Reason:

```text
The user wants future editing tasks to return only one user-facing MP4 output: the Final file. Visual-only renders, no-BGM renders, previews, masters, and other intermediates may still be created for QA, but they should stay internal unless the user asks for debug artifacts.
```

## v74

Tested a fresh full edit render through the edit-first master pipeline.

```text
Rendered visual-only output: ../stacked-output-v74-video2-test-edit-visual.mp4
Muxed speech audio master: ../stacked-output-v74-video2-test-edit-final.mp4
Mixed BGM at 5%: ../stacked-output-v74-video2-test-edit-final-bgm.mp4
Created timestamp QA sheet: render-checks/video2-v74-test-edit-timestamps/v74-test-edit-sheet.jpg
Created frame report: reports/frame-report-v74-video2-test-edit.json
Created final report: reports/final-report-v74-video2-test-edit.md
```

Final metrics:

```text
source duration: 115.946s
final duration: 85.200s
final frames: 2556
content removed: 30.746s / 922 frames
B-roll replacement: 15s / 450 frames
transition mix: 2.52s / 76 frames
B-roll new downloads: 0
B-roll reused local stock: 5
B-roll optimized derivatives: 5
B-roll rejected candidates: 0
BGM: Mixkit stock mixkit-726 Uplifting Bass, 5%, QA pass
QA: pass; only timeline_track_too_dense warning remains
```

Reason:

```text
The user asked to test editing. v74 verifies that the current edit-first pipeline still renders correctly after the v73 completion-marker rule, with speech timing locked by the v72 editorial masters.
```

## v73

Added a clear task completion marker rule.

```text
Updated WORKFLOW.md
Updated STEPS.md
Updated AGENTS.md
Updated NEXT_SESSION.md
Updated local bizdrive-video skill
```

Reason:

```text
The user wants every fully completed task to end with a highly visible `✅✅✅` marker. The marker is allowed only after the task is complete and verified, so it remains a clear signal rather than decoration.
```

## v72

Rebuilt video2 with an edit-first master architecture to remove the remaining lip-sync workflow risk.

```text
Built scripts/build-video2-v72-edit-first-final.js
Created assets/video2/top_edit_master_v72.mp4
Created assets/video2/bottom_visual_master_v72.mp4
Created assets/video2/speech_audio_master_v72.wav
Created assets/video2/bottom_editorial_master_v72.mp4 for lip-sync proof before layout
Rendered HyperFrames visual-only output: ../stacked-output-v72-video2-edit-first-visual.mp4
Muxed speech_audio_master back after render: ../stacked-output-v72-video2-edit-first-final.mp4
Mixed final BGM at 5%: ../stacked-output-v72-video2-edit-first-final-bgm.mp4
Updated WORKFLOW.md, STEPS.md, AGENTS.md, MISTAKES.md, NEXT_SESSION.md, local bizdrive-video skill, and added MODULES.md
```

Final metrics:

```text
source duration: 115.946s
final duration: 85.200s
final frames: 2556
content removed: 30.746s / 922 frames
B-roll replacement: 15s / 450 frames
transition mix: 2.52s / 76 frames
B-roll new downloads: 0
B-roll reused local stock: 5
B-roll optimized derivatives: 5
B-roll rejected candidates: 0
BGM: Mixkit stock mixkit-726 Uplifting Bass, 5%, QA pass
QA: pass; only timeline_track_too_dense warning remains
```

Reason:

```text
The user correctly diagnosed that the workflow should finish the edit before placing the video into the background/layout composition. v72 makes the editorial masters the source of truth: top visual, bottom visual, and speech audio are frame/sample locked before HyperFrames. HyperFrames no longer owns speech timing; it renders visuals only, and the locked speech audio master is muxed back afterward.
```

## v71

Rendered the new video2 final with the full current workflow.

```text
Built scripts/build-video2-v71-full-final.js
Rendered ../stacked-output-v71-video2-lipsync-safe-final.mp4
Mixed final BGM at 5% into ../stacked-output-v71-video2-lipsync-safe-final-bgm.mp4
Used bottom audio as the master timeline and muted top audio
Cut false start/dead air in parallel from top and bottom
Used lip-sync-safe hard concat for bottom face/audio with no visible bottom xfade
Used B-roll only to replace the top frame, with transition mix and stable borders
Created every-second timestamp QA sheets for final and BGM final
Created cut and B-roll contact sheets for visual QA
Generated frame report, BGM QA report, keyterm QA report, and final report
Updated WORKFLOW.md and NEXT_SESSION.md with v71 as the latest proven output
```

Final metrics:

```text
source duration: 115.946s
final duration: 85.200s
final frames: 2556
content removed: 30.746s / 922 frames
B-roll replacement: 15s / 450 frames
transition mix: 2.52s / 76 frames
B-roll new downloads: 0
B-roll reused local stock: 5
B-roll optimized derivatives: 5
B-roll rejected candidates: 0
BGM: Mixkit stock, 5%, QA pass
QA: pass; only timeline_track_too_dense warning remains
```

Reason:

```text
The user asked for a new, more detailed final edit following all current rules. v71 proves the tightened lip-sync-safe workflow on the real video2 assets, keeps speech-first audio, verifies the rendered clip every second, and records exact frame counts for the edit.
```

## v70

Added every-second timestamped clip QA.

```text
Created scripts/timestamp-qa-sheet.js
Added npm run qa:timestamps
Updated WORKFLOW.md, CONFIG.md, QA.md, STEPS.md, AGENTS.md, LIPSYNC_QA.md, NEXT_SESSION.md, and local bizdrive-video skill
Required a visible timestamp label every 1 second when checking rendered clips
Required issue reports to reference the 1-second timestamp from the QA sheet
```

Reason:

```text
The user wants clip inspection to be timestamped every second. This makes lip sync, cut, caption, B-roll, BGM, and visual QA easier to discuss and reproduce without guessing the exact moment.
```

## v69

Recorded the lip-sync root cause and changed soft-cut rules to be lip-sync-safe.

```text
Created reports/lipsync-root-cause-v69.md with evidence from v66 diagnostics
Updated WORKFLOW.md, CONFIG.md, QA.md, STEPS.md, AGENTS.md, MISTAKES.md, LIPSYNC_QA.md, NEXT_SESSION.md, and local bizdrive-video skill
Identified that v66 xfade blended visible bottom face frames at content cuts
Identified that acrossfade blended speech phonemes at the same cuts
Forbid xfade on visible bottom face
Require cut contact sheets around every content cut
Require B-roll/bridge or safe hard cuts instead of blending bottom mouth frames
```

Reason:

```text
The user reported that lip sync still appeared wrong. Diagnostics showed ghost/double-mouth frames around content cuts because bottom face video was xfade blended. A metadata delay cannot fix blended mouth frames, so the workflow now separates top/B-roll soft transitions from the bottom lip-sync layer.
```

## v68

Added zero-tolerance lip-sync rules.

```text
Created LIPSYNC_QA.md as the required lip-sync verification document
Updated MISTAKES.md with a v68 lip-sync zero-tolerance lesson
Updated WORKFLOW.md, CONFIG.md, QA.md, STEPS.md, AGENTS.md, NEXT_SESSION.md, and local bizdrive-video skill
Made lip sync a hard blocker, not a best-effort QA item
Required final stream start_time check after render
Required at least 5 lip-sync spot-check points before final delivery
Required compensationMs and reason when any offset is applied
Required residualRisk=none; otherwise output is blocked and cannot be called final
```

Reason:

```text
The user emphasized that lip sync must never fail. v68 makes lip-sync verification a zero-tolerance gate with explicit proof requirements and a stop rule.
```

## v67

Locked the v65/v66 mistakes into the workflow so they cannot be missed in future sessions.

```text
Created MISTAKES.md as a permanent incident and prevention log
Recorded the v65 false-start/opening-noise mistake
Recorded the v65 audio-source mistake: trusting a prior polished file without re-verifying quality/sync
Recorded the v65 sync QA mistake: checking frame count/duration but not final stream start_time
Recorded the caption remap risk after any new trim/cut
Updated WORKFLOW.md, CONFIG.md, QA.md, STEPS.md, AGENTS.md, NEXT_SESSION.md, and the local bizdrive-video skill with hard gates
```

Hard gates added:

```text
Opening gate: true start must be sustained speech, not first detectable sound
Audio source gate: raw vs polished source must be chosen with evidence
Noise gate: opening false start/noise must be checked before and after polish
Sync metadata gate: final ffprobe video/audio stream start_time must be checked after render
Caption map gate: captions must be remapped after every trim/dead-air/context cut
Summary gate: final summary must report mistake prevention gate status
```

Reason:

```text
The user asked to save all mistakes and prevent them from happening again. v67 makes the incident log a required source of truth and turns each known failure into a blocking QA gate.
```

## v66

Fixed the v65 review issues around opening noise and perceived lip sync.

```text
Built scripts/build-video2-v66-noise-sync-fix.js
Dropped raw 0.0-2.3s because it contained a short false start/non-sustained opening sound followed by reset/silence before sustained speech
Rebuilt top and bottom soft cuts in parallel from the same bottom-master cut list
Changed bottom audio source from the previous polished 96k file back to raw assets/video2/bottom.mp4
Added a speech-first audio chain: highpass, lowpass, afftdn, agate, compressor, loudnorm, limiter
Logged and applied 21ms audio delay compensation because v65 final metadata showed audio start 0.000s while video stream started 0.021s
Rendered ../stacked-output-v66-video2-noise-sync-fix.mp4
Generated reports/frame-edit-report-v66-video2.json
Generated reports/final-report-v66-video2.json and reports/final-report-v66-video2.md
```

Frame results:

```text
original: 115.946s / 3478 frames
final: 87.054s / 2612 report frames, 2611 video stream frames
content dropped: 28.446s / 853 frames
soft-cut overlap removed: 0.446s / 13 frames
total net removed: 28.892s / 867 frames
B-roll top replacement: 15s / 450 frames
transition mix: 2.36s / 71 frames
visible inner-media motion: 87.02s / 2611 frames
```

Reason:

```text
The user reported that v65 opening noise was not acceptable and mouth/audio still felt off. Root-cause checks found the opening had a false start before sustained speech and the rendered MP4 had a video stream start around 21ms after audio. v66 cuts the false start, uses a stronger but still speech-first audio chain from the raw bottom source, and logs the sync compensation.
```

## v65

Ran a full video2 edit test under the v64 production guardrails.

```text
Built scripts/build-video2-v65-full-v64-test.js for repeatable v64-rule validation
Used bottom audio as the master timeline and kept top/bottom/captions on the same edited timeline
Reused the timestamped Whisper large-v3 transcript from the same video2 bottom source
Reduced 115.946s raw source to 89.354333s final output
Kept the same Medium context cut plan as v63, but reduced B-roll density from 8 slots to 5 slots
Fresh Pexels sourcing was attempted, but blocked because PEXELS_API_KEY was not present in the shell environment
Reused 5 local QA-passed Pexels stock clips and re-encoded 5 optimized derivatives
Rendered ../stacked-output-v65-video2-v64-full-test.mp4
Generated reports/frame-edit-report-v65-video2.json
Generated reports/final-report-v65-video2.json and reports/final-report-v65-video2.md
```

Frame results:

```text
original: 115.946s / 3478 frames
final: 89.354s / 2681 report frames, 2680 video stream frames
content dropped: 26.146s / 784 frames
soft-cut overlap removed: 0.446s / 13 frames
total net removed: 26.592s / 798 frames
B-roll top replacement: 15s / 450 frames
transition mix: 2.36s / 71 frames
visible inner-media motion: 89.32s / 2680 frames
```

Reason:

```text
The user requested a new full edit test after tightening the workflow rules. v65 verifies that the v64 sync lock, Whisper requirement, step gates, B-roll density cap, transition mix, and motion safety can run together on the real video2 output.
```

## v64

Added stricter production rules after video2 review.

```text
Updated WORKFLOW.md with sync lock, sequential execution gates, Whisper-required policy, B-roll fresh-stock policy, B-roll density cap, and meaning-first duration target
Updated CONFIG.md with editable values for sync lock, target duration ceiling, transcription fallback, stock index target, and progress updates
Updated STEPS.md so each phase has gates and cannot proceed without required artifacts
Updated QA.md with checks for frame-accurate sync, Whisper transcript, caption timeline mapping, B-roll count limit, and stock/index reporting
Updated AGENTS.md so future sessions announce steps, preserve sync, require Whisper, and prefer fresh B-roll until stock matures
Updated local bizdrive-video skill with the same core rules
```

New rules:

```text
Bottom audio, bottom video, top video, and captions must stay locked on one edited timeline
Whisper timestamped transcription is required before context cut or captions
Every step must be executed in order with a check before moving on
B-roll should try fresh download first until the stock index has about 200 QA-passed clips
B-roll may be reused before 200 only when it clearly matches better or fresh sourcing is blocked
B-roll density is capped at 4 inserts per 60 seconds of final video unless explicitly overridden
Target duration is a ceiling/meaning target: if 1:30 is requested but 1:20 preserves the full message, 1:20 is acceptable and preferred
Progress updates during work should name the current Step/Phase and what is being verified
```

Reason:

```text
The v63 output was good, but future edits need stronger guarantees: exact sync between sound/top/bottom/subtitles, mandatory Whisper context, predictable step-by-step execution, stock-building B-roll behavior, and less dense B-roll pacing.
```

## v63

Completed a full video2 re-edit to about 1:30.

```text
Built scripts/build-video2-v63-context90.js for repeatable video2 context-cut renders
Used bottom audio as the master timeline and cut top/bottom in parallel
Reduced 115.946s raw source to 89.354333s final output
Kept the core hook, feature proof, technology-readiness explanation, assistant benefit, and CTA
Dropped repeated/secondary sections with 0.12s video/audio soft cuts
Re-encoded top/bottom soft-cut media at 30fps, GOP 30, faststart, and bottom audio 48k
Created 8 job-specific B-roll derivatives from local Pexels stock
Rejected 3 earlier B-roll candidates because of graphic/text risk
Rendered ../stacked-output-v63-video2-context90-full.mp4
Generated reports/frame-edit-report-v63-video2.json
Generated reports/final-report-v63-video2.json and reports/final-report-v63-video2.md
```

Frame results:

```text
original: 115.946s / 3478 frames
final: 89.354s / 2681 report frames, 2680 video stream frames
content dropped: 26.146s / 784 frames
soft-cut overlap removed: 0.446s / 13 frames
total net removed: 26.592s / 798 frames
B-roll top replacement: 24s / 720 frames
transition mix: 3.76s / 113 frames
visible inner-media motion: 89.32s / 2680 frames
```

Reason:

```text
The user asked to fully re-edit the new video2 clip of about 1:30. The workflow was exercised end-to-end with context analysis, semantic shortening, soft cuts, B-roll replacement, motion safety, transition QA, render QA, and final reporting.
```

## v62

Added slow inner-media motion with frame safety checks.

```text
Separated the top gold frame into a fixed topFrameShell and inner top/B-roll media
Added very slow top/B-roll inner zoom movement without moving top/bottom frame borders
Created scripts/check-motion-safety.js
Added npm script: check:motion
Updated WORKFLOW.md, CONFIG.md, MOTION_BGM.md, QA.md, STEPS.md, and AGENTS.md
Rendered a 20s video2 smoke test using Screen 1 as top and Screen 2 as bottom/audio
```

Reason:

```text
The user wants smoother, slower zoom in/out movement, but the most important rule is that neither the top nor bottom frame may move. The workflow now supports subtle motion only inside the fixed top frame, with an automated safety check to prevent transforms on the top frame shell, bottom frame, or bottom face video.
```

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
