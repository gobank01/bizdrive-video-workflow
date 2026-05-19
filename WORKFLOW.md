# Bizdrive Video Workflow

สถานะล่าสุด: v66 NOISE/SYNC FIX - ตัด false-start ต้นคลิป, ปรับ audio polish ใหม่ และชดเชย sync ที่วัดได้

ไฟล์นี้เป็น overview ของระบบตัดต่อ Bizdrive stacked video ด้วย HyperFrames ส่วนรายละเอียดให้ดูไฟล์แยกตามหัวข้อด้านล่าง

## Documents

```text
WORKFLOW.md               overview และลำดับระบบหลัก
STEPS.md                  practical step-by-step 62 steps สำหรับแก้งานจริง
STEPS_PRACTICAL_99.md     archived practical reference 99 steps
STEPS_DETAILED_425.md     detailed automation reference 425 steps
CONFIG.md                 ค่าที่แก้ได้ เช่น key terms, layout, audio, caption, B-roll
QA.md                     checklist ก่อน render / หลัง render / final delivery
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
version: v66
base output size: 1080x1920
top frame: 1080x607.5, radius 30px, gold gradient border 4px
bottom frame: 607.5x607.5 circle, gold gradient border 4px
gap top/bottom: ~40px
audio target: -16 LUFS, true peak <= -1.5 dBTP, speech-first noise gate
dead air rule: cut silence longer than 0.5s in parallel
false-start rule: if the opening has a short non-sustained sound/word followed by silence/reset, cut it before the true start
context cut default: Medium
context index: Full
soft cut: always, default 0.12s crossfade
B-roll duration: 3s each
B-roll count: max 4 per 60s of final video, minimum 3 when the clip is long enough
B-roll fresh-stock policy: try fresh download first until QA-passed stock index reaches 200 usable clips
B-roll stock index: assets/broll/index.json
B-roll spacing: minimum 6s between B-roll starts and minimum 3s real top footage between B-rolls
B-roll provider order: Pexels -> OpenRouter veo-3.1-lite -> OpenRouter kling-v3.0-std
B-roll transition mix: enabled, soft 0.22s, bridge 0.26s for jump-cover slots
transition QA command: npm run check:transition
frame edit report command: npm run report:frames
caption max length: about 20 Thai characters, never split Thai words
sync master: bottom audio
sync lock: top video, bottom audio/video, and captions must stay on the same edited timeline with no unlogged offset drift
sync compensation: allowed only when measured, logged in context/report, and applied to the bottom-master pipeline
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
BGM auto latest final command: npm run auto:bgm
final report command: npm run report:final
post-render finalize command: npm run finalize:video
BGM default fallback: mixkit-480 Curiosity
BGM tech fallback: mixkit-1167 Close Up
BGM calm fallback: mixkit-441 Meditation
BGM final-real-file QA: required
BGM mix command: npm run mix:bgm
```

## Master Pipeline

1. Prepare input files.
2. Inspect raw media metadata.
3. Confirm top/bottom roles and sync.
4. Find true spoken start; reject false starts before sustained speech.
5. Trim top and bottom in parallel.
6. Cut dead air in parallel.
7. Re-encode clean media for reliable seeking.
8. Polish bottom audio from the cleanest verified bottom source, preferably raw bottom audio, with speech-first denoise/gate before loudnorm.
9. Transcribe polished audio with Whisper; do not skip transcription.
10. Clean transcript and mark editable key terms.
11. Build Full context index.
12. Decide keep/drop segments from meaning.
13. Apply soft cuts to top and bottom.
14. Select B-roll slots from context.
15. Search/download/index B-roll first; reuse only when indexed stock is clearly the best match or stock count is already mature.
16. QA B-roll and reject text/logo/brand/graphic failures.
17. Re-encode selected B-roll.
18. Build captions with Bizdrive style.
19. If BGM is enabled, run `npm run select:bgm` to select from stock using title/transcript/context; generate only when no stock mood fits.
20. Add B-roll transition mix, optional zoom motion, and BGM loop if enabled.
21. Update HyperFrames composition.
22. Run `npm run check`.
23. Render full MP4.
24. QA output frames, audio, BGM, motion, captions, key terms, and B-roll; after a full render, prefer `npm run finalize:video` to run Auto BGM and final report together.
25. Write frame edit report with `npm run report:frames`.
26. Write final report with `npm run report:final`.
27. Update changelog/workflow version when rules change.

## Sequential Execution Gates

ทุกงานต้องทำตามลำดับ step ห้ามข้าม ถ้า step หนึ่งยังไม่ผ่าน QA ให้แก้ step นั้นก่อนค่อยไปต่อ

```text
1. ก่อนเริ่ม step ถัดไป ให้บอกผู้ใช้ว่าอยู่ Step ไหนและกำลังทำอะไร
2. หลังจบ step ให้เช็ค artifact/QA ที่พิสูจน์ step นั้น เช่น ffprobe, transcript, context index, manifest, contact sheet, npm check
3. ถ้า check fail ให้หยุดแก้ ไม่ข้ามไป render หรือ final report
4. ถ้า command/tool สำคัญ fail เช่น Whisper ให้ใช้ fallback ที่เทียบเท่า เช่น direct whisper-cli แต่ต้องยังมี transcript ก่อน context/caption
5. ทุก timing decision ต้องอิง bottom master timeline และบันทึกใน context/manifest/report
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
ทุก rule change ต้องนับ version
```

## Latest Proven Output

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

## How To Continue Development

1. เพิ่ม/แก้ step ใน `STEPS.md`
2. เพิ่มค่าที่แก้ได้ใน `CONFIG.md`
3. เพิ่ม checklist ใน `QA.md`
4. เพิ่ม output/report format ใน `REPORT_TEMPLATE.md`
5. บันทึก version ใหม่ใน `CHANGELOG.md`
6. ถ้าเป็น rule ที่ agent ต้องทำทุกครั้ง ให้ sync เข้า `AGENTS.md` หรือ skill `bizdrive-video`
