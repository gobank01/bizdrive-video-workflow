# Final Report Template

ใช้ template นี้หลัง render หรือหลังจบงานวิดีโอ

สร้างรายงานอัตโนมัติ:

```bash
npm run report:final -- \
  --final ../final.mp4 \
  --context assets/context/job-context.json \
  --broll-manifest assets/broll/optimized/job/manifest.json \
  --bgm-qa reports/bgm-final-qa.json \
  --keyterm-report reports/keyterm-job.json \
  --json reports/final-report-job.json \
  --markdown reports/final-report-job.md
```

คำสั่งนี้จะรวม metadata ของ final MP4, context cut, B-roll manifest, BGM QA, key term QA และสร้างทั้ง JSON + Markdown

หลัง render เสร็จ ถ้าต้องการทำ BGM + final report ในคำสั่งเดียว:

```bash
npm run finalize:video -- \
  --title "หัวข้อคลิป" \
  --context assets/context/job-context.json \
  --transcript assets/transcript-job.json \
  --broll-manifest assets/broll/optimized/job/manifest.json \
  --keyterm-report reports/keyterm-job.json
```

## Summary

```text
version:
output:
status:
goal:
```

## Render Metadata

```text
duration:
size:
video:
audio:
file size:
```

## Source Media

```text
top source:
bottom source:
background:
trim:
dead air removed:
soft cut:
```

## Sync

```text
sync report:
master timeline:
top duration:
bottom duration:
duration delta:
start offset:
drift:
user notified:
decision:
```

## Audio

```text
audio source:
polish chain:
loudness:
true peak:
BGM source:
BGM source/license:
BGM stock index:
BGM selector report:
BGM selected style:
BGM stock id/title:
BGM style match:
BGM final real file test:
BGM final QA report:
BGM original final loudness:
BGM mixed final loudness:
BGM original preview:
BGM mixed preview:
BGM mixed output:
BGM loop:
BGM level percent:
BGM audibility intent:
BGM audibility QA:
BGM gain/ducking:
BGM mix report:
notes:
```

## Motion

```text
zoom enabled:
zoom targets:
zoom max scale:
zoom timing:
motion QA:
```

## Captions

```text
transcript source:
cue count:
max cue length:
style:
key term preservation:
key term QA report:
```

## B-roll Report

```text
new stock downloads:
new AI generations:
reused sources:
optimized derivatives:
rejected candidates:
manifest:
```

Slot mapping:

```text
slot 01:
slot 02:
slot 03:
slot 04:
slot 05:
slot 06:
slot 07:
slot 08:
slot 09:
slot 10:
```

## QA

```text
npm run check:
layout:
console:
B-roll QA:
caption QA:
audio QA:
motion QA:
BGM QA:
key term QA:
sync QA:
contact sheets:
```

## Files Updated

```text
-
-
-
```

## Notes / Next Step

```text
-
```
