# v69 Lip-Sync Root Cause Report

Date: 2026-05-19

## Trigger

User reported that lip sync still appeared wrong after v66/v68 safeguards.

## Evidence Checked

```text
Final output checked:
/Users/gobank01/Documents/Video V2/stacked-output-v66-video2-noise-sync-fix.mp4

Diagnostics generated:
diagnostics/lipsync-v68/final-mouth-sheet.jpg
diagnostics/lipsync-v68/intermediate-mouth-sheet.jpg
diagnostics/lipsync-v68/final-wave-0-0.7.jpg
diagnostics/lipsync-v68/intermediate-wave-0-0.7.jpg
diagnostics/lipsync-v68/raw-mouth-sheet.jpg
diagnostics/lipsync-v68/raw-wave-2.2-2.9.jpg
diagnostics/lipsync-v68/final-cut-mouth-sheet.jpg
```

## Findings

```text
1. Final MP4 stream metadata still shows video start_time 0.021s and audio start_time 0.000s.
2. Final opening audio has a larger low/silent onset than the intermediate, so final encode/render can alter perceived audio onset.
3. The larger root cause is at content cuts: the v66 builder applied xfade to bottom face video and acrossfade to bottom audio.
4. Contact sheet around final content cuts shows visible ghost/double-mouth frames during xfade.
5. This creates fake mouth positions that can never match a single spoken syllable.
```

## Root Cause

```text
The workflow treated "soft cut" as xfade/acrossfade for both top and bottom.
That is unsafe when bottom face remains visible.

For a talking head, bottom face video and bottom audio are one locked source.
Crossfading two non-contiguous face segments blends two different mouth shapes.
Crossfading two speech segments blends two different phonemes.
The result can look like lip-sync drift even if frame counts and durations match.
```

## What Was Wrong In v66

```text
scripts/build-video2-v66-noise-sync-fix.js

buildVideoFilter() used xfade for every keep segment.
The same buildVideoFilter() was used for TOP_SOURCE and BOTTOM_SOURCE.
buildAudioFilter() used acrossfade for bottom audio.
SYNC_AUDIO_DELAY_MS=21 was based on final stream start_time metadata, but that did not solve ghost-mouth frames at cuts.
```

## New Rule

```text
Soft cut is still allowed, but it must be lip-sync-safe.

Allowed:
- top screen xfade
- B-roll entry/exit transition
- B-roll bridge covering a jump cut
- audio microfade only when it does not smear speech or key terms
- bottom hard cut only at safe speech boundary, silence, or closed-mouth point

Forbidden:
- xfade bottom face while the bottom circle is visible
- crossfade speech over visible mouth movement when it smears words
- claiming lip sync pass from metadata/frame count without visual cut contact sheet
```

## Required Next Fix

```text
Build v69+ edit pipeline:
1. Rebuild context cuts with bottom face/audio locked.
2. Do not xfade bottom visible face.
3. Use B-roll/bridge transition to cover any jump that would look harsh.
4. Generate a cut contact sheet around every content cut.
5. Only call output final if no ghost/double-mouth frames and residualRisk=none.
```
