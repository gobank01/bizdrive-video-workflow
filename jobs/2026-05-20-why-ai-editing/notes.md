# Job Notes — 2026-05-20 why-ai-editing

**Title:** ทำไมจึงควรใช้ AI ตัดต่อ
**Template:** 01-stacked-vertical-burst
**Status:** complete — user accepted ("งานทำได้ดี Perfect")

## What this job is

BIZDRIVE direct-response clip explaining why creators should use AI to edit video. Core argument: recording a clip takes only 1-2 minutes, but editing it takes 15-30+ minutes — AI closes that gap.

## Pipeline run (v88, all 15 steps)

1. Raw: 97.92s, top.mp4 (28MB screen) + bottom.mp4 (154MB face), 1920×1080 30fps, synced
2. ElevenLabs transcribe → 41 phrase entries
3. Editorial subagent → trim 1.68-97.80s, dropped repeated "ใช้ AI ไปเลย" + outro click SFX
4-7. Pad-bleed + VAD jump-cut + parallel top/bottom trim → masters 2753 frames @ 92.149s
8. Audio polish 2-pass loudnorm → -17.5 LUFS
9. Re-transcribe polished → 37 words on edited timeline
10. Post-process subagent → 41 caption groups, 15 gold tokens
11-13. Burst captions + lint (0/0) + render (5m26s, 2764 frames)
14. B-roll: 4 clips via seedance-1-5-pro (~$0.08), inserts at 15/35/55/75s
15. Mux speech + BGM 5% → final.mp4

## Decisions

- **bg.png**: this clip had no background image; reused the BIZDRIVE brand bg.png from `raw-media/2026-04-23-bizdrive-stock-promo/bg.png`.
- **Folder slug**: the user typed a Thai job name with spaces. Renamed the directory to the ASCII slug `2026-05-20-why-ai-editing` (shell-safe); the Thai title is preserved in `manifest.json` `title`.
- **B-roll model**: seedance-1-5-pro (the cheaper default locked in on 2026-05-20).
- **B-roll context**: abstract editing/AI visuals (timeline, clock, neural pipeline, finished video) — prompts said no text/no logos to avoid fake UI text.

## Output

`output/finals/final.mp4` — 92.154s, 2764 frames, 1080×1920, 41.4 MB, BGM 5%.

## Don't change this job

Accepted as-is. To iterate, clone or scaffold a new job.
