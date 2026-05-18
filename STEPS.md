# Bizdrive Video Steps

สถานะล่าสุด: v54 - practical edit map 62 steps with auto final BGM QA

ไฟล์นี้คือ step แบบใช้งานจริงสำหรับเริ่มแก้ workflow ต่อ มี 62 steps ตามฐานล่าสุดที่ต้องการใช้แก้ ส่วน reference ที่ละเอียดกว่าอยู่ใน `STEPS_PRACTICAL_99.md` และ `STEPS_DETAILED_425.md`

## Phase 1 — Intake

1. อ่าน `WORKFLOW.md`, `CONFIG.md`, `QA.md`, `AGENTS.md`
2. ระบุโจทย์จากผู้ใช้ เช่น full render, test render, shorten, B-roll, caption, QA
3. ระบุ target duration ถ้ามี
4. ถ้าไม่ fix duration ให้ใช้ meaning-first duration
5. ระบุ output filename และ version ที่จะใช้

## Phase 2 — Input And Sync

6. หา background image, top/screen video, bottom/face video
7. ยืนยัน top คือหน้าจอและต้อง mute
8. ยืนยัน bottom คือหน้าคนและเป็นเสียงหลัก
9. ยืนยัน top/bottom เป็นคลิปที่ sync กัน โดย bottom audio เป็น master timeline
10. ตรวจว่าไฟล์อยู่ใน path ที่ composition ใช้ได้
11. ตรวจว่าไม่มี API key ถูกเขียนลงไฟล์

## Phase 3 — Media Inspection

12. ใช้ `ffprobe` ตรวจ top และ bottom
13. ตรวจ duration, fps, resolution ของ top/bottom
14. ตรวจ bottom มี audio stream
15. ตรวจ top audio ไม่ถูกใช้
16. ถ้า top/bottom duration หรือ start offset ต่างกัน ให้แจ้งผู้ใช้ก่อน และใช้ bottom เป็น master เพื่อวิเคราะห์ sync/align

## Phase 4 — True Start / End

17. ใช้ bottom audio เป็นหลักในการหา start
18. ตัด cough, throat clear, false start, pause/reset ก่อนเริ่มจริง
19. true start คือจุดที่เริ่มพูดจริงและพูดต่อเนื่องประมาณ 30s+
20. หา end ที่เนื้อหาจบจริงหรือเข้าสู่ trailing silence
21. บันทึก trimStart, trimEnd และเหตุผล

## Phase 5 — Parallel Trim And Dead Air

22. trim top ด้วย trimStart/trimEnd
23. trim bottom ด้วย trimStart/trimEnd เดียวกัน
24. ห้าม trim เฉพาะ top หรือ bottom อย่างเดียว
25. re-encode top/bottom เป็น 30fps / GOP 30 / faststart
26. ตรวจ duration หลัง trim ของ top/bottom
27. ใช้ bottom audio ตรวจ silence
28. ตัด silence > 0.5s ตาม threshold ใน `CONFIG.md`
29. ใช้ dead-air cut list เดียวกันกับ top และ bottom
30. สร้าง `top_deadair_cut.mp4` และ `bottom_deadair_cut.mp4`
31. ตรวจว่าไม่เหลือ silence ยาวเกิน policy

## Phase 6 — Audio Polish

32. ใช้ bottom clean เป็น source
33. apply highpass, noise reduction, compressor, loudness normalization และ limiter
34. target loudness คือ -16 LUFS และ true peak ไม่เกิน -1.5 dBTP
35. สร้าง `bottom_audio_polished.mp4`
36. ตรวจ loudness report และ spot check เสียงพูด

## Phase 7 — Transcript And Key Terms

37. ถอดเสียงจาก bottom polished
38. ใช้ Whisper large-v3 ภาษาไทยเมื่อพร้อม
39. เก็บ raw transcript และสร้าง cleaned transcript
40. ตัด filler เช่น อืม, อะ, อ่ะ, เอ่อ
41. แก้คำทับศัพท์ เช่น พร้อม -> prompt เมื่อบริบทถูกต้อง
42. โหลด Editable Key Terms จาก `CONFIG.md`
43. เพิ่ม key terms เฉพาะคลิปถ้าจำเป็น
44. mark key terms และห้ามลบระหว่าง clean/cut

## Phase 8 — Context Index And Cut

45. แบ่ง transcript เป็น meaning segments
46. sample screen ทุกประมาณ 5s และรอบ likely cut/B-roll points
47. สร้าง Full context index พร้อม speech, topic, intent, screenContext
48. ใส่ importanceScore, redundancyScore, fillerScore, cutRisk
49. ใส่ captionKeywords, brollKeyword, brollQuery, keep/drop reason
50. เลือก keep/drop segments จากสาระ ไม่ตัดแบบหารเวลาเท่า ๆ กัน
51. ตรวจว่า key terms สำคัญยังอยู่ใน keep segments
52. ใช้ soft cut ทุก content cut และหลีกเลี่ยงตัดกลางคำ/key term
53. render softcut top และ softcut bottom

## Phase 9 — B-roll

54. กำหนดจำนวน B-roll ตามโจทย์
55. เลือก slot จาก context ไม่ใช่คำเดี่ยว
56. ใช้ speech ก่อนและหลัง slot เพื่อเลือก broad keyword
57. ตรวจ stock index ก่อน แล้วค่อยโหลด Pexels candidate ใหม่ถ้าต้องการคุณภาพดีที่สุด
58. fallback เป็น OpenRouter `google/veo-3.1-lite` และ premium fallback เป็น `kwaivgi/kling-v3.0-std`
59. reject text, logo, watermark, other brand, distracting graphic
60. re-encode selected B-roll และสร้าง manifest พร้อม downloaded/generated/reused/optimized/rejected counts

## Phase 10 — Captions, Composition, QA

61. สร้าง captions จาก cleaned transcript, จำกัด cue ประมาณ 20 ตัวอักษร, ไม่ตัดคำไทยครึ่งคำ, ใช้ Bizdrive caption style
62. ถ้าเปิดใช้ BGM ให้รัน `npm run qa:bgm` ด้วย final MP4 จริง + title/transcript/context เพื่อเลือกจาก `bgm-library/mixkit-stock-v50.json`, ถ้าเลือกไม่ออกให้ใช้ `mixkit-480 Curiosity`, ยืนยัน source/license, รัน `npm run check:bgm`, mix ด้วย default `--gain-percent 5`, ตั้งใจให้ BGM แทบไม่ได้ยินและห้ามให้เพลงกลบหรือดึงความสนใจจากเสียงพูด, สร้าง preview/loudness report ก่อนหลัง, QA metadata/audio/B-roll/captions/key terms/motion/BGM, สร้าง final report และเก็บ artifacts
