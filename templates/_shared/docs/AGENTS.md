# HyperFrames Composition Project

**v88 status:** PERFECT CHECKPOINT (locked 2026-05-19) — bizdrive pipeline integrated.
For new clips or porting to a different AI agent, start with [`V88_PLAYBOOK.md`](V88_PLAYBOOK.md) and the verbatim prompts in [`SUBAGENT_PROMPTS.md`](SUBAGENT_PROMPTS.md). Do NOT rewrite the subagent prompts — every clause is load-bearing (see [`MISTAKES.md`](MISTAKES.md) v88 lessons).

## v88 Hard Rules for AI Agents

1. Bottom audio is the master timeline. Top is muted visual only.
2. Trim/dead-air cuts MUST be parallel across top and bottom (same EDL applied to both).
3. Editorial subagent prompt (SUBAGENT_PROMPTS.md Section A) is immutable. Fill the `{{...}}` slots only.
4. Post-process subagent prompt (SUBAGENT_PROMPTS.md Section B) is immutable. Fill the `{{...}}` slots only.
5. Editorial output `edl-rough.json` MUST pass `npm run rough:cut:padbleed` before applying.
6. Apply EDLs to top.mp4 and bottom.mp4 with the SAME EDL files. Frame counts MUST match after.
7. Polished WAV is the speech master. Mux step trims to video duration, never `-shortest`.
8. Caption timing comes from re-transcribed polished audio (edited timeline), not interpolation from raw transcript on original timeline.
9. Caption sub-composition lives in `compositions/captions-burst.html`. Inline subtitle-XX divs are forbidden after v88 (causes timeline_track_too_dense).
10. BGM mix preserves frame count. Loudness target -16 LUFS, tolerance -14 to -18.

## Skills

This project uses AI agent skills for framework-specific patterns. Install them if not already present:

```bash
npx skills add heygen-com/hyperframes
```

Skills encode patterns like `window.__timelines` registration, `data-*` attribute semantics, Tailwind v4 browser-runtime styling for `--tailwind` projects, and shader-compatible CSS rules that are not in generic web docs. Using them produces correct compositions from the start.

## Commands

```bash
npm run dev          # start the preview server (long-running — keep it alive in background)
npm run check        # lint + validate + inspect
npm run render       # render to MP4
npm run publish      # publish and get a shareable link
npx hyperframes docs <topic> # reference docs in terminal
```

> **`npm run dev` is a long-running server, not a one-shot command.** It blocks until stopped.
> Always run it as a background process so it stays alive while you edit compositions.
> Running it in the foreground will time out and kill the server, breaking the browser preview.

## Project Structure

- `index.html` — main composition (root timeline)
- `compositions/` — sub-compositions referenced via `data-composition-src`
- `assets/` — media files (video, audio, images)
- `meta.json` — project metadata (id, name)
- `transcript.json` — whisper word-level transcript (if generated)

## Bizdrive Workflow Docs — v87

For Bizdrive stacked-video work, read these files in order:

1. `WORKFLOW.md` — current overview and latest production defaults
2. `STEPS.md` — practical 62-step execution list for real editing
2.1. `MODULES.md` — modular subprojects/commands for transcript, sync, B-roll, render, final QA
3. `CONFIG.md` — editable settings such as key terms, layout, audio, captions, and B-roll provider order
4. `QA.md` — required QA checklists
5. `MISTAKES.md` — real incident log and hard gates that must not regress
6. `LIPSYNC_QA.md` — zero-tolerance lip-sync gate and report format
7. `SYNC_REPORT.md` — sync mismatch/bottom-master reporting template
8. `KEYTERM_QA.md` — key term preservation QA rules
9. `MOTION_BGM.md` — zoom motion and BGM loop rules
10. `BGM_LIBRARY.md` — BGM stock index and style map
11. `REPORT_TEMPLATE.md` — final report format
12. `CHANGELOG.md` — workflow version history

`STEPS_PRACTICAL_99.md` is an archived 99-step reference. Use it only when the 62-step edit map needs more detail.

`STEPS_DETAILED_425.md` is a detailed automation reference. Use it when building scripts or expanding the workflow, but use `STEPS.md` as the current edit map.

`FULL_WORKFLOW_ARCHIVE.md` is historical reference only. Do not treat it as the latest source of truth unless a detail is missing from the split docs.

Every workflow rule change increments the version and must be recorded in `CHANGELOG.md`. If the change affects execution, update `STEPS.md` and/or `CONFIG.md` instead of burying it only in prose.

Execution style rule: while working, report progress to the user as numbered steps. Say what Step/Phase is running, what is being checked, and what artifact proves it passed. Do not silently skip steps.

Choice-based decision rule: before important editorial/creative decisions, ask the user with 2-3 simple options instead of open-ended typing. Put the recommended option first, keep labels short, and use clickable choices when the UI/tool supports it. If clickable choices are unavailable, use A/B/C options and accept a one-letter or short reply. If the user already gave direction at the start, use that as the answer and do not ask again.

Phase-gated testing rule: from v78 onward, run tests and edits one Phase at a time. After each Phase, stop and show the user the phase artifact, QA result, remaining risk, and choices: A. pass to next Phase, B. revise this Phase, C. show more evidence. Do not cross a Phase boundary until the user passes it, unless the user explicitly requests auto/full mode. If a Phase fails QA, fix and rerun that same Phase before continuing.

Rough direction trim gate: before locking `trimStart`/`trimEnd`, collect user rough direction if available: approximate start, approximate end, must keep, must remove, target duration, and cut tone. AI must create start/end candidates from user hint plus audio evidence, rough transcript, and silence/VAD evidence. If evidence conflicts with user hint, report it before locking the cut. The lock record must include selected candidate, rejected candidates, frame/sample values, evidence, and reason.

Mistake prevention rule: read `MISTAKES.md` before every video edit. Treat its hard gates as blockers: opening sustained speech, audio source proof, noise proof, final stream start_time sync, caption remap proof, and final summary gate. Do not claim final completion if any gate lacks evidence.

Lip-sync zero-tolerance rule: read `LIPSYNC_QA.md` before every video edit. Lip sync must be treated as a blocker, not a best-effort check. Do not call an output final unless final stream start_time was checked, any compensation is logged in ms, at least 5 lip-sync spot-check points were reviewed, and residualRisk is none. If uncertain, report blocked.

Raw bottom lip-sync human gate: metadata sync is not enough. Before accepting an input set or crossing Phase 5 into Phase 6, preview bottom face with its own bottom audio and require human/visual lip-sync pass. If one candidate set fails by human review while another passes, continue only with the passing set. A failed set is blocked until rebuilt from synced source or corrected with measured/logged compensation evidence.

Latest v87 checkpoint: `../preview-v87/v87-video-div-final.mp4` was built from folder `../video div` after the user directed trimming the first 24 seconds and then approved finishing the job. It is the latest real-folder final render proof: 103.466667s, 3104 frames, video/audio start_time 0.000000, BGM 5%, B-roll top-frame only, final QA pass with one timeline_track_too_dense warning.

Latest v81 checkpoint: Set B Phase 10 proof `../preview-v80/v80-setB-phase10-proof.mp4` was reviewed by the user and accepted as "สมบูรณ์ แบบไม่ผิดเลย นี้แหละ ที่ต้องการ". The golden copy is `../preview-v80/v80-setB-golden-phase10-proof.mp4`. Continue final/BGM only from this baseline, and do not change top/bottom/audio/caption timing.

Latest v82 checkpoint: BGM final candidate `../preview-v80/v81-setB-final-bgm.mp4` was built from the v81 golden proof with Mixkit `mixkit-175 Digital Clouds` at 5%. QA passed only after preserving the original video stream: 2423 frames, 80.766667s, video start_time 0.000000, audio start_time 0.000000, loudness -16.3 LUFS, true peak -1.7 dBFS.

BGM frame-lock rule: BGM mix must not shorten, extend, shift, retime, or drop frames from the accepted final/golden proof. `mix-bgm.js` must not use `-shortest`; `qa-bgm-final.js` frameLock must pass. If frameDelta is not 0, do not deliver the file.

Latest v83 checkpoint: accepted final output is `../preview-v80/v83-setB-final-accepted.mp4`. User reviewed the BGM candidate and confirmed "สมบูรณ์แบบ ไปต่อได้เลย". Final report status is pass at `reports/phase11/v83-final-report.md` / `.json`. Metadata: 1080x1920, 30fps, 80.766667s, 2423 frames, video/audio start_time 0/0, BGM frameDelta 0, loudness -16.3 LUFS, true peak -1.7 dBFS.

Final report rule: report video frames/start metadata and BGM frameLock. B-roll QA statuses ending in `pass` count as pass.

Caption gold-spacing rule: this belongs to Phase 10 / Step 61 Caption Build and Step 61.2 Caption Gold Spacing QA, before HyperFrames render and before BGM/final mux. Gold-highlighted caption tokens must be separated from adjacent normal text. Example: `ABC` with `B` highlighted should render as `A B C`; if `BCD` needs separated highlighted tokens, render `B C D`. Run `npm run check:caption-gold` after caption HTML/style changes.

Latest v86 checkpoint: perfect workflow baseline saved after the user said "save ทุกอย่างให้เรียบร้อย นี้คือ version ที่สมบูรณ์ที่สุด". Use v86 as the clean baseline for the next development round. Accepted final MP4 remains `../preview-v80/v83-setB-final-accepted.mp4`; future workflow changes should start at v87.

Lip-sync-safe soft cut rule: never xfade or blend the visible bottom face at content cuts. The bottom face/audio pair is the lip-sync master; use hard cuts at safe speech boundaries, closed-mouth/silence points, or cover jump cuts with B-roll/bridge transitions. Always create/review cut contact sheets before calling an output final.

Timestamped clip QA rule: whenever checking a rendered clip, create a 1-second timestamped QA sheet with `npm run qa:timestamps`. Use those timestamps when reporting lip-sync, cut, caption, B-roll, BGM, or timeline issues.

Edit-first master rule: for production/full renders, finish the editorial timeline before HyperFrames layout. Create and QA frame/sample-locked `top_edit_master`, `bottom_visual_master`, `speech_audio_master`, and a `bottom_editorial_master` proof clip first. HyperFrames should render visual-only from those masters, then speech audio is muxed back after render. Do not let the background/layout stage decide or alter speech timing.

Sync rule: treat bottom audio as the master timeline. If top/bottom duration, start offset, or drift mismatch is found, notify the user before alignment/cutting decisions and align top to bottom unless the user says otherwise.

Sync lock rule: bottom audio, bottom face video, top screen video, and subtitles must stay on one edited timeline. Do not manually shift, retime, offset, or speed-change top/bottom/caption independently. B-roll may replace only top visuals and must never change the timeline. If any sync risk appears, stop and fix/report sync before continuing.

Audio cleanup rule: the true start is the first sustained speech, not the first sound Whisper can transcribe. If the opening has a short cough/word/noise followed by silence or a reset, cut that false start in parallel from top and bottom before denoise/transcription/caption. Prefer raw bottom audio for a new polish pass when the previous polished file has noise or sync risk. Use speech-first cleanup: highpass/lowpass, denoise, noise gate, compressor, loudnorm, limiter.

Logged sync compensation rule: if final stream metadata or a visible/audio sync point shows audio/video offset, compensation is allowed only after measuring it and writing the value plus reason into context/final report. Never hide this as an unreported manual offset.

Duration rule: user-provided target duration is a ceiling/meaning target, not a requirement to pad. If the user asks for 1:30 and the meaning is complete at 1:20, deliver the tighter 1:20 rather than stretching.

Whisper rule: every editing workflow requires a timestamped Whisper transcript from the polished bottom audio before context cutting or captions. If HyperFrames transcription fails, use direct `whisper-cli` or another timestamped Whisper fallback; do not proceed without transcript unless the user explicitly pauses that requirement.

When context cuts may remove important spoken terms, run `npm run check:keyterms` or explicitly report why it was not run.

Motion/BGM rule: zoom should be subtle and applied to inner top/B-roll media, not the frame wrapper. BGM is optional, must be licensed/royalty-free/generated-with-rights, loop smoothly, fade out, and stay clearly under the bottom voice.

Motion safety rule: never animate transform/scale/x/y on the top frame shell, bottom frame, or bottom face video. Slow zoom may only target inner top/B-roll media. Run `npm run check:motion` after any motion/zoom change.

B-roll transition rule: every B-roll insert must have transition mix metadata and smooth entry/exit. Use `soft` transition for normal B-roll and `bridge` transition when the B-roll covers a jump cut. Keep transitions border-stable: do not scale or move the top/bottom frame wrapper, bottom face/audio, or captions. Do not place B-roll too densely: keep at least 6s between B-roll starts and at least 3s of real top footage between inserts. If jumps are close together, choose one stronger bridge B-roll or move the weaker insert later. Run `npm run check:transition` after B-roll timing or composition changes.

B-roll density rule: do not use more than 4 B-roll inserts per 60 seconds of final video unless the user explicitly overrides it.

B-roll stock growth rule: before reusing existing B-roll as the default, try fresh Pexels candidates so the project can grow `assets/broll/index.json` toward 200 QA-passed reusable clips. Reuse before 200 only when indexed stock is clearly more relevant or API/network access blocks fresh sourcing. Report newly downloaded, reused, optimized, rejected counts every time.

When BGM is enabled, use `npm run mix:bgm` to create a mixed bottom source. Default BGM level is 5% (`--gain-percent 5`, about -26.02dB). Never claim a track is copyright-free unless its source/license is documented. Report the BGM source, license/usage-rights note, level percent, gain, ducking, output, and QA result.

Before generating or sourcing new BGM, check `bgm-library/mixkit-stock-v50.json` and run `npm run check:bgm`. Prefer a local stock track whose `bestFor` matches the clip style. Report whether the BGM was reused from stock or newly generated/downloaded.

When BGM is enabled, run `npm run select:bgm` with the title/transcript/context before mixing. Store the selector report and use its selected style/track unless listening QA shows the track distracts from speech.

If title/transcript/context is still unclear after analysis, use the default BGM fallback `mixkit-480 Curiosity` at 5%. If the clip is clearly tech but ambiguous, use `mixkit-1167 Close Up`. If speech is dense or teaching-heavy, use `mixkit-441 Meditation`.

BGM QA must include the final rendered MP4 that contains top, bottom, captions, B-roll, and final audio. Testing only the bottom source is not enough. Use `npm run qa:bgm` whenever possible; it selects BGM, mixes the final MP4, creates original/mixed previews, measures loudness, and writes a final QA report.

BGM at 5% is intentionally a barely audible ambient bed. It should make the clip feel less dry, not make the viewer notice a song. If the melody is clearly noticeable or competes with speech, reduce below 5% or choose a calmer track.

## Linting — Always Run After Changes

After creating or editing any `.html` composition, run the full check before considering the task complete:

```bash
npm run check
```

Fix all errors before presenting the result.

## B-roll Reporting — Always Include

After any task that touches B-roll selection, download, generation, optimization, or rendering, summarize:

1. How many B-roll files were newly downloaded from stock providers
2. How many B-roll files were newly generated by AI video models
3. How many existing B-roll sources were reused
4. How many optimized/re-encoded derivative files were created
5. The keyword/provider/source path for every B-roll slot
6. QA status for every slot, especially whether any candidate was rejected for text, logo, watermark, other brand, or distracting graphic

Every B-roll set must have a machine-readable manifest or index entry. Optimized derivatives should keep a `manifest.json` beside the files, mapping each slot back to its source and keyword.

After final render/QA, run `npm run report:final` when the final MP4 and reports are available. The report should include final MP4 metadata, context cut summary, B-roll counts/slots, BGM QA, key term QA, and output both JSON and Markdown.

When BGM is enabled after a full render, prefer `npm run auto:bgm` if the latest final MP4 should be selected automatically. Use `npm run qa:bgm` when the exact final MP4 path must be pinned manually.

When the final MP4, context index, B-roll manifest, and key term report are ready, prefer `npm run finalize:video` for post-render delivery. It runs Auto BGM first, then creates the final report.

Every task summary must include what changed, output/report paths, QA commands and results, and frame counts. Report edited frames such as B-roll top replacement, transition mix, zoom/motion, or overlays, plus removed frames such as dropped content, soft-cut overlap, and total net removed. Use `npm run report:frames` when context index, B-roll manifest, and final MP4 are available.

User decision gates to ask as choices when direction is missing: start/end hints, dead-air style, cut aggressiveness, B-roll on/off/count, B-roll sourcing, caption style, BGM on/off, and final render confirmation.

Single final output rule: in user-facing delivery, show only one MP4 output path: the Final file. Do not list visual-only, no-BGM, preview, master, or intermediate MP4s as outputs unless the user explicitly asks for debug/internal artifacts. Reports and QA artifacts may be mentioned separately, but not as video outputs.

Completion marker rule: when a task is fully complete and verified, the final response must include a clearly visible standalone `✅✅✅`. Do not use this marker for blocked, partial, or unverified work.

When the user wants to split the workflow into smaller projects, use the modules in `MODULES.md`: transcript, sync-inspect, context-index, edl-build, editorial-master, broll-source, caption-build, layout-render, final-mux, and final-qa. Each module must read/write files so the next session can continue without relying on chat memory.

## B-roll Keyword Selection

Before downloading, generating, or selecting B-roll, read the spoken context around the insert point:

1. Use at least one subtitle/transcript cue before and one cue after the insert point
2. Choose a keyword that represents the meaning of that moment, not just one isolated spoken word
3. Prefer broad intent/context keywords that can produce natural B-roll; avoid overly narrow literal transcript words
4. Try to download fresh candidates first until the stock index has at least 200 QA-passed clips
5. Existing QA-passed stock may be used as fallback before 200 only when it clearly matches better than fresh candidates, but report reused source count clearly
6. Record the before/after speech context, keyword, provider, source path, QA status, and category in the manifest or stock index

## Context Index — Use Before Shortening

When the goal is to shorten a clip while preserving meaning, create a timestamped context index before cutting:

1. Use bottom audio/transcript as the primary source of meaning
2. Sample the top/screen video every ~5 seconds and around important edit/B-roll points
3. Also sample before/after likely cut points and B-roll points by about 1-2 seconds
4. Store kept segments, dropped segments, reasons, topic, intent, screen context, caption keywords, B-roll keywords, and scores
5. Cut only by meaning-bearing segments, not by equal time chunks
6. Default cut aggressiveness is Medium unless the user asks otherwise
7. The user supplies the target duration or goal each time; do not force a fixed duration when meaning is better served by a nearby length
8. Use lip-sync-safe soft cuts for content cuts: top/B-roll may crossfade, but visible bottom face must not xfade
9. Use B-roll to cover jump cuts when the face/screen cut would look or sound abrupt

## Key Rules

1. Every timed element needs `data-start`, `data-duration`, and `data-track-index`
2. Visible timed elements **must** have `class="clip"` — the framework uses this for visibility control
3. GSAP timelines must be paused and registered on `window.__timelines`:
   ```js
   window.__timelines = window.__timelines || {};
   window.__timelines["composition-id"] = gsap.timeline({ paused: true });
   ```
4. Videos use `muted` with a separate `<audio>` element for the audio track
5. Sub-compositions use `data-composition-src="compositions/file.html"`
6. Only deterministic logic — no `Date.now()`, no `Math.random()`, no network fetches

## Documentation

Full docs: https://hyperframes.heygen.com/introduction

Machine-readable index for AI tools: https://hyperframes.heygen.com/llms.txt
