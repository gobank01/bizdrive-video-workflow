# Bizdrive Video Config

ไฟล์นี้รวมค่าที่แก้ได้ก่อนเริ่มงานหรือก่อนแจก workflow ต่อ

## Editable Key Terms

แก้รายการนี้ตามโปรเจกต์ ก่อนทำ context cut

```text
B-roll
caption
prompt
Dead Air
audio polish
intro
outro
thumbnail
export
AI
```

Rules:

```text
เพิ่ม feature/product/service/framework/model ที่เป็นแกนของคลิป
ใส่ variant ที่ผู้พูดใช้จริง เช่น B-roll, b roll, บีโรล
ถ้ามีคำถอดเสียงผิด ให้ใส่ mapping เช่น พร้อม -> prompt
ห้ามใส่ filler words เช่น อืม, อะ, เอ่อ
```

## Media

```text
compositionWidth: 1080
compositionHeight: 1920
targetFps: 30
gop: 30
faststart: true
topMuted: true
bottomHasAudio: true
```

## Mistake Prevention

```text
mistakeLog: MISTAKES.md
lipSyncQa: LIPSYNC_QA.md
readMistakeLogBeforeEveryEdit: true
blockFinalIfHardGateFails: true
openingGate: true start must be sustained speech, not first detectable sound
audioSourceGate: choose raw vs polished source with evidence
noiseGate: opening false start/noise checked before and after polish
syncMetadataGate: final ffprobe video/audio stream start_time checked after render
lipSyncZeroTolerance: true
lipSyncSpotCheckMinimum: 5
lipSyncBlockIfUncertain: true
captionMapGate: captions remapped after every trim/dead-air/context cut
summaryGate: final summary reports prevention gate status
timestampQaRequired: true
timestampQaIntervalSeconds: 1
```

## Sync Policy

```text
masterTimeline: bottom audio
bottomPriority: true
topRole: visual screen layer only
topAudioPolicy: ignore/mute
syncLockRequired: true
frameAccurateSync: true
lipSyncZeroTolerance: true
lipSyncQaRequired: true
lipSyncSpotCheckMinimum: 5
lipSyncPassRequiresResidualRiskNone: true
timelineUnit: edited bottom-master timeline
rawBottomHumanLipSyncGate: required
metadataSyncIsNotEnough: true
blockSetOnHumanLipSyncFail: true
notifyUserOnMismatch: true
durationMismatchAction: inspect before trim
startOffsetAction: find sync point and align top to bottom
driftAction: split into sync segments if needed
allowedTinyMismatch: frame/container rounding only
manualOffsetPolicy: forbidden unless logged and user-approved
independentRetimingPolicy: forbidden
captionTimingPolicy: generate/map captions after all trim/dead-air/context cuts
bottomFaceXfadeWhileVisible: forbidden
bottomCutStrategy: hard cut at safe speech boundary or cover jump with B-roll/bridge
cutContactSheetRequired: true
timestampedClipQaSheetRequired: true
```

Rules:

```text
ถ้า top/bottom ความยาวไม่เท่ากัน ให้ถือ bottom สำคัญกว่าเพราะเป็นเสียงจริง
ต้องแจ้งผู้ใช้เมื่อเจอ duration mismatch, start offset, หรือ drift ที่อาจกระทบ sync
ห้ามแก้ด้วยการ time-stretch โดยไม่จำเป็น
ถ้า offset ชัด ให้หา sync point จากคำพูดเทียบกับ action บน screen แล้ว align top ให้เข้ากับ bottom
เสียง, top, bottom และ subtitles ต้องตรง timeline เดียวกันแบบ frame-accurate
ถ้า sync ไม่ผ่าน ให้หยุดแก้ sync ก่อน ห้ามไป step ถัดไป
ถ้า metadata ตรงแต่ human review บอกว่าปากไม่ตรง ให้ถือว่า fail ทันที และ block set นั้น
```

## Layout

```text
topX: 0
topY: 198.9
topWidth: 1080
topHeight: 607.5
topRadius: 30
topBorderWidth: 4

bottomX: 50%
bottomY: 846.4
bottomWidth: 607.5
bottomHeight: 607.5
bottomRadius: 50%
bottomBorderWidth: 4

gapTopBottom: ~40
borderStyle: yellow/gold gradient with visible glow
```

## Trim And Dead Air

```text
trueStartRule: start where speech continues 30s+
falseStartRule: if an early sound/word is followed by silence or reset before sustained speech, drop that false start
deadAirMinDuration: 0.5s
silenceThresholdDefault: -35dB
trimMode: parallel top/bottom only
```

## Audio Polish

```text
preferredSource: raw bottom.mp4 unless a prior polished source is verified clean and in sync
highpass: 90Hz
lowpass: 12000Hz
noiseReduction: afftdn nr=14 nf=-42 tn=1 rf=-38 gs=8
noiseGate: agate threshold=0.015 ratio=2.5 attack=6 release=140 range=0.12 detection=rms
compressor: threshold=-20dB ratio=2.5 attack=8 release=160 makeup=1.35
loudnessTarget: -16 LUFS
truePeakMax: -1.5 dBTP
lra: 9
limiter: 0.95
audioBitrate: 192k
syncCompensation: allowed only when measured/logged; example v66 used 21ms audio delay after final stream showed video start 0.021s and audio start 0.000s
```

## Caption

```text
font: IBM Plex Sans Thai + Inter
normalWeight: 800
highlightWeight: 900
color: #FFFFFF
captionTop: 1490px
captionHeight: 160px
captionMarginX: 60px
maxCharsDefault: 20
targetChars: 14
hardMaxChars: 22
noThaiMidWordBreak: true
removeFillers: อืม, อะ, อ่ะ, เอ่อ
goldHighlight: #FFD93D -> #F4C20F -> #B8860B
goldBaseline: same as normal text
goldSpacing: proportional, about 0.04em
```

## Context Cut

```text
defaultAggressiveness: Medium
targetDuration: user-provided per job
targetDurationPolicy: ceiling/meaning-first
underTargetAllowed: true
example: if target is 90s but meaning is complete at 80s, use 80s
doNotPadToTarget: true
contextIndex: Full
screenSampling: every ~5s plus cut/B-roll neighborhoods
softCutAlways: true
softCutMode: lip-sync-safe
defaultCrossfade: 0.12s for top/B-roll only
bottomVisibleCrossfade: forbidden
crossfadeIfHarsh: 0.15-0.18s
crossfadeIfSlow: 0.08-0.10s
preserveKeyTerms: true
```

## Transcription

```text
whisperRequired: true
preferredModel: large-v3
preferredLanguage: th
preferredInput: bottom_audio_polished
fallback: direct whisper-cli with timestamped JSON
blockContextWithoutTranscript: true
blockCaptionsWithoutTranscript: true
rawTranscriptPathPolicy: keep under assets/context or assets/transcripts, not project root
```

## Motion Zoom

```text
zoomEnabled: true
zoomPurpose: emphasis, B-roll energy, soft cut cover
applyZoomTo: top inner media, B-roll inner media, optional caption highlight
avoidZoomOn: bottom face video always, unless a future user explicitly changes the rule
topSlowZoomScale: 1.000 -> 1.018 -> 1.006 across the full clip
brollSlowZoomScale: 1.006 -> 1.022 across each 3s B-roll
maxZoomScale: 1.025
punchZoomScale: disabled by default
slowZoomDuration: full visible segment / full B-roll duration
minimumGapBetweenZooms: not applicable for continuous slow inner-media movement
zoomFrameRule: transform inner media only, never frame/border wrapper
motionSafetyQaCommand: npm run check:motion
```

## Transition Mix

```text
transitionMixEnabled: true
defaultBrollTransition: soft-crossfade-pan
jumpCutBrollTransition: bridge-crossfade-pan
softTransitionIn: 0.22s
softTransitionOut: 0.22s
bridgeTransitionIn: 0.26s
bridgeTransitionOut: 0.26s
transitionEaseIn: power2.out / power3.out for bridge
transitionEaseOut: power2.out / power2.inOut for bridge
panRange: 49%-51% object-position only
borderStable: true
applyTo: B-roll/top-frame media opacity, filter, object-position
avoid: scaling frame wrapper, moving top/bottom border, moving captions
bridgeRule: if B-roll covers a jump cut, use bridge mode and let B-roll overlap the cut point
bridgePurpose: cover bottom/top jump cuts without xfade blending visible bottom mouth frames
spacingRule: do not place 2 B-rolls inside the same 6s viewing window
minBrollStartGap: 6s
minRealTopFootageGap: 3s
denseClusterFallback: choose the stronger B-roll, move the weaker slot later, or cover the jump with one bridge B-roll instead of two rapid inserts
qaCommand: npm run check:transition
```

## BGM Loop

```text
bgmEnabled: optional
bgmSource: assets/bgm/*
bgmTrackedIndex: bgm-library/mixkit-stock-v50.json
bgmSelectorCommand: npm run select:bgm
bgmFinalQaCommand: npm run qa:bgm
bgmSelectorKeywords: bgm-library/style-keywords-v53.json
bgmRuntimeIndex: assets/bgm/index.json
bgmRuntimeStockRoot: assets/bgm/stock/mixkit
bgmStockCount: 15
bgmCheckCommand: npm run check:bgm
bgmDefaultFallback: mixkit-480 Curiosity
bgmDefaultFallbackPath: assets/bgm/stock/mixkit/mixkit-480-curiosity.mp3
bgmTechFallback: mixkit-1167 Close Up
bgmCalmFallback: mixkit-441 Meditation
bgmSourcePolicy: user-provided licensed, royalty-free with documented terms, generated with usage rights, or internal verified stock only
bgmAutoSource: allowed only when license/source is recorded before final render
bgmSelectionOrder: local stock index -> generated OpenRouter/Lyria -> user-provided licensed track
bgmLoop: true
bgmFadeIn: 0.5s
bgmFadeOut: 1.0s
bgmAllowed: licensed, royalty-free, generated-with-usage-rights only
bgmAvoid: vocals, audio tags, watermark, distracting melody
speechPriority: true
bgmDefaultLevel: 5%
bgmAudibilityIntent: barely audible, felt more than heard
bgmTooLoudRule: if the melody is clearly noticeable or pulls attention from speech, reduce below 5% or change track
suggestedBgmGain: -26.02dB default, equivalent to 5% linear amplitude
bgmLimiterLimit: 0.80
duckingDuringSpeech: -6dB to -12dB if BGM distracts
finalAudioMix: bottom polished voice + BGM
mixCommand: npm run mix:bgm
defaultBgmOutput: assets/bottom_audio_polished_bgm.mp4
defaultBgmReport: reports/bgm-mix-vXX.json
```

## B-roll

```text
defaultDuration: 3s
minimumCount: 3
maxPerMinute: 4
countFormula: min(user requested count, floor(finalDurationSeconds / 60 * 4))
usualCount: 3-4 per minute
test2StyleCount: deprecated; obey maxPerMinute unless user explicitly overrides
replaceArea: top frame only
audio: muted/no audio
providerOrder: Pexels API -> OpenRouter google/veo-3.1-lite -> OpenRouter kwaivgi/kling-v3.0-std
freshDownloadFirst: true
stockIndexPath: assets/broll/index.json
stockTargetQaPassedCount: 200
reuseDefaultAfterStockTarget: true
reuseBeforeTarget: only if indexed stock is clearly more relevant than new candidates or network/API fails
indexEveryDownloadedCandidate: true
indexEveryRejectedCandidate: true
candidatePerSlotFinal: 3
orientation: landscape
minimumResolution: HD
qaReject: text, logo, watermark, other brand, distracting graphic
optimizedFormat: 1920x1080, 30fps, GOP 30, faststart, no audio
```

## Work Updates

```text
progressUpdatesRequired: true
progressUpdateFormat: Step N - what is being checked or changed
progressUpdateBeforeLongCommand: true
progressUpdateAfterFailedCheck: true
doNotSkipStepNarration: true
```

## Reporting

```text
alwaysReportOutputPath: true
alwaysReportVersion: true
alwaysReportMetadata: true
alwaysReportCheckResult: true
alwaysReportBrollCounts: true
alwaysReportBrollSlotMapping: true
alwaysReportQaArtifacts: true
```
