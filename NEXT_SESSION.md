# Next Session Handoff

สถานะล่าสุด: v58 - เพิ่ม post-render finalize command

วันที่บันทึก: 2026-05-19

## Saved Checkpoints

```text
v53 tag: v53-auto-bgm-selector
v53 commit: f6aba92 Add automatic BGM selector
v54 commit: 5a90e2f Add automatic final BGM QA
v55 commit: f897a32 Add next session handoff
v56 commit: 145f10f Add final report generator
v57 commit: 485facb Add auto final BGM wrapper
current branch: main
repo: https://github.com/gobank01/bizdrive-video-workflow
```

## What Is Done

```text
1. BGM stock library มี 15 เพลงจาก Mixkit
2. default BGM level = 5%
3. BGM intent = แทบไม่ได้ยิน / felt more than heard
4. default fallback = mixkit-480 Curiosity
5. Auto BGM Selector เลือกเพลงจาก title/transcript/context ได้
6. Auto Final BGM QA เลือกเพลง, mix final MP4 จริง, สร้าง preview, วัด loudness และออก report ได้
7. v53 checkpoint ถูก tag และ push แล้ว
8. Final Report Generator รวม final MP4 metadata, context, B-roll, BGM QA, key term QA เป็น JSON + Markdown ได้
9. Auto Final BGM wrapper เลือก final MP4 ล่าสุดที่ไม่ใช่ preview/BGM แล้วเรียก QA BGM ต่อได้
10. Finalize command รวม Auto BGM + Final Report หลัง render ได้ในคำสั่งเดียว
```

## Commands Now Available

เลือก BGM:

```bash
npm run select:bgm -- \
  --title "หัวข้อคลิป" \
  --context assets/context/test2-v35-full-context-index.json \
  --transcript assets/transcript_test2.large-v3.json \
  --output reports/bgm-select-v53.json
```

QA BGM กับ final MP4 จริง:

แบบเลือก final MP4 ล่าสุดอัตโนมัติ:

```bash
npm run auto:bgm -- \
  --title "หัวข้อคลิป" \
  --context assets/context/test2-v35-full-context-index.json \
  --transcript assets/transcript_test2.large-v3.json
```

แบบระบุไฟล์เอง:

```bash
npm run qa:bgm -- \
  --final ../stacked-output-v35-test2-full-context-softcut-broll-full-test.mp4 \
  --title "หัวข้อคลิป" \
  --context assets/context/test2-v35-full-context-index.json \
  --transcript assets/transcript_test2.large-v3.json \
  --output ../stacked-output-v54-auto-bgm-qa-test.mp4 \
  --report reports/bgm-final-qa-v54-test2.json
```

ตรวจ BGM stock:

```bash
npm run check:bgm
```

สร้าง final report:

```bash
npm run report:final -- \
  --final ../stacked-output-v54-auto-bgm-qa-test.mp4 \
  --context assets/context/test2-v35-full-context-index.json \
  --broll-manifest assets/broll/optimized/test2-v35/manifest.json \
  --bgm-qa reports/bgm-final-qa-v54-test2.json \
  --keyterm-report reports/keyterm-test2-v45.json \
  --json reports/final-report-v56-test2.json \
  --markdown reports/final-report-v56-test2.md
```

Finalize หลัง render:

```bash
npm run finalize:video -- \
  --title "หัวข้อคลิป" \
  --context assets/context/test2-v35-full-context-index.json \
  --transcript assets/transcript_test2.large-v3.json \
  --broll-manifest assets/broll/optimized/test2-v35/manifest.json \
  --keyterm-report reports/keyterm-test2-v45.json
```

## Latest Verified Test

Input final:

```text
../stacked-output-v35-test2-full-context-softcut-broll-full-test.mp4
```

Auto BGM QA output:

```text
../stacked-output-v54-auto-bgm-qa-test.mp4
```

Auto-selected BGM:

```text
selectedStyle: tech_explainer
selectedTrack: mixkit-175 Digital Clouds
gainPercent: 5
audibilityIntent: barely audible ambient bed, felt more than heard
```

Measured result:

```text
original final: -16.0 LUFS, true peak -1.0 dBFS
BGM final:      -16.1 LUFS, true peak -1.7 dBFS
qa.status: pass
```

Preview files:

```text
../stacked-output-v35-test2-full-context-softcut-broll-full-test-preview20s-original.mp4
../stacked-output-v54-auto-bgm-qa-test-preview20s.mp4
```

Final report test:

```text
reports/final-report-v56-test2.json
reports/final-report-v56-test2.md
status: review
reason: B-roll QA pass, BGM QA pass, key term QA warn from existing v45 report missing "prompt"
```

Auto BGM wrapper test:

```text
command: npm run auto:bgm -- --title ... --context ... --transcript ...
selectedFinal: ../stacked-output-v35-test2-full-context-softcut-broll-full-test.mp4
output: ../stacked-output-v35-test2-full-context-softcut-broll-full-test-auto-bgm-5pct.mp4
report: reports/stacked-output-v35-test2-full-context-softcut-broll-full-test-auto-bgm-qa.json
selectedStyle: tech_explainer
selectedTrack: mixkit-175 Digital Clouds
qa.status: pass
original final: -16.0 LUFS, true peak -1.0 dBFS
BGM final:      -16.1 LUFS, true peak -1.7 dBFS
```

Finalize command test:

```text
command: npm run finalize:video -- --title ... --context ... --transcript ... --broll-manifest ... --keyterm-report ...
selectedFinal: ../stacked-output-v35-test2-full-context-softcut-broll-full-test.mp4
bgmOutput: ../stacked-output-v35-test2-full-context-softcut-broll-full-test-auto-bgm-5pct.mp4
finalReportJson: reports/stacked-output-v35-test2-full-context-softcut-broll-full-test-final-report.json
finalReportMarkdown: reports/stacked-output-v35-test2-full-context-softcut-broll-full-test-final-report.md
BGM QA: pass
B-roll QA: pass
Final report status: review
reason: key term QA warn from existing v45 report missing "prompt"
```

## Tomorrow Recommended Next Work

1. **Unified Context Decision**
   - Use the same context index to drive both B-roll and BGM.
   - Store `clipStyle`, `brollIntent`, `bgmStyle`, and `reason` in one report.

2. **Full Pipeline Orchestrator**
   - Later combine: inspect -> cut -> captions -> B-roll -> render -> finalize.
   - Target command: `npm run bizdrive:render`.

3. **Run On A New Real Job Folder**
   - The current system is proven on Test 2.
   - Next important proof is running it on the next raw top/bottom pair.

## Important Rules To Keep

```text
BGM remains 5% by default.
BGM should be barely audible.
If melody is clearly noticeable, it is too loud.
Always test BGM on final MP4, not only bottom source.
Never claim copyright-free without source/license.
Bottom audio remains master.
Top/bottom trims and cuts remain parallel.
```
