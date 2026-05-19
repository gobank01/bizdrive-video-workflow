# Next Session Handoff

สถานะล่าสุด: v59 - เพิ่ม B-roll Transition Mix Engine

วันที่บันทึก: 2026-05-19

## Saved Checkpoints

```text
v53 tag: v53-auto-bgm-selector
v53 commit: f6aba92 Add automatic BGM selector
v54 commit: 5a90e2f Add automatic final BGM QA
v55 commit: f897a32 Add next session handoff
v56 commit: 145f10f Add final report generator
v57 commit: 485facb Add auto final BGM wrapper
v58 commit: dc3b0fa Add post-render finalize command
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
11. B-roll Transition Mix Engine ทำ soft/bridge transition ตอน B-roll เข้าออกได้ โดยไม่ขยับกรอบ top/bottom และไม่กระทบ bottom audio/caption
12. มี transition QA command ตรวจ metadata ทุก B-roll slot และบังคับให้ B-roll ที่ cover jump cut ใช้ bridge mode
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

ตรวจ B-roll transition mix:

```bash
npm run check:transition
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

v59 full render:

```text
../stacked-output-v59-transition-mix-full-test.mp4
duration: 59.354333s
size: 35.1 MB
video: h264 1080x1920
audio: aac 48000 Hz
```

v59 transition mix:

```text
B-roll count: 10
soft transition slots: 5
bridge transition slots: 5
soft duration: 0.22s in/out
bridge duration: 0.26s in/out
QA command: npm run check:transition -- --output reports/transition-mix-v59-test2.json
QA status: pass
visual contact sheet: render-checks/v59-transition-mix/contact-sheet.jpg
```

v59 final report:

```text
reports/final-report-v59-transition-mix.json
reports/final-report-v59-transition-mix.md
status: review
reason: B-roll QA pass, transition QA pass, BGM QA disabled for this render, key term QA warn from existing v45 report missing "prompt"
```

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

1. **Watch v59 Output**
   - Review the transition mix by eye on the full output.
   - Confirm B-roll entry/exit feels smoother and does not distract from speech.

2. **Finalize v59 With BGM**
   - After visual approval, run `npm run finalize:video` using `../stacked-output-v59-transition-mix-full-test.mp4`.
   - Keep BGM at 5% unless the user explicitly asks for a different level.

3. **Unified Context Decision**
   - Use the same context index to drive both B-roll and BGM.
   - Store `clipStyle`, `brollIntent`, `bgmStyle`, and `reason` in one report.

4. **Full Pipeline Orchestrator**
   - Later combine: inspect -> cut -> captions -> B-roll -> render -> finalize.
   - Target command: `npm run bizdrive:render`.

5. **Run On A New Real Job Folder**
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
B-roll transition replaces top frame only.
Use soft transition for normal B-roll and bridge transition when covering jump cuts.
Do not move/scale top or bottom frame borders during transition.
Run npm run check:transition after B-roll timing or transition edits.
```
