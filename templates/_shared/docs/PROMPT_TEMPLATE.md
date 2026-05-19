# Prompt Template

ใช้ prompt นี้เพื่อเริ่มงานใน session ใหม่

```text
ใช้ bizdrive-video workflow ในโปรเจกต์นี้

อ่านไฟล์เหล่านี้ก่อน:
- WORKFLOW.md
- STEPS.md
- CONFIG.md
- QA.md
- AGENTS.md

มีไฟล์ดิบ:
- bg png
- top/screen video
- bottom/face+audio video

ต้องการ output MP4 แนวตั้ง 1080x1920:
- bg เป็น background layer ล่างสุด
- top เป็นวิดีโอหน้าจอด้านบนและต้อง mute
- bottom เป็นวิดีโอวงกลมด้านล่างและเป็นเสียงหลัก
- trim/cut/dead-air ต้องทำคู่ขนาน top+bottom เสมอ
- ทำ audio polish ก่อน transcribe/render
- ทำ caption ไทยตาม Bizdrive caption style
- ทำ context index ก่อนตัดสั้น
- preserve key terms จาก CONFIG.md
- ใส่ B-roll แทน top frame เท่านั้น
- ตรวจ B-roll ไม่มี text/logo/watermark/brand/graphic
- render full MP4
- ทำ final report ตาม REPORT_TEMPLATE.md

หลังจบงานให้สรุป:
- output path
- version
- duration/metadata
- npm run check result
- B-roll report
- QA artifacts
- files updated
```
