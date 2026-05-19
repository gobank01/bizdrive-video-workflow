# Bizdrive Video Workflow

สถานะล่าสุด: v87 VIDEO DIV FINAL RENDER - ตัด 24s แรก, ทำ final render ครบ pipeline และบันทึกผล QA

ไฟล์นี้เป็น overview ของระบบตัดต่อ Bizdrive stacked video ด้วย HyperFrames ส่วนรายละเอียดให้ดูไฟล์แยกตามหัวข้อด้านล่าง

## Documents

```text
WORKFLOW.md               overview และลำดับระบบหลัก
STEPS.md                  practical step-by-step 62 steps สำหรับแก้งานจริง
STEPS_PRACTICAL_99.md     archived practical reference 99 steps
STEPS_DETAILED_425.md     detailed automation reference 425 steps
MODULES.md                modular subprojects/commands สำหรับแยกงาน เช่น transcript, B-roll, final mux QA
CONFIG.md                 ค่าที่แก้ได้ เช่น key terms, layout, audio, caption, B-roll
QA.md                     checklist ก่อน render / หลัง render / final delivery
MISTAKES.md               incident log และ hard gates กันความผิดพลาดซ้ำ
LIPSYNC_QA.md             zero-tolerance lip-sync QA และ report format
SYNC_REPORT.md            template วิเคราะห์ top/bottom sync และ bottom-master decisions
KEYTERM_QA.md             rule และ command สำหรับตรวจ key terms หลัง cut
MOTION_BGM.md             rule สำหรับ zoom in/out และ BGM sound loop
BGM_LIBRARY.md            BGM stock index และ style map สำหรับเลือกเพลง
NEXT_SESSION.md           handoff ล่าสุดและงานที่ควรทำต่อ
schemas/context-index.schema.json schema สำหรับ Full context index
PROMPT_TEMPLATE.md        prompt สำหรับสั่ง Codex รอบหน้า
REPORT_TEMPLATE.md        template รายงานหลัง render
CHANGELOG.md              ประวัติ version และเหตุผลที่เปลี่ยน
FULL_WORKFLOW_ARCHIVE.md  archive ของ workflow เดิม v37 ก่อนแยกไฟล์
AGENTS.md                 project rules สำหรับ agent
```

## Goal

สร้าง MP4 แนวตั้ง `1080x1920` จาก:

```text
top video    = screen recording, muted
bottom video = face video + main audio
bg.png       = full-screen background layer
```

Composition หลัก:

```text
1. bg.png เป็น layer ล่างสุด
2. top video วางด้านบนใต้ logo Bizdrive
3. bottom video เป็นวงกลมด้านล่าง top
4. top ต้อง mute
5. bottom เป็นเสียงหลัก
6. captions อยู่ใต้ bottom
7. B-roll replace เฉพาะ top frame
8. output เป็น MP4 แนวตั้ง
```

## Current Production Defaults

```text
version: v87
base output size: 1080x1920
top frame: 1080x607.5, radius 30px, gold gradient border 4px
bottom frame: 607.5x607.5 circle, gold gradient border 4px
gap top/bottom: ~40px
audio target: -16 LUFS, true peak <= -1.5 dBTP, speech-first noise gate
dead air rule: cut silence longer than 0.5s in parallel
false-start rule: if the opening has a short non-sustained sound/word followed by silence/reset, cut it before the true start
context cut default: Medium
context index: Full
soft cut: always, but lip-sync-safe only; top/B-roll can crossfade, bottom face must not xfade while visible
B-roll duration: 3s each
B-roll count: max 4 per 60s of final video, minimum 3 when the clip is long enough
B-roll fresh-stock policy: try fresh download first until QA-passed stock index reaches 200 usable clips
B-roll stock index: assets/broll/index.json
B-roll spacing: minimum 6s between B-roll starts and minimum 3s real top footage between B-rolls
B-roll provider order: Pexels -> OpenRouter veo-3.1-lite -> OpenRouter kling-v3.0-std
B-roll transition mix: enabled, soft 0.22s, bridge 0.26s for jump-cover slots
transition QA command: npm run check:transition
frame edit report command: npm run report:frames
timestamp QA command: npm run qa:timestamps
timestamp QA interval: every 1s with visible timestamp label
caption max length: about 20 Thai characters, never split Thai words
caption gold spacing: highlighted gold token must be visually separated from adjacent normal text; ABC with B highlighted becomes A B C
caption gold spacing QA command: npm run check:caption-gold
sync master: bottom audio
sync lock: top video, bottom audio/video, and captions must stay on the same edited timeline with no unlogged offset drift
edit-first master: required; create frame/sample-locked top visual, bottom visual, and speech audio masters before HyperFrames layout
HyperFrames render audio: visual-only when edit-first master is used; mux speech audio master back after render
sync compensation: allowed only when measured, logged in context/report, and applied to the bottom-master pipeline
lip sync: zero tolerance; must pass LIPSYNC_QA.md before final delivery
notify on sync mismatch: true
sync report: required when mismatch exists
context index schema: schemas/context-index.schema.json
key term checker: npm run check:keyterms
zoom motion: enabled as slow inner-media movement only, never frame/border movement
motion safety QA command: npm run check:motion
BGM loop: optional, speech-first, default 5%, licensed/royalty-free/generated-with-rights only
BGM loudness intent: barely audible ambient bed, not a noticeable song
BGM stock library: bgm-library/mixkit-stock-v50.json, 15 Mixkit tracks, check before generating
BGM selector: npm run select:bgm
BGM selector keywords: bgm-library/style-keywords-v53.json
BGM final QA command: npm run qa:bgm
BGM frame lock: required; BGM mix must preserve final video frames, video duration, and video/audio start_time
BGM auto latest final command: npm run auto:bgm
final report command: npm run report:final
post-render finalize command: npm run finalize:video
mistake prevention log: MISTAKES.md
lip sync QA: LIPSYNC_QA.md
BGM default fallback: mixkit-480 Curiosity
BGM tech fallback: mixkit-1167 Close Up
BGM calm fallback: mixkit-441 Meditation
BGM final-real-file QA: required
BGM mix command: npm run mix:bgm
completion marker: when a task is fully complete and verified, final response must include a clear standalone `✅✅✅`
delivery output: show only one user-facing MP4 output, the Final file; intermediate visual/no-BGM files are internal QA artifacts
user decision gate: ask before important editorial/creative decisions when possible
decision question style: choice-based, 2-3 simple options, recommended first, minimal typing
rough direction trim gate: before lock trimStart/trimEnd, collect user rough direction if available and create candidates from hint + evidence
phase gate mode: required; after every Phase, stop with proof and wait for user pass before continuing unless user explicitly requests auto/full mode
raw bottom lip-sync gate: metadata sync is not enough; before accepting an input set, preview raw/phase bottom face with its own bottom audio and require human/visual lip-sync pass
latest phase test: v86 perfect workflow checkpoint saved; v83 remains accepted final output
```

## Master Pipeline

1. Prepare input files.
1.1. Read `MISTAKES.md` and `LIPSYNC_QA.md`; identify active prevention gates.
2. Inspect raw media metadata.
3. Confirm top/bottom roles and sync.
3.1. Ask user decision gates as choices when the answer affects creative/editorial direction.
4. Find true spoken start; reject false starts before sustained speech.
5. Trim top and bottom in parallel.
6. Cut dead air in parallel.
7. Re-encode clean media for reliable seeking.
8. Polish bottom audio from the cleanest verified bottom source, preferably raw bottom audio, with speech-first denoise/gate before loudnorm.
9. Transcribe polished audio with Whisper; do not skip transcription.
10. Clean transcript and mark editable key terms.
11. Build Full context index.
12. Decide keep/drop segments from meaning.
13. Create edit-first editorial masters before layout: top visual master, bottom visual master, speech audio master, and bottom editorial proof clip.
14. Prove masters are locked: same duration, same frame count, same start_time, and speech audio sample count matches the frame-snapped EDL.
15. Apply lip-sync-safe soft cuts: top/B-roll may crossfade, but bottom face must not xfade while visible.
16. Select B-roll slots from context.
17. Search/download/index B-roll first; reuse only when indexed stock is clearly the best match or stock count is already mature.
18. QA B-roll and reject text/logo/brand/graphic failures.
19. Re-encode selected B-roll.
20. Build captions with Bizdrive style. Gold-highlight terms must be separated from adjacent normal text with word-safe spacing. This belongs to Phase 10 Caption Build, before HyperFrames render and before BGM/final mux.
21. If BGM is enabled, run `npm run select:bgm` to select from stock using title/transcript/context; generate only when no stock mood fits.
22. Add B-roll transition mix, optional zoom motion, and BGM loop if enabled.
23. Update HyperFrames composition using visual masters only and keep render audio disabled.
24. Run `npm run check`.
25. Render visual-only MP4.
26. Mux the speech audio master back onto the visual render, then mix BGM at 5% if enabled.
26.0. BGM mix must preserve the original final video stream: same frame count, same video duration, same video start_time, and same audio start_time. Never use an audio-shortened mux as final.
26.1. Mark exactly one MP4 as the user-facing Final output.
27. QA output frames, audio, BGM, motion, captions, key terms, and B-roll; after a full render, prefer `npm run finalize:video` to run Auto BGM and final report together.
27.1. Run mistake prevention gates: opening true start, audio source proof, noise proof, edit-first master proof, final stream start_time sync, caption remap proof.
27.2. Run lip-sync zero-tolerance gate from `LIPSYNC_QA.md`; if uncertain, mark output blocked, not final.
27.3. Create timestamped clip QA sheet every 1 second with `npm run qa:timestamps`.
28. Write frame edit report with `npm run report:frames`.
29. Write final report with `npm run report:final`.
30. Update changelog/workflow version when rules change.

## v86 Perfect Workflow Checkpoint

ผู้ใช้ยืนยันว่า:

```text
save ทุกอย่างให้เรียบร้อย นี้คือ version ที่สมบูรณ์ที่สุด
```

บันทึกเป็นฐาน workflow สมบูรณ์ล่าสุด:

```text
workflow checkpoint = v86
accepted final output = ../preview-v80/v83-setB-final-accepted.mp4
accepted final report = reports/phase11/v83-final-report.md
latest rule checkpoint = v85 caption gold placement
current git baseline = v86 perfect workflow checkpoint
```

QA ณ จุดบันทึก:

```text
npm run check:caption-gold = pass, 27 captions, 0 issues
npm run check = pass, 0 errors, 1 existing warning: timeline_track_too_dense
worktree before v86 edits = clean
main video frames changed = 0
main video frames removed = 0
B-roll newly downloaded = 0
B-roll reused = 0
AI-generated B-roll = 0
```

กติกา:

```text
ใช้ v86 เป็น workflow baseline ก่อนพัฒนารอบถัดไป
ถ้าจะเปลี่ยน rule/logic ต่อจากนี้ ให้เริ่ม v87
v83 ยังเป็น accepted final MP4 ของคลิปทดสอบนี้
```

## v85 Placement: Caption Gold Spacing

ตำแหน่งที่ถูกต้องของ rule นี้:

```text
Phase: Phase 10 — Captions, Composition, QA
Sub-step: 61 Caption Build
QA sub-step: 61.2 Caption Gold Spacing QA
Module: caption-build
Timing: หลัง transcript/context/cut timeline lock แล้ว, ก่อน HyperFrames render, ก่อน BGM/final mux
Command: npm run check:caption-gold
```

เหตุผล:

```text
gold spacing เป็นปัญหาในชั้น caption HTML/style ไม่ใช่ B-roll, BGM, final mux หรือ delivery
ต้องตรวจทันทีหลังสร้าง/แก้ caption HTML เพราะถ้ารอไปตรวจหลัง render จะเสียเวลาย้อนงาน
rule นี้ไม่เปลี่ยน audio, sync, B-roll timing, final mux หรือ frame count
```

## v84 Caption Gold Spacing Rule

เพิ่ม rule สำหรับ subtitle/caption สีเหลือง:

```text
ถ้ามี token ที่ต้องทำสีเหลือง ต้องเว้นช่องว่างหน้าหลังจากข้อความธรรมดา
ตัวอย่าง: ABC และ B เป็นสีเหลือง -> A B C
ตัวอย่าง: BCD และ B/C/D เป็น token ที่ต้องแยก -> B C D ตาม token ที่ highlight
ถ้า token สีเหลืองอยู่ต้น caption ไม่ต้องมีช่องว่างนำหน้าที่มองเห็นเกินจำเป็น แต่ต้องไม่ติดกับ token ถัดไป
ถ้า token สีเหลืองอยู่ท้าย caption ไม่ต้องมีช่องว่างท้ายที่เกินจำเป็น แต่ต้องไม่ติดกับ token ก่อนหน้า
```

Implementation:

```text
index.html: .gold เพิ่ม margin แนวนอน และ first/last child guard
package.json: เพิ่ม npm run check:caption-gold
scripts/check-caption-gold-spacing.js: ตรวจว่า .gold ไม่ติดตัวอักษรธรรมดาซ้าย/ขวาใน caption-box
```

QA:

```text
npm run check:caption-gold = pass, captionCount 27, issues 0
```

## v83 Accepted Final

ผู้ใช้ตรวจ v82 BGM final candidate แล้วให้ผลว่า:

```text
สมบูรณ์แบบ ไปต่อได้เลย
```

บันทึกเป็น final accepted output:

```text
final output = ../preview-v80/v83-setB-final-accepted.mp4
base = ../preview-v80/v80-setB-golden-phase10-proof.mp4
final report json = reports/phase11/v83-final-report.json
final report md = reports/phase11/v83-final-report.md
timestamp QA sheet = reports/phase11/v83-timestamps/timestamp-qa-sheet.jpg
```

QA:

```text
final report status = pass
video = 1080x1920, 30fps, 2423 frames
duration = 80.766667s
video/audio start_time = 0.000000 / 0.000000
BGM frameLock = pass, frameDelta 0
BGM = mixkit-175 Digital Clouds, 5%
loudness = -16.3 LUFS
true peak = -1.7 dBFS
B-roll = 27 fresh Pexels downloads, 5 selected, 0 reused, 0 generated, 22 rejected, 5 optimized
B-roll replacement frames = 450
main video frames removed after v81 golden proof = 0
```

กติกาต่อจาก v83:

```text
ใช้ v83 เป็น accepted final reference สำหรับงานคลิปนี้
ถ้าจะปรับต่อ ให้เริ่มจาก final/golden proof ที่ผ่านแล้วและ preserve timing ทุกชั้น
final report ต้องแสดง BGM frameLock และมอง B-roll status ที่ลงท้ายด้วย pass เป็น pass
```

## v82 Final BGM Candidate

ต่อจาก v81 golden proof ได้ทดสอบ BGM 5% บนไฟล์จริง:

```text
final candidate = ../preview-v80/v81-setB-final-bgm.mp4
base = ../preview-v80/v80-setB-golden-phase10-proof.mp4
BGM style = tech_explainer
BGM track = mixkit-175 Digital Clouds
provider/license = Mixkit / https://mixkit.co/license/
gain = 5% (-26.0206 dB)
```

QA:

```text
video frames = 2423 -> 2423
video duration = 80.766667s -> 80.766667s
video start_time = 0.000000 -> 0.000000
audio start_time = 0.000000
audio duration = 80.766000s
loudness = -16.2 LUFS -> -16.3 LUFS
true peak = -1.5 dBFS -> -1.7 dBFS
BGM QA status = pass
timestamp QA sheet = reports/phase11/timestamps/timestamp-qa-sheet.jpg
```

Root cause ที่แก้:

```text
`mix-bgm.js` เดิมใช้ `-shortest` ทำให้ BGM candidate แรกสั้นลง 2 frames (2423 -> 2421)
แก้โดยตัด `-shortest` ออก และ lock audio filter ด้วย `apad,atrim=0:<duration>,asetpts=PTS-STARTPTS`
`qa-bgm-final.js` เพิ่ม frameLock check เพื่อ fail/review ทันทีถ้า BGM ทำให้ video frames/duration/start_time เปลี่ยน
```

กติกาต่อจาก v82:

```text
ถ้าเพิ่ม BGM หรือแก้ final audio ต้องตรวจ frameLock ทุกครั้ง
ถ้า frameDelta ไม่ใช่ 0 ห้ามส่ง final
ถ้า BGM ชัดเกินไปหรือรบกวนเสียงพูด ให้ลดต่ำกว่า 5% หรือย้อนกลับ v81 golden proof
```

## v81 Golden Phase 10 Proof

ผู้ใช้ตรวจ `../preview-v80/v80-setB-phase10-proof.mp4` แล้วให้ผลว่า:

```text
สมบูรณ์ แบบไม่ผิดเลย นี้แหละ ที่ต้องการ
```

บันทึกเป็น golden checkpoint:

```text
golden proof = ../preview-v80/v80-setB-golden-phase10-proof.mp4
source proof = ../preview-v80/v80-setB-phase10-proof.mp4
report = reports/phase10/v80-setB-phase10-report.md
composition = index.html
```

QA ที่ต้องรักษาห้ามถอย:

```text
video/audio start_time = 0.000000 / 0.000000
start delta = 0ms
duration = 80.766667s
video frames = 2423
loudness = -16.2 LUFS
true peak = -1.5 dBFS
B-roll = 5 fresh-selected Pexels clips in top frame only
captions = 27 cues, no cue over 22 visible chars
main video frames removed in Phase 10 = 0
top/bottom/audio timing shifted in Phase 10 = 0
```

กติกาต่อจากจุดนี้:

```text
ห้ามเปลี่ยน timing ของ top/bottom/audio/captions จาก golden proof
ถ้าจะเพิ่ม BGM ให้ mix ที่ 5% บน golden proof และ QA start_time/loudness/lip-sync ซ้ำ
ถ้า BGM ทำให้เสียงพูดด้อยลง ให้ย้อนกลับ golden proof ทันที
```

## v79 Root Cause: Why Set A Failed And Set B Passed

ใน v78 Phase 5 มีการทดสอบ 2 input sets:

```text
Set A: video2/Ai ตัดต่อ Screen 1.mp4 + video2/Ai ตัดต่อ Screen 2.mp4
Set B: test 2/top screen - video 2.mp4 + test 2/botton screen - video 2.mp4
```

## v80 Clean Set B Phase 5 Test

ล้าง generated artifacts แล้ว rebuild เฉพาะ Set B เพื่อพิสูจน์ซ้ำว่าปากกับเสียงยังตรงเมื่อเริ่มใหม่จากศูนย์

```text
cleaned:
  assets/
  reports/phase4/
  reports/phase5/
  ../preview-v78/
  ../preview-v80/

source:
  top = test 2/top screen - video 2.mp4
  bottom = test 2/botton screen - video 2.mp4
  bg = video/bg.png

cut:
  trimStart = 8.000s
  trimEnd = 90.900s
  dead air cuts = 37.566667-38.100000, 40.800000-41.900000, 71.100000-71.600000

outputs:
  bottom proof = ../preview-v80/v80-setB-bottom-lipsync-proof.mp4
  stacked preview = ../preview-v80/v80-setB-phase5-preview.mp4

QA:
  phase frames = 2423
  phase duration = 80.766667s
  video/audio start_time = 0.000000
  silencedetect >0.5s after cut = pass
```

สถานะ: รอ human lip-sync review จากผู้ใช้ก่อนข้ามไป Phase 6

ผลจาก human review:

```text
Set A: fail - ปากไม่ตรง
Set B: pass - ปากตรงเป๊ะ
```

สาเหตุที่สรุปได้:

```text
1. Phase 5 ตัด top/bottom แบบคู่ขนานแล้ว และ frame count/duration/start_time ตรงกัน
2. preview ใช้เสียงจาก bottom เท่านั้น top audio ถูก ignore
3. ถ้าปากของ bottom ยังไม่ตรงกับเสียง bottom หลังตัดคู่ขนาน แปลว่าปัญหาไม่ได้เกิดจาก top layer หรือ layout
4. root cause ที่เป็นไปได้สูงสุดคือ Set A bottom source มี internal audio/video offset อยู่แล้ว หรือ Set A ไม่ใช่คู่ raw ที่ sync กันจริงตั้งแต่ต้น
5. Set B ผ่าน เพราะ bottom face + bottom audio ใน source/preview ตรงกันจริง ไม่ใช่แค่ metadata ตรง
```

บทเรียน:

```text
metadata sync เช่น duration, fps, frame count, stream start_time เป็นแค่ container proof
metadata ไม่สามารถพิสูจน์ semantic lip sync ได้
lip sync ต้องพิสูจน์จากปากกับเสียงจริง โดยเฉพาะ bottom face + bottom audio
ถ้า human reviewer บอกว่าปากไม่ตรง ให้ถือว่า fail ทันที ถึงแม้ ffprobe จะดูตรงทุกค่า
```

กฎใหม่:

```text
ก่อนข้าม Phase 3/5 ไป Phase 6 ต้องมี Raw/Phase Bottom Lip-Sync Gate
สร้างหรือเปิด preview ที่เห็น bottom face และใช้ bottom audio ของ set นั้น
ให้ผู้ใช้หรือ reviewer ยืนยันว่า pass/fail
ถ้ามีหลาย set ให้เลือก set ที่ผ่าน human lip-sync gate
set ที่ fail ห้ามใช้ต่อจนกว่าจะ rebuild จาก source ที่ sync หรือมี measured compensation พร้อม proof
ห้ามแก้ด้วยการขยับ audio เดาสุ่ม เพราะอาจทำให้ caption/top/B-roll drift
```

## Phase-Gated Testing Rule

ตั้งแต่ v78 เป็นต้นไป การทดสอบ workflow ต้องเดินทีละ Phase และหยุดให้ผู้ใช้ตรวจหลังจบ Phase นั้น ก่อนเริ่ม Phase ถัดไป

หลังจบแต่ละ Phase ต้องแสดง:

```text
phase: Phase number/name
artifact: ไฟล์/report/log/contact sheet ที่พิสูจน์ผล
QA: ผ่านอะไร / ไม่ผ่านอะไร
risk: sync, caption, audio, B-roll, render risk ที่ยังเหลือ
next choice:
  A. ผ่าน ไป Phase ถัดไป (Recommended เมื่อหลักฐานครบ)
  B. ไม่ผ่าน ย้อนแก้ Phase นี้
  C. ขอหลักฐานเพิ่ม
```

กฎสำคัญ:

```text
do not cross phase boundary until user says pass/approve
if a Phase fails, fix and rerun the same Phase before continuing
if the user gives all direction at the start, still summarize the Phase result before moving on
auto/full mode can skip waiting only when the user explicitly requests it
record the user gate result in the report/context when the task produces artifacts
```

## User Decision Gate

ก่อนข้าม decision สำคัญ ให้ถามผู้ใช้ถ้าถามได้ โดยถามเป็นตัวเลือกง่าย ๆ:

```text
question style: 2-3 choices, recommended choice first
input style: click/select if UI supports it; otherwise A/B/C short reply
free text: allowed only as optional "อื่น ๆ" when needed
default: if user already gave direction at the beginning, use that as the answer and do not ask again
stop rule: if answer changes edit direction and is missing, ask before cutting/rendering
```

ต้องถาม/ยืนยันเป็นตัวเลือกในจุดเหล่านี้เมื่อยังไม่รู้คำตอบ:

```text
start/end: ให้ผู้ใช้บอกคร่าว ๆ หรือให้ AI หาเอง
cut aggressiveness: Conservative / Medium / Aggressive
dead air: ตัด silence >0.5s ทั้งหมด / ตัดเฉพาะช่วงยาวมาก / ให้ AI เสนอ
B-roll: ใส่ / ไม่ใส่ / ให้ AI แนะนำจำนวน
B-roll sourcing: พยายามโหลดใหม่ / ใช้ stock ก่อน / ผสมสองแบบ
BGM: ใส่ 5% / ไม่ใส่ / ให้ AI เลือกหลังวิเคราะห์
caption style: clean สั้น / ใกล้เสียงพูดจริง / ให้ AI balance
final render: confirm decision summary ก่อน render full
```

Phase 4 trim decision ต้องมี evidence ตามนี้:

```text
20.1 รับ user rough direction ถ้ามี: start คร่าว ๆ, end คร่าว ๆ, must keep, must remove, target duration, tone
20.2 AI สร้าง start/end candidates จาก user hint + audio evidence + rough transcript + silence/VAD evidence
20.3 ถ้ามี user hint ต้องใช้เป็น anchor; ห้ามเลือกจุดตัดจากการเดาล้วน
20.4 ถ้าหลักฐานขัดกับ user hint ต้องรายงานก่อน เช่น user บอกเริ่ม 24s แต่เสียงพูดจริงเริ่ม 23.6s
21 lock trimStart/trimEnd พร้อม user choice, selected candidate, rejected candidates, frame/sample values, evidence และเหตุผล
```

ตัวอย่างคำถาม:

```text
Step 21 Start Gate:
A. ใช้จุดที่คุณบอกคร่าว ๆ เป็น anchor (Recommended)
B. ให้ AI หา true start จาก audio/transcript
C. หยุดก่อน ส่ง preview/candidates ให้เลือก
```

## Sequential Execution Gates

ทุกงานต้องทำตามลำดับ step ห้ามข้าม ถ้า step หนึ่งยังไม่ผ่าน QA ให้แก้ step นั้นก่อนค่อยไปต่อ

```text
1. ก่อนเริ่ม step ถัดไป ให้บอกผู้ใช้ว่าอยู่ Step ไหนและกำลังทำอะไร
2. หลังจบ step ให้เช็ค artifact/QA ที่พิสูจน์ step นั้น เช่น ffprobe, transcript, context index, manifest, contact sheet, npm check
3. ถ้า check fail ให้หยุดแก้ ไม่ข้ามไป render หรือ final report
4. ถ้า command/tool สำคัญ fail เช่น Whisper ให้ใช้ fallback ที่เทียบเท่า เช่น direct whisper-cli แต่ต้องยังมี transcript ก่อน context/caption
5. ทุก timing decision ต้องอิง bottom master timeline และบันทึกใน context/manifest/report
6. ก่อนข้าม editorial/creative gate ให้ถามเป็นตัวเลือก ถ้าผู้ใช้ยังไม่ได้ให้ direction
7. ก่อนข้าม Phase ต้องมี Phase Gate Report และ user pass เว้นแต่ผู้ใช้สั่ง auto/full mode ชัดเจน
```

## Sync Lock Rule

เสียงและเฟรมต้องตรงกันเสมอแบบ frame-accurate:

```text
bottom audio = master clock
bottom video = must stay locked to bottom audio
top video = must use the exact same trim/cut list as bottom
captions = must be generated after cuts and mapped to the edited timeline
B-roll = may replace only top visuals; it must never change top/bottom/caption timing
no manual offset, speed change, frame shift, or independent retime unless explicitly logged and approved
```

ถ้าพบ top/bottom/caption/audio ไม่ตรงกัน แม้เพียงเล็กน้อย ให้แจ้งผู้ใช้และแก้ sync ก่อนทำงานต่อ

ถ้าต้องชดเชย sync ให้ใช้หลักฐานก่อนเสมอ เช่น `ffprobe` stream `start_time`, frame count, หรือ sync point ที่มองเห็น/ได้ยิน และบันทึกค่า offset ใน context/final report

Raw bottom lip-sync gate:

```text
bottom face + bottom audio ต้องตรงกันตั้งแต่ source/phase preview
ถ้า bottom ภายในตัวเองไม่ตรง ห้ามแก้ downstream ด้วย layout หรือ caption
ถ้า set หนึ่ง fail แต่มีอีก set pass ให้ใช้ set ที่ pass เป็นหลัก
```

## Edit-First Master Rule

ทุกคลิป production ต้องตัดต่อให้จบก่อนวางลง background:

```text
1. สร้าง EDL ที่ frame-snapped จาก bottom audio master
2. ใช้ EDL เดียวกันตัด top visual, bottom visual และ speech audio
3. สร้าง master อย่างน้อย 4 ไฟล์: top_edit_master.mp4, bottom_visual_master.mp4, speech_audio_master.wav, bottom_editorial_master.mp4
4. ตรวจ master ก่อนเข้า HyperFrames: duration เท่ากัน, frame count เท่ากัน, start_time 0, sample rate 48k, ไม่มี silence >0.5s
5. HyperFrames ใช้ top/bottom visual master เท่านั้น และ render แบบ audioCount=0 หรือ visual-only
6. หลัง render visual-only แล้วค่อย mux speech_audio_master.wav กลับเข้า MP4
7. BGM 5% ใส่หลัง speech audio mux แล้วเท่านั้น
```

เหตุผล: layout/background/caption/B-roll stage ไม่ควรมีสิทธิ์เปลี่ยนเวลาเสียงหรือเฟรมปากอีกแล้ว ถ้าเสียงกับปากจะพลาด ต้องจับได้ตั้งแต่ editorial master stage ก่อนเสียเวลา render final

## Lip-Sync Zero-Tolerance Rule

lip sync ห้ามพลาดเด็ดขาด:

```text
1. ก่อน render ต้องพิสูจน์ raw/intermediate top-bottom-bottomAudio sync
2. หลัง render ต้องตรวจ final video/audio stream start_time ทุกครั้ง
3. ต้อง spot-check ปากกับเสียงจริงอย่างน้อย 5 จุด: hook, hard consonant, after cuts, around bridge B-roll, CTA
4. ห้ามสรุป sync pass จาก frame count/duration อย่างเดียว
5. ถ้าต้อง compensate offset ต้องมี ms value + reason ใน context/final report
6. ถ้ายังไม่มั่นใจ ให้รายงาน blocked และห้ามเรียก output ว่า final
7. ห้าม xfade bottom face ตอนเห็นปากอยู่ เพราะจะเกิด ghost/double-mouth frame ที่ไม่มีทางตรงเสียง
```

## Lip-Sync-Safe Soft Cut Rule

soft cut ยังใช้ได้ แต่ต้องไม่ทำลายปากกับเสียง:

```text
allowed:
  - top screen xfade
  - B-roll entry/exit transition
  - B-roll bridge covering jump cuts
  - audio microfade เฉพาะจุดที่ไม่ smear speech/key term
  - bottom hard cut ที่ silence, closed-mouth point, หรือ speech boundary ที่พิสูจน์แล้ว

forbidden:
  - xfade bottom face while bottom circle is visible
  - acrossfade speech over visible mouth movement when it blends phonemes
  - calling lip sync pass without cut contact sheet around every content cut
```

ถ้าจุดตัดจำเป็นต้องข้ามช่วงคำพูดและ bottom jump ดูแรง ให้ใช้ B-roll/transition ปิดช่วง jump แทนการ blend ปากสองช่วงเข้าด้วยกัน

## Audio Noise Rule

ช่วงต้นของไฟล์ดิบมักมีเสียงไอ เสียงลองพูด เสียงสั้น หรือพูดแล้วหยุดตั้งสมาธิใหม่ ให้ตัดออกก่อนทำ denoise:

```text
1. ใช้ bottom audio เป็นหลักเพื่อหา true start
2. ถ้าช่วงแรกเป็นเสียงสั้นแล้วตามด้วย silence/reset ก่อน sustained speech ให้ถือเป็น false start
3. true start ต้องเป็นจุดที่พูดต่อเนื่องจริง ไม่ใช่คำแรกที่ Whisper เดาได้
4. ใช้ raw bottom audio เป็นแหล่ง polish ถ้าไฟล์ polished เดิมยังไม่ผ่าน noise/sync
5. chain เริ่มต้น: highpass 90Hz, lowpass 12000Hz, afftdn nr=14 nf=-42 tn=1 rf=-38 gs=8, agate threshold=0.015 ratio=2.5, compressor, loudnorm -16 LUFS, limiter
6. ห้ามให้ noise reduction ทำให้เสียงพูดบาง/robotic; ถ้าเสียงเสีย ให้ลดความแรงก่อน render full
```

## Duration Target Rule

เวลา output ที่ผู้ใช้กำหนดคือเพดาน/เป้าหมาย ไม่ใช่ข้อบังคับให้ยืดคลิป:

```text
ถ้าผู้ใช้ขอ 1:30 แต่ตัดตามสาระแล้วได้ 1:20 และเนื้อหาครบ ให้ถือว่าดีกว่า
ห้ามเติมเนื้อหาหรือยืดจังหวะเพื่อให้ชน target duration
ถ้าสั้นกว่า target มากเกินไปจนสาระหาย ให้กลับไปตรวจ context index
```

## Required Summary And Frame Counts

ทุกครั้งหลังทำงาน ต้องสรุปให้ผู้ใช้เห็นอย่างน้อย:

```text
1. ทำอะไรไปบ้าง
2. output path หรือ report path ที่เกี่ยวข้อง
3. QA/test ที่รันและผลลัพธ์
4. B-roll โหลดใหม่ / generated / reused / optimized เท่าไร ถ้างานเกี่ยวกับ B-roll
5. ตัดต่อไปกี่เฟรม เช่น B-roll replace top frame, transition mix, zoom/motion หรือ overlay สำคัญ
6. เอาออกไปกี่เฟรม เช่น dropped content segments, soft-cut overlap, total net removed
7. mistake prevention gates ผ่านหรือไม่ โดยเฉพาะ opening/noise/sync/caption
8. lip-sync status: finalStreamStartDeltaMs, compensationMs, spotCheckPoints และ residualRisk
9. ถ้า task เสร็จสมบูรณ์และ verify แล้ว ให้แสดง `✅✅✅` แบบบรรทัดเดี่ยวให้เห็นชัดเจน
10. แสดง user-facing video output เพียงไฟล์เดียว คือ Final MP4; ห้าม list visual-only/no-BGM/intermediate เป็น output หลัก ยกเว้นผู้ใช้ขอ debug artifact
```

ให้นับเฟรมด้วย `30fps` เป็นค่า default ของ workflow นี้ เว้นแต่ source หรือ output ระบุชัดว่าต้องใช้ fps อื่น

ใช้คำสั่งนี้เมื่อมี context index, B-roll manifest และ final MP4:

```bash
npm run report:frames -- \
  --context assets/context/test2-v35-full-context-index.json \
  --broll-manifest assets/broll/optimized/test2-v35/manifest.json \
  --final ../stacked-output-v59-transition-mix-full-test.mp4 \
  --json reports/frame-edit-report-v59.json
```

ดูรายละเอียดเต็มใน `STEPS.md`

## Key Rules

```text
ตัด top/bottom คู่ขนานเสมอ
ห้าม trim หรือ dead-air cut เฉพาะ bottom อย่างเดียว
ถ้า top/bottom duration หรือ start offset ไม่เท่ากัน ให้แจ้งผู้ใช้ก่อน
bottom audio เป็น master timeline และสำคัญกว่า top เพราะเป็นเสียงจริง
ใช้ bottom audio เป็น source หลักสำหรับ transcript/context/dead-air
ใช้ screen sampling เป็นตัวช่วย ไม่ใช่ตัวหลักของความหมาย
ห้ามตัด key spoken terms จนหายจากเสียงพูดจริง
Whisper จำเป็นทุกงาน ถ้า HyperFrames transcribe fail ให้ใช้ direct whisper-cli หรือ fallback ที่ให้ timestamp ได้
ห้ามเลื่อน top, bottom, audio หรือ captions แยกกันเด็ดขาด ต้องใช้ timeline เดียวกัน
ตัดต่อ production ต้องใช้ edit-first master: ตัด top/bottom/audio ให้เสร็จและ QA sync ก่อนเข้า HyperFrames layout
HyperFrames final render ใน workflow นี้ควรเป็น visual-only แล้ว mux speech audio master กลับทีหลัง
เวลาส่งงานให้ผู้ใช้ แสดง Output เดียวเท่านั้นคือ Final MP4; intermediate ใช้ภายใน QA ไม่ต้อง list เป็น output
ก่อน decision สำคัญ เช่น start/end, cut aggressiveness, B-roll, BGM, caption style และ final render ให้ถามผู้ใช้เป็นตัวเลือกง่าย ๆ ถ้ายังไม่มี direction
ก่อน lock trimStart/trimEnd ต้องมี user rough direction ถ้ามี, start/end candidates, audio/transcript/silence evidence, และรายงานก่อนถ้าหลักฐานขัดกับ hint
caption timing ต้อง map หลัง trim/dead-air/context cut แล้ว ไม่ใช้ timestamp raw โดยตรง
B-roll ต้องไม่มี text/logo/watermark/other brand/distracting graphic
B-roll ต้องพยายามโหลด fresh candidate ก่อนเพื่อสะสม stock/index จนมี QA-passed stock อย่างน้อย 200 clips
เมื่อ stock index มี QA-passed footage ครบ 200 clips แล้ว จึงค่อย reuse เป็น default; แต่ถ้า context ไม่ match ต้องโหลดใหม่
B-roll ใช้ได้ไม่เกิน 4 อันต่อ final video 1 นาที
B-roll เข้า/ออกต้องใช้ transition mix เสมอ และถ้าปิด jump cut ให้ใช้ bridge mode
transition mix ห้ามขยับกรอบ top/bottom หรือ caption
zoom motion ต้อง subtle, ช้า, และใช้กับ inner media เท่านั้น
ห้าม animate transform/scale/x/y กับ top frame shell หรือ bottom frame เด็ดขาด
BGM ต้องอยู่ใต้เสียงพูดเสมอ default 5% และต้องมีสิทธิ์ใช้งาน
BGM 5% ตั้งใจให้แทบไม่ได้ยิน แค่ช่วยไม่ให้คลิปแห้ง ถ้า melody ชัดจนคนสนใจเพลงถือว่าดังเกิน
ห้ามบอกว่าเพลงไม่มีลิขสิทธิ์ถ้าไม่มี license/source ยืนยัน
ถ้าเปิด BGM ให้เช็ค `bgm-library/mixkit-stock-v50.json` ก่อน generate เพลงใหม่
ถ้าเปิด BGM ให้รัน `npm run select:bgm` โดยใช้ title/transcript/context และเก็บ report
ถ้าวิเคราะห์ title/transcript/context แล้วยังไม่ชัด ให้ใช้ default fallback `mixkit-480 Curiosity`
ทดสอบ BGM ต้องทำกับ final MP4 จริงที่มี top/bottom/caption/B-roll แล้วเสมอ โดยใช้ `npm run qa:bgm`
หลัง render full แล้วใช้ `npm run auto:bgm` ได้ถ้าต้องการให้ระบบเลือก final MP4 ล่าสุดให้อัตโนมัติ
หลัง render full และมี context/B-roll/keyterm report แล้วใช้ `npm run finalize:video` เพื่อทำ BGM + final report ในคำสั่งเดียว
หลังแก้ index.html ต้องรัน npm run check
หลังแก้ B-roll timing/transition ต้องรัน npm run check:transition
หลังแก้ zoom/motion ต้องรัน npm run check:motion
เมื่อตัด context ให้รัน key term QA ถ้า key terms อาจถูกตัดหาย
ทุกงาน B-roll ต้องมี manifest และ final report
หลัง render/QA ให้สร้าง JSON + Markdown final report ด้วย `npm run report:final`
ทุกงานต้องอ่าน `MISTAKES.md` และห้ามส่ง final ถ้า hard gate ในไฟล์นั้นยังไม่ผ่าน
ทุกงานต้องอ่าน `LIPSYNC_QA.md`; ถ้า lip sync ยังไม่มั่นใจ 100% ให้หยุดและรายงาน blocked
ทุก rule change ต้องนับ version
เมื่อ task จบสมบูรณ์และตรวจแล้ว ต้องใส่ ✅✅✅ ใน final response เสมอ
```

## Latest Proven Output

```text
version: v87 video div final render
output: /Users/gobank01/Documents/Video V2/preview-v87/v87-video-div-final.mp4
duration: 103.466667s
frames: 3104 video frames at 30fps
video: h264 1080x1920, 30fps, start_time 0.000000
audio: AAC, 48kHz, stereo, BGM mixed at 5%, start_time 0.000000
source duration: 130.433333s / 3913 frames
content dropped: 26.966667s / 809 frames
opening trim: 24.000s / 720 frames
dead-air removed: 2.966667s / 89 frames
B-roll: 5 reused QA-passed indexed sources, 5 optimized derivatives, 0 new downloads, 0 AI generations, 0 rejected candidates
B-roll fresh sourcing: blocked because PEXELS_API_KEY/OPENROUTER_API_KEY were not present in shell env
B-roll replacement: 15s / 450 frames, top-frame only
BGM: Mixkit mixkit-1167 Close Up, finance_business, 5%, frame-lock pass
QA: caption-gold pass, motion pass, transition pass, keyterms pass, npm run check pass with only timeline_track_too_dense warning
timestamp QA: reports/phase11/v87-timestamps/timestamp-qa-sheet.jpg
final report: reports/phase11/v87-final-report.md
```

Previous proven output:

```text
version: v74 video2 test edit
output: /Users/gobank01/Documents/Video V2/stacked-output-v74-video2-test-edit-final-bgm.mp4
duration: 85.200s
frames: 2556 video frames at 30fps
video: h264 1080x1920, 30fps
audio: AAC, 48kHz, stereo, BGM mixed at 5%
source duration: 115.946s
content dropped: 30.746s / 922 frames
total net removed: 30.746s / 922 frames
B-roll: 5 local Pexels stock sources reused, 5 optimized derivatives, 0 new downloads, 0 AI generations, 0 rejected candidates
B-roll fresh sourcing: attempted, blocked because PEXELS_API_KEY/OPENROUTER_API_KEY were not present in shell env
B-roll replacement: 15s / 450 frames
transition mix: 2.52s / 76 frames
architecture fix: top_edit_master, bottom_visual_master, speech_audio_master were created first and QAed before HyperFrames layout
render flow: visual-only HyperFrames render, then speech_audio_master mux, then BGM 5%
sync proof: editorial masters share exact 85.200s duration and 2556 frames; final video/audio stream start_time both 0.000s before BGM, BGM final starts at 0.000s with AAC tail rounding only
QA: pass, with only timeline_track_too_dense warning
reports: reports/frame-report-v72-video2.json, reports/final-report-v72-video2.md, reports/bgm-qa-v72-video2.json
v74 reports: reports/frame-report-v74-video2-test-edit.json, reports/final-report-v74-video2-test-edit.md, reports/bgm-qa-v74-video2-test-edit.json
v74 timestamp QA: render-checks/video2-v74-test-edit-timestamps/v74-test-edit-sheet.jpg
note: v74 uses the same v72 edit-first masters and verifies the current v73/v74 workflow path with a fresh render
```

Previous proven output:

```text
version: v72 video2 edit-first final
output: /Users/gobank01/Documents/Video V2/stacked-output-v72-video2-edit-first-final-bgm.mp4
duration: 85.200s
frames: 2556 video frames at 30fps
note: first proven edit-first master final
```

Previous proven output:

```text
version: v71 video2 lip-sync-safe final
output: /Users/gobank01/Documents/Video V2/stacked-output-v71-video2-lipsync-safe-final-bgm.mp4
duration: 85.200s
frames: 2556 video frames at 30fps
note: superseded by v72 because v72 moves the authoritative edit into pre-layout editorial masters
```

Previous proven output:

```text
version: v66 video2 noise/sync fix
output: /Users/gobank01/Documents/Video V2/stacked-output-v66-video2-noise-sync-fix.mp4
duration: 87.054333s
frames: 2611 video frames at 30fps
video: h264 1080x1920, 30fps
audio: AAC, 48kHz, stereo
source duration: 115.946s
content dropped: 28.446s / 853 frames
soft-cut overlap removed: 0.446s / 13 frames
total net removed: 28.892s / 867 frames
B-roll: 5 local Pexels stock sources reused, 5 optimized derivatives, 0 new downloads, 0 AI generations, 0 rejected candidates
B-roll fresh sourcing: attempted, blocked because PEXELS_API_KEY was not present in shell env
B-roll replacement: 15s / 450 frames
transition mix: 2.36s / 71 frames
audio fix: dropped 0-2.3s false start, rebuilt from raw bottom audio with denoise/gate, logged 21ms audio delay compensation
QA: pass, with only timeline_track_too_dense warning
reports: reports/frame-edit-report-v66-video2.json, reports/final-report-v66-video2.md
contact sheets: render-checks/video2-v66-final/contact-sheet.jpg, render-checks/video2-v66-final-broll/contact-sheet.jpg
```

Previous proven output:

```text
version: v65 video2 v64 full test
output: /Users/gobank01/Documents/Video V2/stacked-output-v65-video2-v64-full-test.mp4
duration: 89.354333s
video: 1080x1920, 30fps, h264
audio: AAC, 48kHz, stereo
B-roll: 5 local Pexels stock sources reused, 5 optimized derivatives, 0 new downloads, 0 AI generations, 0 rejected candidates
QA: pass, with only timeline_track_too_dense warning
```

```text
version: v63 video2 full edit
output: /Users/gobank01/Documents/Video V2/stacked-output-v63-video2-context90-full.mp4
duration: 89.354333s
video: 1080x1920, 30fps, h264
audio: AAC, 48kHz, stereo
B-roll: 8 local Pexels stock sources reused, 8 optimized derivatives, 0 new downloads, 0 AI generations, 3 rejected candidates
QA: pass, with only timeline_track_too_dense warning
```

```text
version: v35 full context test
output: /Users/gobank01/Documents/Video V2/stacked-output-v35-test2-full-context-softcut-broll-full-test.mp4
duration: 59.354s
video: 1080x1920, 30fps, h264
audio: AAC, 48kHz, stereo
B-roll: 10 fresh Pexels selections, 30 candidates downloaded, 20 rejected, 10 optimized
QA: pass, with only timeline_track_too_dense warning
```

v36 เพิ่ม rule preserve key spoken terms  
v37 แยก editable key terms  
v38 แยก workflow docs เพื่อพัฒนาต่อและแจกต่อ  
v39 กาง step แบบละเอียด 425 steps ครอบคลุมทั้ง automation map  
v40 ย้าย 425 steps ไป `STEPS_DETAILED_425.md` และทำ `STEPS.md` เป็น practical edit map 99 steps  
v41 ย้าย 99 steps ไป `STEPS_PRACTICAL_99.md` และทำ `STEPS.md` เป็น practical edit map 62 steps สำหรับเริ่มแก้จริง
v42 เพิ่ม bottom-master sync policy: bottom สำคัญกว่า และต้องแจ้งผู้ใช้เมื่อพบ duration/start/drift mismatch
v43 เพิ่ม `SYNC_REPORT.md` สำหรับ sync decisions
v44 เพิ่ม `schemas/context-index.schema.json`
v45 เพิ่ม `KEYTERM_QA.md` และ `npm run check:keyterms`
v46 เพิ่ม `MOTION_BGM.md`, zoom in/out rules และ BGM loop rules
v47 เพิ่ม `scripts/mix-bgm.js` และ `npm run mix:bgm` สำหรับ mix BGM loop ใต้ bottom voice
v48 ตั้ง BGM default เป็น 5% (`--gain-percent 5`) และเพิ่ม policy เรื่อง source/license ห้ามใช้เพลงที่สิทธิ์ไม่ชัดเจน
v49 เพิ่ม `BGM_LIBRARY.md`, local Mixkit stock 15 tracks และ `npm run check:bgm`
v50 ตั้ง `mixkit-480 Curiosity` เป็น default BGM fallback พร้อม tech/calm fallback และ test policy 5%
v51 เพิ่ม rule: BGM QA ต้อง mix/test กับ final MP4 จริง และเทียบ loudness/preview ก่อนหลัง
v52 บันทึก user acceptance: BGM 5% ควรเป็น ambient bed ที่แทบไม่ได้ยิน เสียงพูดต้องชัดก่อนเสมอ
v53 เพิ่ม `scripts/select-bgm.js`, `npm run select:bgm` และ keyword map ที่แก้ได้สำหรับเลือก BGM อัตโนมัติ
v54 เพิ่ม `scripts/qa-bgm-final.js` และ `npm run qa:bgm` สำหรับเลือก/mix/preview/loudness QA กับ final MP4 จริงอัตโนมัติ
v55 เพิ่ม `NEXT_SESSION.md` เพื่อบันทึก checkpoint, ผลทดสอบล่าสุด และงานที่ควรทำต่อ
v56 เพิ่ม `scripts/final-report.js` และ `npm run report:final` สำหรับรวม final MP4 metadata, context cut, B-roll, BGM QA, key term QA เป็น JSON + Markdown report
v57 เพิ่ม `scripts/auto-final-bgm.js` และ `npm run auto:bgm` สำหรับเลือก final MP4 ล่าสุดที่ยังไม่ใช่ BGM/preview แล้วส่งเข้า Auto Final BGM QA
v58 เพิ่ม `scripts/finalize-video.js` และ `npm run finalize:video` สำหรับรวม post-render Auto BGM + final report เป็นคำสั่งเดียว
v59 เพิ่ม B-roll Transition Mix Engine, metadata `transitionMix`, และ `npm run check:transition` เพื่อตรวจ B-roll entry/exit, bridge transition และ border-stable pan
v60 เพิ่ม `scripts/frame-edit-report.js`, `npm run report:frames` และกติกาสรุป edited/removed frames ทุกงาน
v61 เพิ่ม B-roll spacing rule: ห้าม B-roll ถี่จนใน 6 วินาทีมี 2 อัน และต้องเหลือ footage จริงของ top อย่างน้อย 3 วินาทีระหว่าง B-roll
v62 เพิ่ม slow inner-media zoom: แยก top frame shell ออกจาก video media, zoom เฉพาะ top/B-roll inner media, ห้ามขยับ top/bottom frame และเพิ่ม `npm run check:motion`
v63 ตัดต่อ video2 ใหม่ทั้งหมดเป็น 89.354s โดยใช้ bottom audio เป็น master, context cut แบบ Medium, soft cut คู่ขนาน top/bottom, B-roll 8 จุดจาก local Pexels stock และ reject 3 candidate ที่เสี่ยง graphic/text
v64 เพิ่มกฎ sync lock แบบ frame-accurate, Whisper required ทุกงาน, sequential execution gates, B-roll fresh-stock policy จน stock index ครบ 200 clips, B-roll density cap ไม่เกิน 4 อันต่อ 1 นาที และ duration target แบบ meaning-first ไม่ต้องยืดให้ชนเวลา
v65 ทดสอบ full edit video2 ตามกฎ v64 สำเร็จ: sync lock ผ่าน, Whisper transcript พร้อม, B-roll ลดเหลือ 5 จุดตาม density cap, render output `stacked-output-v65-video2-v64-full-test.mp4`, frame report/final report พร้อมใช้งาน
v66 แก้ noise/sync: ตัด false-start 0-2.3s, เปลี่ยนมา polish จาก raw bottom audio, เพิ่ม denoise/gate chain ใหม่, log audio delay 21ms เพื่อชดเชย stream start mismatch และ render output `stacked-output-v66-video2-noise-sync-fix.mp4`
v67 เพิ่ม `MISTAKES.md` เพื่อบันทึกความผิดพลาด v65/v66 และ hard gates: opening sustained speech, audio source proof, noise proof, final stream start_time sync, caption remap proof และ final summary ต้องรายงาน gates เหล่านี้
v68 เพิ่ม `LIPSYNC_QA.md` และ zero-tolerance lip-sync gate: ห้ามส่ง final ถ้าไม่มี final stream start_time check, compensation log เมื่อจำเป็น, spot-check อย่างน้อย 5 จุด และ residual risk ต้องเป็น none
v69 บันทึก root cause lip-sync: v66 xfade bottom face และ acrossfade speech ที่ content cuts ทำให้เกิด ghost/double-mouth frames; ต่อไป soft cut ต้องเป็น lip-sync-safe ห้าม xfade bottom face ตอน visible และต้องมี cut contact sheet ก่อนเรียก final
v70 เพิ่ม timestamped clip QA: ทุกครั้งที่ตรวจคลิปต้องสร้าง contact sheet ที่มี timestamp กำกับทุก 1 วินาที ด้วย `npm run qa:timestamps` เพื่อไล่ lip sync, cut, caption, B-roll และ timeline ได้แม่นขึ้น
v71 ตัดต่อ video2 ใหม่ทั้งหมดแบบ final: ใช้ bottom audio เป็น master, ตัด false start/dead air, ตัดแบบ lip-sync-safe hard concat ไม่มี visible bottom xfade, B-roll 5 จุดตาม density cap, BGM Mixkit 5%, timestamp QA ทุก 1 วินาที, cut contact sheet และ final report ผ่าน
v72 เปลี่ยน architecture เป็น edit-first master: สร้าง top visual, bottom visual และ speech audio master ที่ frame/sample lock ก่อนเข้า HyperFrames, render visual-only แล้ว mux speech audio กลับทีหลัง เพื่อกัน lip-sync drift จาก layout/render stage
v73 เพิ่ม completion marker rule: ทุกครั้งที่ task เสร็จสมบูรณ์และ verify แล้ว final response ต้องแสดง `✅✅✅` แบบชัดเจน
v74 ทดสอบตัดต่อ full render ด้วย edit-first master pipeline: render visual-only, mux speech audio master, mix BGM 5%, สร้าง timestamp QA, frame report, keyterm QA และ final report ผ่าน
v75 เพิ่ม single final output rule: เวลาส่งงานให้ผู้ใช้แสดง Output เดียวคือ Final MP4 เท่านั้น ส่วน visual-only/no-BGM/intermediate เป็น internal QA artifact
v76 เพิ่ม choice-based user decision gate: ก่อนข้าม decision สำคัญให้ถามเป็นตัวเลือก 2-3 ข้อแบบคลิก/เลือกง่าย ถ้าผู้ใช้ให้ direction ตั้งแต่แรกให้ใช้เป็น anchor
v77 เพิ่ม rough direction trim gate: Step 20.1-21 ต้องรับ user rough direction, สร้าง start/end candidates จาก hint+evidence, ห้ามเดาล้วน, รายงานเมื่อ evidence ขัดกับ hint และ lock trim พร้อม frame/sample/evidence
v78 เพิ่ม phase-gated testing: ทุกการทดสอบต้องจบทีละ Phase พร้อม artifact/QA/risk report และรอ user pass ก่อนข้าม Phase ถัดไป ยกเว้นสั่ง auto/full mode ชัดเจน
v79 เพิ่ม raw bottom lip-sync human gate: metadata ตรงไม่พอ ต้อง preview bottom face + bottom audio จริงก่อนรับ set เข้า pipeline; human fail ถือเป็น blocker แม้ duration/frame/start_time จะตรง
v80 ล้าง generated artifacts แล้ว rebuild Set B เท่านั้นจนถึง Phase 5 เพื่อทำ bottom lip-sync proof และ stacked preview ใหม่: frame/duration/start_time/silence QA ผ่าน รอ human lip-sync gate

## How To Continue Development

1. เพิ่ม/แก้ step ใน `STEPS.md`
2. เพิ่มค่าที่แก้ได้ใน `CONFIG.md`
3. เพิ่ม checklist ใน `QA.md`
4. เพิ่ม output/report format ใน `REPORT_TEMPLATE.md`
5. บันทึก version ใหม่ใน `CHANGELOG.md`
6. ถ้าเป็น rule ที่ agent ต้องทำทุกครั้ง ให้ sync เข้า `AGENTS.md` หรือ skill `bizdrive-video`
