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

## Sync Policy

```text
masterTimeline: bottom audio
bottomPriority: true
topRole: visual screen layer only
topAudioPolicy: ignore/mute
notifyUserOnMismatch: true
durationMismatchAction: inspect before trim
startOffsetAction: find sync point and align top to bottom
driftAction: split into sync segments if needed
allowedTinyMismatch: frame/container rounding only
```

Rules:

```text
ถ้า top/bottom ความยาวไม่เท่ากัน ให้ถือ bottom สำคัญกว่าเพราะเป็นเสียงจริง
ต้องแจ้งผู้ใช้เมื่อเจอ duration mismatch, start offset, หรือ drift ที่อาจกระทบ sync
ห้ามแก้ด้วยการ time-stretch โดยไม่จำเป็น
ถ้า offset ชัด ให้หา sync point จากคำพูดเทียบกับ action บน screen แล้ว align top ให้เข้ากับ bottom
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
deadAirMinDuration: 0.5s
silenceThresholdDefault: -35dB
trimMode: parallel top/bottom only
```

## Audio Polish

```text
highpass: 80Hz
noiseReduction: afftdn nf=-25 default
compressor: threshold=-18dB ratio=3 attack=8 release=120
loudnessTarget: -16 LUFS
truePeakMax: -1.5 dBTP
lra: 11
limiter: 0.95
audioBitrate: 192k
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
contextIndex: Full
screenSampling: every ~5s plus cut/B-roll neighborhoods
softCutAlways: true
defaultCrossfade: 0.12s
crossfadeIfHarsh: 0.15-0.18s
crossfadeIfSlow: 0.08-0.10s
preserveKeyTerms: true
```

## Motion Zoom

```text
zoomEnabled: true
zoomPurpose: emphasis, B-roll energy, soft cut cover
applyZoomTo: top inner media, B-roll inner media, optional caption highlight
avoidZoomOn: bottom face video unless explicitly requested
subtleZoomScale: 1.00 -> 1.035
maxZoomScale: 1.06
punchZoomScale: 1.00 -> 1.045 -> 1.00
slowZoomDuration: 2.0s-3.0s
punchZoomDuration: 0.45s-0.80s
minimumGapBetweenZooms: 2s
zoomFrameRule: transform inner media only, not frame/border wrapper
```

## BGM Loop

```text
bgmEnabled: optional
bgmSource: assets/bgm/*
bgmTrackedIndex: bgm-library/mixkit-stock-v49.json
bgmRuntimeIndex: assets/bgm/index.json
bgmRuntimeStockRoot: assets/bgm/stock/mixkit
bgmStockCount: 15
bgmCheckCommand: npm run check:bgm
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
suggestedBgmGain: -26.02dB default, equivalent to 5% linear amplitude
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
usualCount: 5-10
test2StyleCount: 10
replaceArea: top frame only
audio: muted/no audio
providerOrder: Pexels API -> OpenRouter google/veo-3.1-lite -> OpenRouter kwaivgi/kling-v3.0-std
candidatePerSlotFinal: 3
orientation: landscape
minimumResolution: HD
qaReject: text, logo, watermark, other brand, distracting graphic
optimizedFormat: 1920x1080, 30fps, GOP 30, faststart, no audio
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
