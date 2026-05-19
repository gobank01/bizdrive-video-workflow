# Bizdrive Lip-Sync QA

Lip sync เป็น zero-tolerance gate สำหรับ workflow นี้ ถ้าปากกับเสียงไม่ตรง ห้ามส่ง final

## Principle

```text
bottom audio คือ master clock
bottom face video ต้องตรงกับ bottom audio แบบ frame-accurate
top video และ captions ต้องตาม edited bottom-master timeline
B-roll เปลี่ยนได้เฉพาะ top visual ห้ามกระทบ bottom/audio/caption timing
```

## What Counts As Failure

```text
เสียงนำปาก
เสียงตามปาก
ปากเริ่มขยับก่อนเสียงพยัญชนะชัด
เสียงพยัญชนะชัดมาก่อนปากเปิด
sync ดูดีใน intermediate แต่ final MP4 มี stream start_time ต่างกันโดยไม่ compensate/log
caption ตรงกับเสียงแต่ bottom face ไม่ตรงกับเสียง
ภาพปากซ้อน/ghost frame/double-mouth จากการ xfade bottom face ตอน bottom circle visible
```

ถ้าผู้ใช้รู้สึกว่า lip sync ไม่ตรง ให้ถือว่า fail จนกว่าจะพิสูจน์และแก้

## Required Checks Before Render

```text
1. raw top/bottom ffprobe duration, fps, stream start_time
2. bottom audio source selected with evidence
3. every trim/dead-air/context cut uses the same cut list for top and bottom
4. no independent speed change, offset, retime, or frame shift on bottom face/audio
5. intermediate top/bottom video frame count and duration match, except documented container rounding
6. caption cues are generated/remapped after final edited timeline is known
7. content cut strategy is lip-sync-safe: no bottom-face xfade while bottom circle is visible
```

## Required Checks After Render

```text
1. ffprobe final MP4 video/audio stream start_time
2. ffprobe final MP4 video frame count and audio duration
3. compare final stream start_time delta in milliseconds
4. if delta is non-zero, decide whether it is container-only or visible sync risk; log decision
5. create a timestamped QA sheet with one labeled frame per second
6. visual/audio spot-check at minimum 5 points:
   - first clear speech in first 3 seconds
   - first hard consonant / plosive after hook
   - after every major soft cut
   - around every B-roll bridge cut
   - final CTA
7. cut contact sheet around every content cut shows no ghost/double-mouth frame
8. if any check is uncertain, create a short sync review clip around the suspect timestamp
```

## Allowed Compensation

Sync compensation is allowed only when measured and logged.

```text
allowed:
  - apply audio delay/advance by measured ms when final stream or spot-check proves offset
  - rebuild from raw bottom audio if prior audio pipeline introduced drift
  - split/rebuild segments if drift changes over time

forbidden:
  - hidden manual offset
  - guessing delay by feel without recording evidence
  - fixing only captions while face/audio remains off
  - time-stretching one layer independently without explicit logged reason
  - xfade bottom face while it is visible
  - using metadata-only compensation to hide ghost-mouth frames at cuts
```

## Reporting Required

Every final summary must include:

```text
lipSyncStatus: pass/fail/blocked
rawSyncEvidence: top/bottom raw duration, fps, start_time
intermediateSyncEvidence: top/bottom edited frame count and duration
finalStreamStartDeltaMs: video start_time - audio start_time
compensationMs: value or none
spotCheckPoints: timestamps checked
timestampQaSheet: path to every-1s timestamp sheet
residualRisk: none / needs human review / blocked
```

## Stop Rule

ถ้า lip sync ยังไม่มั่นใจ 100% ให้หยุดและรายงานว่า blocked ห้ามเรียกว่า final
