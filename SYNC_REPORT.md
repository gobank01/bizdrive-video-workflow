# Sync Report

ใช้ไฟล์นี้เป็น template และ rule สำหรับวิเคราะห์ top/bottom sync ก่อน trim หรือ context cut

## Principle

```text
bottom audio คือ master timeline
top คือ visual screen layer
top ต้อง mute
ถ้า top/bottom duration, start offset, หรือ drift ต่างกัน ต้องแจ้งผู้ใช้ก่อนตัดสินใจ align/cut
```

## Required Checks

```text
top source:
bottom source:
top duration:
bottom duration:
duration delta:
top fps:
bottom fps:
bottom audio stream:
top audio policy: ignored/muted
```

## Sync Status

```text
status: pass | tiny_mismatch | offset_detected | drift_detected | fail
bottom is master: true
user notified: yes | no | not_needed
```

## Offset Analysis

ใช้เมื่อต้นคลิปเริ่มไม่พร้อมกัน

```text
sync point type: speech_to_screen_action | click | visual_event | manual
bottom time:
top time:
offset seconds:
decision:
```

ตัวอย่าง:

```text
bottom พูด "กดตรงนี้" ที่ 10.00s
top เห็นเมาส์กดจริงที่ 11.20s
top ช้ากว่า bottom 1.20s
decision: align top -1.20s relative to bottom
```

## Drift Analysis

ใช้เมื่อช่วงต้น sync แต่ช่วงท้ายเริ่มหลุด

```text
sync point A bottom/top:
sync point B bottom/top:
drift seconds:
drift per minute:
decision: split into sync segments | reject source | ask user
```

## Decision Rules

```text
1. ถ้า mismatch เป็นแค่ frame/container rounding ให้บันทึกเป็น tiny_mismatch และทำต่อได้
2. ถ้า start offset ชัด ให้ align top ให้ตรง bottom audio ก่อน trim
3. ถ้ามี drift ระหว่างคลิป ให้แบ่งเป็นหลาย sync segment หรือแจ้งผู้ใช้ว่าต้องเลือก source ใหม่
4. ห้าม time-stretch โดยไม่จำเป็น
5. ห้ามตัดตาม top หากขัดกับ bottom audio
6. ต้องบันทึก sync decision ลง final report
```

