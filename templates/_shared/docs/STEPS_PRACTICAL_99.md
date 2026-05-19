# Bizdrive Video Steps

สถานะล่าสุด: v40 - practical edit map 99 steps

ไฟล์นี้คือ step แบบใช้งานจริงสำหรับเริ่มแก้ workflow ต่อ มี 99 steps ส่วนเวอร์ชันละเอียด 425 steps เก็บไว้ใน `STEPS_DETAILED_425.md`

## Phase 1 — Intake

1. อ่าน `WORKFLOW.md`, `CONFIG.md`, `QA.md`, `AGENTS.md`
2. ระบุโจทย์จากผู้ใช้ เช่น full render, test render, shorten, B-roll, caption, QA
3. ระบุ target duration ถ้ามี
4. ถ้าไม่ fix duration ให้ใช้ meaning-first duration
5. ระบุ output filename และ version ที่จะใช้

## Phase 2 — Input Files

6. หา background image
7. หา top/screen video
8. หา bottom/face video
9. ยืนยัน top คือหน้าจอและต้อง mute
10. ยืนยัน bottom คือหน้าคนและเป็นเสียงหลัก
11. ยืนยัน top/bottom เป็นคลิปที่ sync กัน
12. ตรวจว่าไฟล์อยู่ใน path ที่ composition ใช้ได้
13. ตรวจว่าไม่มี API key ถูกเขียนลงไฟล์

## Phase 3 — Media Inspection

14. ใช้ `ffprobe` ตรวจ top
15. ใช้ `ffprobe` ตรวจ bottom
16. ตรวจ duration, fps, resolution ของ top/bottom
17. ตรวจ bottom มี audio stream
18. ตรวจ top audio ไม่ถูกใช้
19. ถ้า top/bottom duration ต่างมาก ให้หยุดวิเคราะห์ sync ก่อน
20. บันทึก raw metadata สำคัญไว้ใน report หรือ notes

## Phase 4 — True Start / End

21. ใช้ bottom audio เป็นหลักในการหา start
22. ตัด cough, throat clear, false start, pause/reset ก่อนเริ่มจริง
23. true start คือจุดที่เริ่มพูดจริงและพูดต่อเนื่องประมาณ 30s+
24. ถ้าพูดสั้นแล้วเงียบ ยังไม่ถือเป็น true start
25. หา end ที่เนื้อหาจบจริงหรือเข้าสู่ trailing silence
26. บันทึก trimStart, trimEnd และเหตุผล

## Phase 5 — Parallel Trim

27. trim top ด้วย trimStart/trimEnd
28. trim bottom ด้วย trimStart/trimEnd เดียวกัน
29. ห้าม trim เฉพาะ top หรือ bottom อย่างเดียว
30. re-encode top เป็น 30fps / GOP 30 / faststart
31. re-encode bottom เป็น 30fps / GOP 30 / faststart
32. ตรวจ duration หลัง trim ของ top/bottom
33. ถ้า duration หลุด sync ให้แก้ก่อนทำขั้นถัดไป

## Phase 6 — Dead Air

34. ใช้ bottom audio ตรวจ silence
35. ใช้ค่าจาก `CONFIG.md`: silence > 0.5s และ threshold default -35dB
36. เลือกเฉพาะ dead air ที่อยู่ในเนื้อหาจริง
37. ตรวจว่า silence ที่จะตัดไม่กินคำพูดหรือ key term
38. ใช้ cut list เดียวกันกับ top และ bottom
39. สร้าง `top_deadair_cut.mp4` และ `bottom_deadair_cut.mp4`
40. ตรวจว่าไม่เหลือ silence ยาวเกิน policy
41. บันทึก total dead air removed

## Phase 7 — Audio Polish

42. ใช้ bottom clean เป็น source
43. apply highpass 80Hz
44. apply noise reduction แบบไม่ทำให้เสียงเป็นโลหะ
45. apply compressor
46. apply loudness normalization target -16 LUFS
47. apply limiter true peak ไม่เกิน -1.5 dBTP
48. สร้าง `bottom_audio_polished.mp4`
49. ตรวจ loudness report และ spot check เสียงพูด

## Phase 8 — Transcript And Key Terms

50. ถอดเสียงจาก bottom polished
51. ใช้ Whisper large-v3 ภาษาไทยเมื่อพร้อม
52. เก็บ raw transcript
53. สร้าง cleaned transcript
54. ตัด filler เช่น อืม, อะ, อ่ะ, เอ่อ
55. แก้คำทับศัพท์ เช่น พร้อม -> prompt เมื่อบริบทถูกต้อง
56. โหลด Editable Key Terms จาก `CONFIG.md`
57. เพิ่ม key terms เฉพาะคลิปถ้าจำเป็น
58. mark key terms ใน transcript
59. ห้ามลบ key term ระหว่าง clean/cut

## Phase 9 — Context Index

60. แบ่ง transcript เป็น meaning segments
61. sample screen ทุกประมาณ 5s
62. sample screen รอบ likely cut points และ B-roll points
63. สร้าง Full context index
64. แต่ละ segment ต้องมี speech, topic, intent, screenContext
65. ใส่ importanceScore, redundancyScore, fillerScore, cutRisk
66. ใส่ captionKeywords, brollKeyword, brollQuery
67. ใส่ keepReason/dropReason และ softCutPlan
68. ใช้ context index เป็น source กลาง ห้ามตัดแบบหารเวลาเท่า ๆ กัน

## Phase 10 — Context Cut And Soft Cut

69. เลือก keep segments จากสาระหลัก
70. เลือก drop segments จาก filler, repetition, waiting bridge
71. เก็บ hook, core explanation, key terms และ CTA ที่จำเป็น
72. ตรวจว่า key terms สำคัญยังอยู่ใน keep segments
73. หลีกเลี่ยงตัดกลางคำ กลางวลี หรือกลาง key term
74. ใช้ soft cut ทุก content cut
75. default crossfade คือ video/audio 0.12s
76. ปรับ crossfade เป็น 0.08-0.18s ตามจังหวะเสียง
77. render softcut top และ softcut bottom
78. ตรวจ duration ของ softcut media

## Phase 11 — B-roll

79. กำหนดจำนวน B-roll ตามโจทย์
80. เลือก slot จาก context ไม่ใช่คำเดี่ยว
81. ใช้ speech ก่อนและหลัง slot เพื่อเลือก broad keyword
82. ให้ B-roll ช่วยปิด jump cut ถ้าภาพ/เสียงโดด
83. ตรวจ stock index ก่อน
84. ถ้าต้องการคุณภาพดีที่สุด ให้โหลด Pexels candidate ใหม่อย่างน้อย 3 ตัวต่อ slot
85. fallback เป็น OpenRouter `google/veo-3.1-lite`
86. premium fallback เป็น `kwaivgi/kling-v3.0-std`
87. ทำ candidate contact sheet
88. reject text, logo, watermark, other brand, distracting graphic
89. re-encode selected B-roll เป็น 1920x1080 / 30fps / GOP 30 / faststart / no audio
90. สร้าง B-roll manifest พร้อม downloaded/generated/reused/optimized/rejected counts

## Phase 12 — Captions And Composition

91. สร้าง caption cues จาก cleaned transcript
92. จำกัด cue ประมาณ 20 ตัวอักษร และห้ามตัดคำไทยครึ่งคำ
93. ใช้ Bizdrive caption style และตรวจ gold highlight baseline/spacing
94. วาง background, top frame, bottom circle, B-roll และ captions ตาม `CONFIG.md`
95. ให้ B-roll replace เฉพาะ top frame และไม่ทับ bottom/caption
96. อัปเดต duration ทุกจุดใน composition

## Phase 13 — QA, Render, Report

97. รัน `npm run check` และต้องไม่มี lint/console/layout error
98. render MP4 แล้วตรวจ metadata, B-roll contact sheet, soft cut contact sheet, audio, captions และ key terms
99. สร้าง final report, อัปเดต changelog ถ้ามี rule change, และเก็บ artifacts ทั้งหมด
