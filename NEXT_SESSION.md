# Next Session Handoff

สถานะล่าสุด: v62 - เพิ่ม slow inner-media zoom โดย frame ห้ามขยับ

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
v59 commit: f02d694 Add B-roll transition mix
v60 commit: 216073c Add frame edit reporting
v61 commit: 91d3f9b Add B-roll spacing rule
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
13. ทุกงานต้องมี summary และ frame counts: edited frames, removed frames, output/report paths, QA result
14. มี frame edit report command สำหรับนับเฟรมจาก context index + B-roll manifest + final MP4
15. B-roll spacing rule: ห้าม B-roll ติดกันจนลายตา ต้องห่างกันอย่างน้อย 6s ระหว่าง start และมี footage จริงของ top อย่างน้อย 3s ระหว่าง insert
16. Slow inner-media motion: top/B-roll ขยับได้ช้า ๆ เฉพาะ media ข้างใน frame; top frame shell และ bottom frame ห้ามขยับเด็ดขาด
17. Motion safety command ตรวจไม่ให้ animate frame/border หรือ bottom face
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

กติกาที่ command นี้ตรวจด้วย:

```text
minBrollStartGap: 6s
minRealTopFootageGap: 3s
ถ้าเจอ B-roll -> top footage สั้น ๆ -> B-roll ในช่วงประมาณ 6s ให้ fail
```

ตรวจ motion safety:

```bash
npm run check:motion
```

สร้าง frame edit report:

```bash
npm run report:frames -- \
  --context assets/context/test2-v35-full-context-index.json \
  --broll-manifest assets/broll/optimized/test2-v35/manifest.json \
  --final ../stacked-output-v59-transition-mix-full-retest.mp4 \
  --json reports/frame-edit-report-v59-retest.json
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

v59 full retest after v60 reporting rule:

```text
../stacked-output-v59-transition-mix-full-retest.mp4
duration: 59.354333s
size: 35.1 MB
video: h264 1080x1920
audio: aac 48000 Hz
render: completed
npm run check: pass with existing warnings composition_file_too_large, timeline_track_too_dense
npm run check:transition: pass
frame report: reports/frame-edit-report-v59-retest.json
original: 2535 frames
final output: 1781 frames
content dropped: 735 frames
soft-cut overlap removed: 18 frames
total net removed: 754 frames
B-roll top replacement: 900 frames
transition mix: 144 frames
```

v61 B-roll spacing test:

```text
../stacked-output-v61-broll-spacing-full-test.mp4
duration: 59.354333s
size: 34.6 MB
video: h264 1080x1920
audio: aac 48000 Hz
render: completed
npm run check: pass with existing warnings composition_file_too_large, timeline_track_too_dense
npm run check:transition: pass
B-roll starts: 1, 7, 13, 19, 25, 31, 37, 43, 49, 55
minimum B-roll start gap: 6.00s
minimum real top footage gap: 3.00s
frame report: reports/frame-edit-report-v61-spacing.json
final report: reports/final-report-v61-spacing.md
original: 2535 frames
final output: 1781 frames
content dropped: 735 frames
soft-cut overlap removed: 18 frames
total net removed: 754 frames
B-roll top replacement: 900 frames
transition mix: 139 frames
```

v62 video2 smoke test:

```text
source folder: ../video2
top: ../video2/Ai ตัดต่อ Screen 1.mp4
bottom/audio: ../video2/Ai ตัดต่อ Screen 2.mp4
test output: ../stacked-output-v62-video2-smoke-20s.mp4
duration: 20.021s
size: 14.2 MB
video: h264 1080x1920
audio: aac 48000 Hz
render: completed
motion safety: pass
contact sheet: render-checks/video2-smoke-v62/contact-sheet.jpg
edited frames: 600 visible slow inner-media motion frames
removed frames: 0 editorial removed frames in smoke test
not rendered: remaining source after first 20s was intentionally outside smoke-test window, not counted as an edit removal
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
Every task must end with a summary and frame counts: edited frames and removed frames.
Use npm run report:frames when context index, B-roll manifest, and final MP4 are available.
B-roll starts must be at least 6s apart, with at least 3s of real top footage between inserts.
Never animate topFrameShell, bottomVideo, or .bottom-frame transform/scale/x/y.
Run npm run check:motion after any zoom/motion change.
```
