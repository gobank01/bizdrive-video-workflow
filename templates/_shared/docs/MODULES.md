# Bizdrive Modular Workflow

สถานะล่าสุด: v72 - แยก workflow เป็น module ย่อยเพื่อทำงานต่อได้โดยไม่พึ่ง context ใน chat

เป้าหมายของไฟล์นี้คือทำให้สั่งงานเป็นชิ้นได้ เช่น "ช่วยถอดเสียงและทำ timestamp", "หา B-roll", หรือ "ทำ final mux/QA" โดยทุก module ต้องอ่าน/เขียน artifact ชัดเจน

## Module 1 — Transcript

งาน:

```text
ถอดเสียง bottom audio ด้วย Whisper large-v3
สร้าง word/segment timestamp
clean filler เช่น อืม อะ อ่ะ เอ่อ
รักษา key terms ที่แก้ได้จาก CONFIG.md
```

Output:

```text
assets/<job>/transcript-raw.json
assets/<job>/transcript-clean.json
reports/<job>/transcript-qa.json
```

## Module 2 — Sync Inspect

งาน:

```text
ตรวจ top/bottom metadata ด้วย ffprobe
ตรวจ duration, fps, frame count, stream start_time
รายงานว่า bottom audio เป็น master และ top/bottom sync กันหรือไม่
```

Output:

```text
reports/<job>/sync-inspect.json
reports/<job>/sync-inspect.md
```

## Module 3 — Context Index

งาน:

```text
วิเคราะห์ transcript เป็น meaning segments
sample screen ตามช่วงสำคัญ
ใส่ keep/drop reason, importance, redundancy, filler, cut risk
เลือก B-roll intent จากบริบทก่อน/หลัง ไม่ใช่คำเดี่ยว
```

Output:

```text
assets/context/<job>-context-index.json
```

## Module 4 — EDL Build

งาน:

```text
สร้าง frame-snapped edit decision list จาก bottom master timeline
กำหนด kept segments, dropped segments, content cut points
รักษา key terms และไม่ตัดกลางคำสำคัญ
```

Output:

```text
assets/context/<job>-edl.json
reports/<job>/edl-summary.md
```

## Module 5 — Editorial Master

งาน:

```text
ใช้ EDL เดียวกันตัด top visual, bottom visual และ speech audio
สร้าง proof clip สำหรับดูปากกับเสียงก่อนเข้า layout
ตรวจ duration/frame/sample lock
```

Output:

```text
assets/<job>/top_edit_master.mp4
assets/<job>/bottom_visual_master.mp4
assets/<job>/speech_audio_master.wav
assets/<job>/bottom_editorial_master.mp4
reports/<job>/editorial-master-qa.json
```

Gate:

```text
ถ้า module นี้ไม่ผ่าน ห้ามไป layout/render
```

## Module 6 — B-roll Source

งาน:

```text
หา B-roll จาก context intent
พยายามโหลดใหม่ก่อนเพื่อเพิ่ม stock
ถ้า API ไม่มีหรือ candidate ไม่ดี จึงใช้ stock ที่ QA แล้ว
reject ทันทีถ้ามี text/logo/watermark/brand/graphic รบกวน
```

Output:

```text
assets/broll/optimized/<job>/manifest.json
assets/broll/index.json
reports/<job>/broll-qa.md
```

## Module 7 — Caption Build

งาน:

```text
สร้าง caption จาก transcript ที่ map กับ edited timeline แล้ว
ไม่เกินประมาณ 20 ตัวอักษร
ไม่ตัดคำไทยครึ่งคำ
highlight สีทองต้อง baseline เท่าข้อความปกติและ spacing ถูก
```

Output:

```text
assets/<job>/captions.json
reports/<job>/caption-qa.json
```

## Module 8 — Layout Render

งาน:

```text
ใช้ top_edit_master และ bottom_visual_master เป็น source
วาง background, top frame, bottom circle, captions, B-roll, motion
render visual-only เพื่อไม่ให้ layout stage แตะเสียงพูด
```

Output:

```text
../stacked-output-<version>-<job>-visual.mp4
reports/<job>/layout-render-qa.json
```

## Module 9 — Final Mux

งาน:

```text
mux speech_audio_master.wav กลับเข้า visual render
mix BGM 5% หลัง mux แล้วเท่านั้น
ตรวจ loudness, true peak, silence, stream start_time
```

Output:

```text
../stacked-output-<version>-<job>-final.mp4
../stacked-output-<version>-<job>-final-bgm.mp4
reports/<job>/bgm-qa.json
```

## Module 10 — Final QA

งาน:

```text
สร้าง timestamped QA sheet ทุก 1 วินาที
สร้าง cut contact sheet รอบ content cuts
สร้าง B-roll contact sheet
รัน npm run check, check:transition, check:motion, check:keyterms
สร้าง frame report และ final report
```

Output:

```text
render-checks/<job>-timestamps/*.jpg
render-checks/<job>-cuts/*.jpg
render-checks/<job>-broll/*.jpg
reports/frame-report-<job>.json
reports/final-report-<job>.json
reports/final-report-<job>.md
```

## Command Direction

อนาคตควรมี wrapper command ตาม module:

```text
npm run bizdrive:transcript
npm run bizdrive:sync
npm run bizdrive:context
npm run bizdrive:edl
npm run bizdrive:editorial
npm run bizdrive:broll
npm run bizdrive:caption
npm run bizdrive:layout
npm run bizdrive:mux
npm run bizdrive:qa
npm run bizdrive:render
```

หลักสำคัญ: `bizdrive:render` ต้องเรียก module ตามลำดับเท่านั้น และต้องหยุดทันทีเมื่อ gate สำคัญ fail โดยเฉพาะ sync, editorial master, lip sync, B-roll QA, caption timing และ final stream start_time
