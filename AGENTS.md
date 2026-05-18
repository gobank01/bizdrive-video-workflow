# HyperFrames Composition Project

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

## Bizdrive Workflow Docs — v54

For Bizdrive stacked-video work, read these files in order:

1. `WORKFLOW.md` — current overview and latest production defaults
2. `STEPS.md` — practical 62-step execution list for real editing
3. `CONFIG.md` — editable settings such as key terms, layout, audio, captions, and B-roll provider order
4. `QA.md` — required QA checklists
5. `SYNC_REPORT.md` — sync mismatch/bottom-master reporting template
6. `KEYTERM_QA.md` — key term preservation QA rules
7. `MOTION_BGM.md` — zoom motion and BGM loop rules
8. `BGM_LIBRARY.md` — BGM stock index and style map
9. `REPORT_TEMPLATE.md` — final report format
10. `CHANGELOG.md` — workflow version history

`STEPS_PRACTICAL_99.md` is an archived 99-step reference. Use it only when the 62-step edit map needs more detail.

`STEPS_DETAILED_425.md` is a detailed automation reference. Use it when building scripts or expanding the workflow, but use `STEPS.md` as the current edit map.

`FULL_WORKFLOW_ARCHIVE.md` is historical reference only. Do not treat it as the latest source of truth unless a detail is missing from the split docs.

Every workflow rule change increments the version and must be recorded in `CHANGELOG.md`. If the change affects execution, update `STEPS.md` and/or `CONFIG.md` instead of burying it only in prose.

Sync rule: treat bottom audio as the master timeline. If top/bottom duration, start offset, or drift mismatch is found, notify the user before alignment/cutting decisions and align top to bottom unless the user says otherwise.

When context cuts may remove important spoken terms, run `npm run check:keyterms` or explicitly report why it was not run.

Motion/BGM rule: zoom should be subtle and applied to inner top/B-roll media, not the frame wrapper. BGM is optional, must be licensed/royalty-free/generated-with-rights, loop smoothly, fade out, and stay clearly under the bottom voice.

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

## B-roll Keyword Selection

Before downloading, generating, or selecting B-roll, read the spoken context around the insert point:

1. Use at least one subtitle/transcript cue before and one cue after the insert point
2. Choose a keyword that represents the meaning of that moment, not just one isolated spoken word
3. Prefer broad intent/context keywords that can produce natural B-roll; avoid overly narrow literal transcript words
4. Try to download fresh candidates for final-quality work when better context matching is possible
5. Existing QA-passed stock may be used as fallback, but report reused source count clearly
6. Record the before/after speech context, keyword, provider, and source path in the manifest

## Context Index — Use Before Shortening

When the goal is to shorten a clip while preserving meaning, create a timestamped context index before cutting:

1. Use bottom audio/transcript as the primary source of meaning
2. Sample the top/screen video every ~5 seconds and around important edit/B-roll points
3. Also sample before/after likely cut points and B-roll points by about 1-2 seconds
4. Store kept segments, dropped segments, reasons, topic, intent, screen context, caption keywords, B-roll keywords, and scores
5. Cut only by meaning-bearing segments, not by equal time chunks
6. Default cut aggressiveness is Medium unless the user asks otherwise
7. The user supplies the target duration or goal each time; do not force a fixed duration when meaning is better served by a nearby length
8. Use soft cuts for all content cuts, then re-encode GOP 30 / faststart before HyperFrames render
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
