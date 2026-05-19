# Bizdrive Video Steps

สถานะล่าสุด: v78 - phase-gated testing: ทดสอบทีละ Phase ผ่านแล้วค่อยไปต่อ

ไฟล์นี้คือ step แบบใช้งานจริงสำหรับเริ่มแก้ workflow ต่อ มี 62 steps ตามฐานล่าสุดที่ต้องการใช้แก้ ส่วน reference ที่ละเอียดกว่าอยู่ใน `STEPS_PRACTICAL_99.md` และ `STEPS_DETAILED_425.md`

## Phase Gate Mode

ตั้งแต่งาน v78 เป็นต้นไป การทดสอบและการตัดต่อให้ทำทีละ Phase เสมอ เมื่อจบ Phase ต้องหยุดและแสดงหลักฐานให้ผู้ใช้ตรวจ ก่อนข้ามไป Phase ถัดไป

ตัวเลือกหลังจบแต่ละ Phase:

```text
A. ผ่าน ไป Phase ถัดไป (Recommended เมื่อหลักฐานครบ)
B. ไม่ผ่าน ย้อนแก้ Phase นี้
C. ขอหลักฐานเพิ่ม
```

ห้ามข้าม Phase ถ้า user ยังไม่กดผ่าน/ตอบผ่าน ยกเว้นผู้ใช้สั่งชัดเจนว่าให้ทำแบบ auto/full โดยไม่ต้องรอ gate ระหว่างทาง ถ้า Phase ใดไม่ผ่าน QA ให้ย้อนแก้ Phase นั้นก่อน แล้วส่งหลักฐานใหม่จนกว่าจะผ่าน

## Phase 1 — Intake

1. อ่าน `WORKFLOW.md`, `CONFIG.md`, `QA.md`, `AGENTS.md`, `MISTAKES.md`, `LIPSYNC_QA.md`
2. ระบุโจทย์จากผู้ใช้ เช่น full render, test render, shorten, B-roll, caption, QA
3. ระบุ target duration ถ้ามี
4. ถ้ามี target duration ให้ถือเป็นเพดาน/เป้าหมาย ไม่ต้องยืดให้ชนเวลา ถ้าสาระครบและสั้นกว่า เช่น 1:30 เหลือ 1:20 ให้ใช้ 1:20
5. ระบุ output filename และ version ที่จะใช้
5.1 ประกาศกับผู้ใช้ว่าอยู่ Step/Phase ไหนและกำลังทำอะไร
5.2 ก่อนข้าม phase ให้เช็คว่า artifact/QA ของ phase ก่อนหน้าครบแล้ว
5.3 ระบุ hard gates จาก `MISTAKES.md` ที่ต้องพิสูจน์ในงานนี้
5.4 ระบุ lip-sync proof ที่ต้องมีตาม `LIPSYNC_QA.md`
5.5 ถ้างานเป็น production/full render ให้ประกาศว่าจะใช้ edit-first master: ตัดต่อและล็อก sync ก่อนเข้า HyperFrames layout
5.6 ถ้าโจทย์ยังขาด creative/editorial direction ให้ถามผู้ใช้เป็นตัวเลือก 2-3 ข้อแบบคลิก/เลือกง่าย ไม่บังคับพิมพ์ยาว
5.7 ตั้ง Phase Gate Mode: หลังจบแต่ละ Phase ต้องสรุป artifact/QA และรอ user เลือก ผ่าน / ย้อนแก้ / ขอหลักฐานเพิ่ม ก่อนข้าม Phase ถัดไป

## Phase 2 — Input And Sync

6. หา background image, top/screen video, bottom/face video
7. ยืนยัน top คือหน้าจอและต้อง mute
8. ยืนยัน bottom คือหน้าคนและเป็นเสียงหลัก
9. ยืนยัน top/bottom เป็นคลิปที่ sync กัน โดย bottom audio เป็น master timeline
10. ตรวจว่าไฟล์อยู่ใน path ที่ composition ใช้ได้
11. ตรวจว่าไม่มี API key ถูกเขียนลงไฟล์
11.1 ตั้ง sync lock: top, bottom audio/video และ captions ต้องอยู่ timeline เดียวกัน ห้ามเลื่อนแยก

## Phase 3 — Media Inspection

12. ใช้ `ffprobe` ตรวจ top และ bottom
13. ตรวจ duration, fps, resolution ของ top/bottom
14. ตรวจ bottom มี audio stream
15. ตรวจ top audio ไม่ถูกใช้
16. ถ้า top/bottom duration หรือ start offset ต่างกัน ให้แจ้งผู้ใช้ก่อน และใช้ bottom เป็น master เพื่อวิเคราะห์ sync/align
16.1 ถ้า sync ยังไม่ชัด ให้หยุดแก้ sync ก่อน ห้ามไป true start/context/caption
16.2 ตั้ง lip-sync zero tolerance: ถ้าไม่มั่นใจ 100% ห้ามส่ง final

## Phase 4 — True Start / End

17. ใช้ bottom audio เป็นหลักในการหา start
18. ตัด cough, throat clear, false start, pause/reset ก่อนเริ่มจริง
19. true start คือจุดที่เริ่มพูดจริงและพูดต่อเนื่องประมาณ 30s+
19.1 ถ้าช่วงแรกมีเสียง/คำสั้นแล้วตามด้วย silence/reset ก่อนพูดยาว ให้ถือเป็น false start แม้ Whisper จะจับคำได้
19.2 ก่อน lock true start ให้ถามเป็นตัวเลือกถ้ายังไม่มี user hint: ใช้ hint ผู้ใช้ / ให้ AI หาเอง / ส่ง candidates ให้เลือก
20. หา end ที่เนื้อหาจบจริงหรือเข้าสู่ trailing silence
20.1 รับ user rough direction ถ้ามี เช่น start คร่าว ๆ, end คร่าว ๆ, must keep, must remove, target duration และ tone การตัด
20.2 AI สร้าง start/end candidates จาก user hint + audio evidence + rough transcript + silence/VAD evidence ไม่ใช่จากการเดาล้วน
20.3 ถ้ามี user hint ต้องใช้เป็น anchor เสมอ; AI ห้ามเลือกจุดตัดที่ไม่สัมพันธ์กับ hint โดยไม่อธิบายเหตุผล
20.4 ถ้าหลักฐานขัดกับ user hint ต้องรายงานก่อน เช่น ผู้ใช้บอกเริ่ม 24s แต่เสียงพูดจริงเริ่ม 23.6s แล้วให้เลือก/ยืนยันก่อน lock
20.5 ก่อน lock end ให้ถามเป็นตัวเลือกถ้ายังไม่รู้ direction: จบหลัง CTA / ให้ AI หา end / ส่ง candidates ให้เลือก
21. lock trimStart/trimEnd พร้อม user choice, rough direction, selected candidate, rejected candidates, frame/sample values, evidence และเหตุผล

## Phase 5 — Parallel Trim And Dead Air

22. trim top ด้วย trimStart/trimEnd
23. trim bottom ด้วย trimStart/trimEnd เดียวกัน
24. ห้าม trim เฉพาะ top หรือ bottom อย่างเดียว
25. re-encode top/bottom เป็น 30fps / GOP 30 / faststart
26. ตรวจ duration หลัง trim ของ top/bottom
27. ใช้ bottom audio ตรวจ silence
28. ก่อนตัด dead air ให้ถามเป็นตัวเลือกถ้ายังไม่มี direction: ตัด silence >0.5s ทั้งหมด / ตัดเฉพาะ silence ยาวมาก / ให้ AI เสนอ cut list
29. ใช้ dead-air cut list เดียวกันกับ top และ bottom
30. สร้าง `top_deadair_cut.mp4` และ `bottom_deadair_cut.mp4`
31. ตรวจว่าไม่เหลือ silence ยาวเกิน policy
31.1 ตรวจว่า top/bottom ยังมีจำนวนเฟรมและ duration ตรงกันหลังตัดคู่ขนาน
31.2 ตรวจ final-prep gate จาก `MISTAKES.md`: opening sustained speech, audio source proof, noise proof, caption map proof
31.3 ตรวจ lip-sync pre-render gate: ไม่มี independent retime/offset, top/bottom edited frame count ตรง, captions mapped to edited timeline
31.4 ถ้าเป็น production ให้ยังไม่เข้า layout จนกว่าจะสร้าง editorial masters และ QA ผ่าน

## Phase 6 — Audio Polish

32. ใช้ bottom clean เป็น source; ถ้าไฟล์ polished เดิมมี noise/sync risk ให้กลับไปใช้ raw bottom audio
33. apply speech-first chain: highpass/lowpass, afftdn, agate noise gate, compressor, loudness normalization และ limiter
33.1 ถ้า final stream หรือ sync point บอกว่า audio/video start offset จริง ให้ชดเชยได้เฉพาะเมื่อบันทึกค่า ms และเหตุผลใน context/report
34. target loudness คือ -16 LUFS และ true peak ไม่เกิน -1.5 dBTP
35. สร้าง `bottom_audio_polished.mp4`
36. ตรวจ loudness report และ spot check เสียงพูด

## Phase 7 — Transcript And Key Terms

37. ถอดเสียงจาก bottom polished
38. ต้องใช้ Whisper large-v3 ภาษาไทยเป็น default ทุกงาน
38.1 ถ้า HyperFrames transcribe fail ให้ใช้ direct `whisper-cli` หรือ fallback ที่ให้ timestamp ได้ ห้ามข้าม transcript
39. เก็บ raw transcript และสร้าง cleaned transcript
40. ตัด filler เช่น อืม, อะ, อ่ะ, เอ่อ
41. แก้คำทับศัพท์ เช่น พร้อม -> prompt เมื่อบริบทถูกต้อง
42. โหลด Editable Key Terms จาก `CONFIG.md`
43. เพิ่ม key terms เฉพาะคลิปถ้าจำเป็น
44. mark key terms และห้ามลบระหว่าง clean/cut
44.1 ตรวจ transcript timestamp ก่อนสร้าง context/caption เพราะ caption ต้อง map กับ edited timeline

## Phase 8 — Context Index And Cut

45. แบ่ง transcript เป็น meaning segments
46. sample screen ทุกประมาณ 5s และรอบ likely cut/B-roll points
47. สร้าง Full context index พร้อม speech, topic, intent, screenContext
48. ใส่ importanceScore, redundancyScore, fillerScore, cutRisk
49. ใส่ captionKeywords, brollKeyword, brollQuery, keep/drop reason
50. เลือก keep/drop segments จากสาระ ไม่ตัดแบบหารเวลาเท่า ๆ กัน
50.1 ก่อนเลือก keep/drop final ให้ถาม cut aggressiveness เป็นตัวเลือก: Conservative / Medium / Aggressive
51. ตรวจว่า key terms สำคัญยังอยู่ใน keep segments
52. ใช้ soft cut ทุก content cut แต่ต้องเป็น lip-sync-safe: หลีกเลี่ยงตัดกลางคำ/key term และเลือกจุด silence/closed-mouth/speech boundary เมื่อ bottom ยัง visible
53. render context cut โดย top/B-roll ใช้ xfade ได้ แต่ bottom face ห้าม xfade ตอน visible; ถ้า jump cut ของ bottom ดูแรง ให้ใช้ B-roll/bridge ปิดช่วง jump หรือใช้ hard cut ที่จุดปลอดภัย
53.1 ตรวจว่า softcut top/bottom duration, fps และ frame count ตรงกัน ก่อนทำ B-roll/caption
53.2 สร้าง contact sheet รอบ content cut ทุกจุด และต้องไม่เห็น ghost/double-mouth frame ก่อน render final
53.3 สร้าง edit-first masters ก่อนเข้า HyperFrames: `top_edit_master.mp4`, `bottom_visual_master.mp4`, `speech_audio_master.wav`, และ `bottom_editorial_master.mp4`
53.4 ตรวจ master proof: top/bottom duration เท่ากัน, frame count เท่ากัน, start_time 0, speech audio duration/sample rate ถูกต้อง, และ `silencedetect` ไม่เจอ silence >0.5s
53.5 ถ้า master proof fail ให้ย้อนกลับไปแก้ EDL/cut list ห้ามไป B-roll/layout/render

## Phase 9 — B-roll

54. กำหนดจำนวน B-roll ตามโจทย์ แต่ต้องไม่เกิน 4 อันต่อ final video 1 นาที เว้นแต่ผู้ใช้ override ชัดเจน
54.1 ก่อนทำ B-roll ให้ถามเป็นตัวเลือกถ้ายังไม่มี direction: ใส่ B-roll / ไม่ใส่ / ให้ AI แนะนำจำนวน
54.2 ก่อน sourcing ให้ถามเป็นตัวเลือกถ้ายังไม่มี direction: โหลดใหม่ก่อน / ใช้ stock ก่อน / ผสมสองแบบ
55. เลือก slot จาก context ไม่ใช่คำเดี่ยว
56. ใช้ speech ก่อนและหลัง slot เพื่อเลือก broad keyword
57. ตรวจ stock index เพื่อรู้ว่ามีอะไรแล้ว แต่ default ให้พยายามโหลด Pexels candidate ใหม่ก่อนเพื่อสะสม stock จนมี QA-passed footage อย่างน้อย 200 clips
57.1 ถ้า stock index ครบ 200 QA-passed clips แล้ว ให้ reuse เป็น default แต่ต้องโหลดใหม่เมื่อ context ไม่ match
57.2 ทุก candidate ที่โหลด/เลือก/reject ต้องบันทึก keyword, category, source, QA status ลง manifest หรือ stock index
58. fallback เป็น OpenRouter `google/veo-3.1-lite` และ premium fallback เป็น `kwaivgi/kling-v3.0-std`
59. reject text, logo, watermark, other brand, distracting graphic
60. re-encode selected B-roll และสร้าง manifest พร้อม downloaded/generated/reused/optimized/rejected counts
60.1 เว้นจังหวะ B-roll ให้ไม่ลายตา: B-roll starts ห่างกันอย่างน้อย 6s และมี footage จริงของ top อย่างน้อย 3s ระหว่าง insert; ถ้า jump cut ถี่ ให้เลือก B-roll เดียวที่สำคัญกว่า หรือใช้ bridge B-roll หนึ่งอันแทนการใส่ติดกัน
60.2 ใส่ transition mix metadata ทุก slot: soft สำหรับ B-roll ปกติ, bridge สำหรับ B-roll ที่ cover jump cut, แล้วรัน `npm run check:transition`
60.3 ถ้าใส่ zoom/motion ให้ใช้เฉพาะ inner media ของ top/B-roll เท่านั้น ห้าม animate frame shell หรือ bottom frame และต้องรัน `npm run check:motion`

## Phase 10 — Captions, Composition, QA

61. สร้าง captions จาก cleaned transcript หลัง trim/dead-air/context cut แล้วเท่านั้น, จำกัด cue ประมาณ 20 ตัวอักษร, ไม่ตัดคำไทยครึ่งคำ, ใช้ Bizdrive caption style
61.0 ก่อนสร้าง caption ให้ถามเป็นตัวเลือกถ้ายังไม่มี direction: clean สั้น / ใกล้เสียงพูดจริง / ให้ AI balance
61.1 ตรวจ caption timing เทียบกับ bottom audio และ edited frame timeline ห้ามใช้ raw timestamp โดยไม่ map
61.2 HyperFrames composition ต้องใช้ visual masters เป็น source และ render แบบ visual-only/audio disabled เมื่อใช้ edit-first architecture
61.3 หลัง render visual-only ให้ mux `speech_audio_master.wav` กลับเข้า MP4 แล้วค่อยทำ BGM mix/QA
61.4 ก่อน BGM ให้ถามเป็นตัวเลือกถ้ายังไม่มี direction: ใส่ BGM 5% / ไม่ใส่ BGM / ให้ AI เลือกหลังวิเคราะห์
62. หลัง full render ให้รัน `npm run finalize:video` เมื่อมี context/B-roll/keyterm report พร้อมแล้ว เพื่อเลือก final MP4 ล่าสุด, ทำ Auto BGM, และสร้าง final report ในคำสั่งเดียว; ถ้าต้องทำเฉพาะ BGM ให้ใช้ `npm run auto:bgm`, หรือใช้ `npm run qa:bgm` เมื่อจะระบุไฟล์เอง, ใช้ title/transcript/context เพื่อเลือกจาก `bgm-library/mixkit-stock-v50.json`, ถ้าเลือกไม่ออกให้ใช้ `mixkit-480 Curiosity`, ยืนยัน source/license, รัน `npm run check:bgm`, mix ด้วย default `--gain-percent 5`, ตั้งใจให้ BGM แทบไม่ได้ยินและห้ามให้เพลงกลบหรือดึงความสนใจจากเสียงพูด, สร้าง preview/loudness report ก่อนหลัง, QA metadata/audio/B-roll/captions/key terms/motion/transition/BGM, รัน `npm run report:final` เพื่อสร้าง JSON + Markdown final report และเก็บ artifacts
62.0 ก่อน full render ให้สรุป decision choices ทั้งหมดแล้วถาม confirm เป็นตัวเลือก: Render final / แก้ decision / หยุดรอ
62.1 สรุปให้ผู้ใช้ทุกครั้งว่าแต่ละ Step ผ่านอะไร, B-roll โหลดใหม่/ใช้เก่าเท่าไร, ตัดต่อกี่เฟรม, เอาออกกี่เฟรม และมี sync/caption risk หรือไม่
62.2 หลัง render ต้องตรวจ `LIPSYNC_QA.md`: final stream start_time delta, compensationMs, spot-check อย่างน้อย 5 จุด และ residualRisk ต้องเป็น none
62.3 หลัง render ต้องตรวจ cut contact sheet รอบทุก content cut ว่าไม่มี ghost/double-mouth frame จาก bottom xfade
62.4 ทุกครั้งที่ตรวจคลิป ให้สร้าง timestamped QA sheet ทุก 1 วินาทีด้วย `npm run qa:timestamps -- --input <mp4> --output-dir <dir>` และใช้ timestamp นั้นอ้างอิงปัญหา/จุดแก้เสมอ
62.5 เมื่อ task เสร็จสมบูรณ์และ verify แล้ว final response ต้องมีบรรทัด `✅✅✅` ให้เห็นชัดเจน ถ้า task ยัง blocked หรือยังไม่ verify ห้ามใช้ marker นี้
62.6 ตอนส่งผลลัพธ์ให้ผู้ใช้ ให้แสดง Output MP4 เพียงไฟล์เดียวคือ Final เท่านั้น; visual-only, no-BGM, preview, master และ report เป็น QA/internal artifact ไม่ต้อง list เป็น output หลัก ยกเว้นผู้ใช้ขอ
62.7 ทุกคำถามกับผู้ใช้ควรเป็น choice-based ก่อน: 2-3 ตัวเลือก, recommended option อยู่ก่อน, ถ้า UI รองรับให้ใช้ปุ่ม/choice prompt; ถ้าไม่รองรับให้ใช้ A/B/C และให้ตอบสั้นที่สุด
62.8 หลังจบทุก Phase ให้ทำ Phase Gate Report: Phase ที่ทำ, artifact ที่ได้, QA ที่ผ่าน/ไม่ผ่าน, risk ที่เหลือ และตัวเลือก A/B/C ให้ผู้ใช้ตัดสินใจก่อนข้าม Phase

## Modular Subprojects

ใช้เมื่ออยากแยกงานเป็นคำสั่งย่อย แทนการสั่ง full render ทุกครั้ง:

1. `transcript` - ถอดเสียง bottom, ทำ word/segment timestamp, สร้าง transcript QA
2. `sync-inspect` - ตรวจ top/bottom/audio metadata, start_time, duration, fps, frame count
3. `context-index` - วิเคราะห์เสียง + screen context แล้วสร้าง keep/drop/B-roll/caption plan
4. `edl-build` - สร้าง frame-snapped EDL จาก bottom master timeline
5. `editorial-master` - ตัด top/bottom/speech audio เป็น master ที่ lock กันก่อน layout
6. `broll-source` - หา/โหลด/เลือก/QA B-roll และ update stock index
7. `caption-build` - clean transcript, key terms, caption cues ที่ map กับ edited timeline
8. `layout-render` - render HyperFrames visual-only จาก visual masters
9. `final-mux` - mux speech audio master, mix BGM 5%, ตรวจ loudness/silence
10. `final-qa` - timestamp sheet, contact sheets, frame report, final report

หลักคิด: module ไหนผลิต artifact ได้ ให้ module ถัดไปอ่าน artifact นั้น ไม่ใช้ความจำจาก chat เป็นแหล่งข้อมูลหลัก
