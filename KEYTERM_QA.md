# Key Term QA

ใช้สำหรับตรวจว่าคำสำคัญของคลิปไม่ถูกตัดหายหลังทำ cleaned transcript หรือ context cut

## Source Of Truth

รายการคำหลักมาจาก `CONFIG.md` หัวข้อ `Editable Key Terms`

```text
B-roll
caption
prompt
Dead Air
audio polish
intro
outro
thumbnail
export
AI
```

## Rules

```text
1. key term ไม่ใช่ filler
2. ถ้า key term เป็นหัวข้อของช่วงนั้น ต้องได้ยินในเสียงพูดอย่างน้อย 1 ครั้ง
3. ถ้าจะตัดคำอธิบายรอบ ๆ ให้ตัดรอบคำ ไม่ตัด key term
4. ตรวจทั้ง raw transcript และ kept/context transcript
5. ถ้า key term หาย ให้รายงาน warning หรือ fail ตาม mode
```

## Recommended Modes

```text
warn: แจ้งเตือนแต่ไม่ fail
strict: fail ถ้า required key term ไม่พบ
```

## Command

```bash
npm run check:keyterms -- --transcript assets/transcript_test2.large-v3.json --context assets/context/test2-v35-full-context-index.json
```

เพิ่ม required terms เองได้:

```bash
npm run check:keyterms -- --context assets/context/test2-v35-full-context-index.json --required B-roll,prompt,caption
```

## Report Fields

```text
transcript path
context path
mode
terms checked
found in transcript
found in kept segments
missing required terms
status: pass | warn | fail
```

