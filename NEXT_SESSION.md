# Next Session Handoff

สถานะล่าสุด: v76 - choice-based user decision gates recorded

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
v62 commit: 9e1d85a Add safe inner-media motion
v63 commit: 1fc1cd7 Add video2 context edit
v64 commit: 4773216 Add v64 production guardrails
v65 commit: 1bc100c Add v65 full edit test
v66 commit: ea280c4 Add v66 noise and sync fix
v67 commit: 5284118 Add v67 mistake prevention gates
v68 commit: bd330bc Add v68 lip sync zero tolerance
v69 commit: 59ff1dd Add v69 lip-sync safe cut rules
v70 commit: f3356ba Add v70 timestamped clip QA
v71 commit: 34e6937 Add v71 lip-sync safe final edit
v72 commit: 4a49374 Add v72 edit-first master workflow
v73 commit: e475c2b Add v73 completion marker rule
v74 commit: 02084a6 Add v74 test edit record
v75 commit: 364be31 Add v75 single final output rule
v76 commit: included in current commit (Add v76 choice-based decision gates)
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
18. video2 v66 noise/sync fix render แล้วที่ `../stacked-output-v66-video2-noise-sync-fix.mp4`
19. video2 v66 ใช้ B-roll 5 จุดจาก local Pexels stock, re-encode ใหม่ 5 derivatives, reject 0 candidate
20. video2 v66 frame report และ final report พร้อมใช้ต่อ: `reports/frame-edit-report-v66-video2.json`, `reports/final-report-v66-video2.md`
21. v64 เพิ่ม sync lock: top + bottom audio/video + subtitles ต้องอยู่ edited timeline เดียวกัน ห้ามเลื่อนแยก
22. v64 บังคับใช้ Whisper transcript ก่อน context cut/caption ทุกงาน ถ้า HyperFrames fail ให้ใช้ direct whisper-cli fallback
23. v64 บังคับทำงานเรียง step และต้องเช็ค artifact/QA ก่อนข้าม step
24. v64 B-roll ต้องพยายามโหลด fresh Pexels ก่อนเพื่อสะสม `assets/broll/index.json` จนมี QA-passed stock ประมาณ 200 clips
25. v64 B-roll ใช้ไม่เกิน 4 inserts ต่อ final video 1 นาที เว้นแต่ผู้ใช้ override ชัดเจน
26. v64 target duration เป็นเพดาน/meaning target ถ้าขอ 1:30 แต่ตัดได้ 1:20 และสาระครบ ให้ใช้ 1:20
27. v64 ระหว่างทำงานให้รายงานเป็น Step/Phase ว่ากำลังทำอะไรและเช็คอะไร
28. v65 full test พยายามโหลด fresh B-roll แล้ว แต่ shell env ไม่มี `PEXELS_API_KEY` จึงใช้ local QA-passed stock; รอบต่อไปถ้าต้องการ stock growth ให้ export key ก่อนเริ่มงาน
29. v66 เพิ่ม false-start cleanup: true start คือ sustained speech ไม่ใช่เสียงแรกที่ Whisper จับได้
30. v66 เพิ่ม audio polish chain ใหม่จาก raw bottom audio และบันทึก sync compensation 21ms เมื่อมีหลักฐานจาก stream start mismatch
31. v67 เพิ่ม `MISTAKES.md` เป็น incident log ถาวร และทุกงานต้องอ่านก่อนเริ่ม edit
32. v67 เพิ่ม hard gates: opening sustained speech, audio source proof, noise proof, final stream start_time sync, caption remap proof, final summary gate
33. v68 เพิ่ม `LIPSYNC_QA.md` และกำหนด lip sync เป็น zero-tolerance blocker
34. v68 ห้ามเรียก output ว่า final ถ้าไม่มี final stream start_time check, compensationMs/reason ถ้ามี offset, spot-check อย่างน้อย 5 จุด และ residualRisk=none
35. v69 พบ root cause lip-sync ของ v66: bottom face ถูก xfade ตอน visible จนเกิด ghost/double-mouth frames รอบ content cuts
36. v69 กำหนดว่า soft cut ต้องเป็น lip-sync-safe: top/B-roll crossfade ได้ แต่ bottom face ห้าม xfade ตอน visible; ใช้ hard cut จุดปลอดภัยหรือ B-roll/bridge ปิด jump แทน
37. v70 เพิ่ม `npm run qa:timestamps` สำหรับสร้าง QA contact sheet ทุก 1 วินาทีพร้อม timestamp label และต้องใช้ทุกครั้งที่ตรวจคลิป
38. v71 render final video2 แล้ว: `../stacked-output-v71-video2-lipsync-safe-final-bgm.mp4`
39. v71 ใช้ bottom audio เป็น master, hard-concat bottom face/audio, ไม่มี visible bottom xfade, B-roll แทน top เท่านั้น
40. v71 ตัดจาก 115.946s เหลือ 85.200s, เอาออก 30.746s / 922 frames, output 2556 frames
41. v71 ใช้ B-roll 5 จุด: fresh download 0 เพราะ shell env ไม่มี `PEXELS_API_KEY`, reused local stock 5, optimized 5, rejected 0
42. v71 BGM QA pass: Mixkit stock `mixkit-726 Uplifting Bass`, gain 5%, LUFS delta -0.1, voice remains clear
43. v71 QA pass: `npm run check`, `npm run check:transition`, `npm run check:motion`, final silencedetect >0.5s none, keyterm QA pass, final report pass
44. v72 แก้ architecture ตาม user diagnosis: ตัดต่อให้เสร็จก่อนวางลง background/HyperFrames
45. v72 สร้าง editorial masters ก่อน layout: `top_edit_master_v72.mp4`, `bottom_visual_master_v72.mp4`, `speech_audio_master_v72.wav`, `bottom_editorial_master_v72.mp4`
46. v72 HyperFrames render เป็น visual-only แล้ว mux speech audio master กลับทีหลัง จากนั้นค่อย mix BGM 5%
47. v72 final: `../stacked-output-v72-video2-edit-first-final-bgm.mp4`
48. v72 ตัดจาก 115.946s เหลือ 85.200s, เอาออก 30.746s / 922 frames, output 2556 frames
49. v72 ใช้ B-roll 5 จุด: fresh download 0 เพราะ shell env ไม่มี `PEXELS_API_KEY/OPENROUTER_API_KEY`, reused local stock 5, optimized 5, rejected 0
50. v72 QA pass: edit-first master proof, `npm run check`, `npm run check:transition`, `npm run check:motion`, final silencedetect >0.5s none, keyterm QA pass, final report pass
51. เพิ่ม `MODULES.md` เพื่อแยกงานเป็น transcript, sync-inspect, context-index, edl-build, editorial-master, broll-source, caption-build, layout-render, final-mux, final-qa
52. v73 เพิ่ม completion marker rule: เมื่อ task เสร็จสมบูรณ์และ verify แล้ว final response ต้องมี `✅✅✅` แบบบรรทัดเดี่ยวให้เห็นชัดเจน
53. v74 ทดสอบตัดต่อ full render สำเร็จด้วย edit-first master pipeline: visual-only render -> mux speech master -> BGM 5% -> final QA
54. v74 final: `../stacked-output-v74-video2-test-edit-final-bgm.mp4`
55. v74 QA pass: lint/validate/inspect with timeout 30000, transition pass, motion pass, keyterm pass, BGM pass, silence >0.5s none, timestamp QA created
56. v75 เพิ่ม single final output rule: ตอนส่งงานให้ผู้ใช้ แสดง Output MP4 เดียวคือ Final เท่านั้น; intermediate ใช้ภายใน QA และไม่ list เป็น output หลัก
57. v76 เพิ่ม choice-based user decision gates: ก่อน decision สำคัญให้ถามเป็นตัวเลือก 2-3 ข้อแบบคลิก/เลือกง่าย เช่น start/end, dead air, cut aggressiveness, B-roll, BGM, caption style, final render confirm
```

## Latest v75 Delivery

```text
Final MP4 output: ../stacked-output-v74-video2-test-edit-final-bgm.mp4
QA/report artifacts remain available internally: reports/final-report-v74-video2-test-edit.md, reports/frame-report-v74-video2-test-edit.json, render-checks/video2-v74-test-edit-timestamps/v74-test-edit-sheet.jpg
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

v66 video2 noise/sync fix:

```text
../stacked-output-v66-video2-noise-sync-fix.mp4
duration: 87.054333s
size: 51.8 MB
video: h264 1080x1920, 30fps, 2611 stream frames
audio: aac 48000 Hz
render: completed
npm run check: pass with warning timeline_track_too_dense
npm run check:transition: pass
npm run check:motion: pass
frame report: reports/frame-edit-report-v66-video2.json
final report: reports/final-report-v66-video2.md
B-roll manifest: assets/broll/optimized/video2-v66/manifest.json
B-roll new downloads: 0
B-roll AI generations: 0
B-roll reused local stock: 5
B-roll optimized derivatives: 5
B-roll rejected candidates: 0
fresh B-roll attempt: blocked_missing_env_pexels_api_key
content dropped: 853 frames
soft-cut overlap removed: 13 frames
total net removed: 867 frames
B-roll top replacement: 450 frames
transition mix: 71 frames
audio fix: dropped 0-2.3s false start, raw bottom audio polish, 21ms logged sync compensation
```

v65 video2 v64 full test:

```text
../stacked-output-v65-video2-v64-full-test.mp4
duration: 89.354333s
size: 52.5 MB
video: h264 1080x1920, 30fps, 2680 stream frames
audio: aac 48000 Hz
render: completed
npm run check: pass with warning timeline_track_too_dense
npm run check:transition: pass
npm run check:motion: pass
frame report: reports/frame-edit-report-v65-video2.json
final report: reports/final-report-v65-video2.md
B-roll manifest: assets/broll/optimized/video2-v65/manifest.json
B-roll new downloads: 0
B-roll AI generations: 0
B-roll reused local stock: 5
B-roll optimized derivatives: 5
B-roll rejected candidates: 0
fresh B-roll attempt: blocked_missing_env_pexels_api_key
content dropped: 784 frames
soft-cut overlap removed: 13 frames
total net removed: 798 frames
B-roll top replacement: 450 frames
transition mix: 71 frames
```

v63 video2 full edit:

```text
../stacked-output-v63-video2-context90-full.mp4
duration: 89.354333s
size: 55.6 MB
video: h264 1080x1920, 30fps, 2680 stream frames
audio: aac 48000 Hz
render: completed
npm run check: pass with warning timeline_track_too_dense
npm run check:transition: pass
npm run check:motion: pass
frame report: reports/frame-edit-report-v63-video2.json
final report: reports/final-report-v63-video2.md
B-roll manifest: assets/broll/optimized/video2-v63/manifest.json
B-roll new downloads: 0
B-roll AI generations: 0
B-roll reused local stock: 8
B-roll optimized derivatives: 8
B-roll rejected candidates: 3
content dropped: 784 frames
soft-cut overlap removed: 13 frames
total net removed: 798 frames
B-roll top replacement: 720 frames
transition mix: 113 frames
```

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

1. **Watch v72 Output**
   - Review the full final once by human eye/ear.
   - Focus on lip sync around 00:11, 00:27, 00:46, 00:55, 01:04 and B-roll timing at 00:05, 00:22, 00:39, 00:56, 01:13.

2. **Modular Commands**
   - Convert `MODULES.md` into repeatable npm commands.
   - Start with `bizdrive:transcript`, `bizdrive:sync`, `bizdrive:editorial`, and `bizdrive:qa`.

3. **Full Pipeline Orchestrator**
   - Combine transcript -> sync -> context -> EDL -> editorial master -> B-roll -> caption -> layout -> mux -> QA into one command.
   - Target command: `npm run bizdrive:render`.

4. **Unified Context Decision**
   - Use the same context index to drive both B-roll and BGM.
   - Store `clipStyle`, `brollIntent`, `bgmStyle`, and `reason` in one report.

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
Production/full render must use edit-first editorial masters before HyperFrames layout.
HyperFrames should render visual-only, then mux speech audio master back after render.
Top/bottom trims and cuts remain parallel.
When a task is fully complete and verified, final response must include a standalone ✅✅✅ marker.
When delivering a video edit, show only one MP4 output path: the Final file.
Ask important editorial/creative decisions as simple choices; use clickable options if available, otherwise A/B/C.
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
