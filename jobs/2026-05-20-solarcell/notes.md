# Job Notes — 2026-05-20 solarcell

**Title:** โซลาร์เซลล์ — On Grid / Off Grid / Hybrid
**Template:** 01-stacked-vertical-burst
**Status:** complete

## What this job is

BIZDRIVE explainer on solar cells — the 3 installation types (On Grid, Off
Grid, Hybrid) and how they differ.

## Pipeline run (v88, all 15 steps)

1. Raw: 107.221s, top.mp4 (60MB screen) + bottom.mp4 (103MB face), 1920x1080 30fps
2. ElevenLabs transcribe -> 56 phrase entries
3. Editorial subagent -> trim 10.72-102.14s; dropped 10s pre-roll recording-test
   chatter, 5s trailing banter, and stutter-duplicated terms (kept last take)
4-7. Pad-bleed + VAD jump-cut (27 speech ranges) + parallel trim -> masters 2461 frames @ 83.475s
8. Audio polish 2-pass loudnorm -> -17.7 LUFS
9. Re-transcribe polished -> 48 words on edited timeline
10. Post-process subagent -> 50 caption groups, 20 gold (On Grid/Off Grid/Hybrid)
11. set-duration.py 83.475260 + build-burst-captions.py
12-13. add-broll.py 12 32 52 70 + lint (0/0) + render (2m40s, 2504 frames)
14. B-roll: 4 clips via seedance-1-5-pro (broll-04 fell back to seedance-2.0-fast)
15. Mux speech + BGM 5% -> final.mp4

## First job on the refactored Template 01

This is the first job that used the new generic-path template — no manual
sed path-fixing was needed. Step 11 was just three scripts:
set-duration.py -> build-burst-captions.py -> add-broll.py.

## Known cosmetic note

`npm run check` printed a StaticGuard message about `hf-video-0` having no
src. Root cause: the template index.html had a literal `<video>` tag inside an
HTML comment, which HyperFrames' guard scanned. It did NOT affect the render
(2504 frames produced fine). The comment was reworded in the template and this
workspace so future jobs don't see the message.

## Output

`output/finals/final.mp4` — 83.488s, 2504 frames, 1080x1920, 38 MB, BGM 5%.
