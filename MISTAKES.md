# Bizdrive Mistakes And Prevention Log

ไฟล์นี้บันทึกความผิดพลาดจริงที่เคยเกิดขึ้น เพื่อบังคับไม่ให้ workflow ทำซ้ำ

## v67 Locked Lessons

### 1. v65 เปิดคลิปด้วยเสียงที่ไม่ใช่เสียงพูดจริง

What happened:

```text
คลิป v65 เริ่มจากเสียงสั้น/false start แล้วตามด้วย silence/reset ก่อน sustained speech
Whisper จับคำต้นได้ แต่จุดนั้นไม่ใช่ true start ที่ผู้ชมควรเห็น
ผลลัพธ์คือช่วงต้นรู้สึกเป็น noise หรือไม่ใช่เสียงพูดจริง
```

Root cause:

```text
workflow เชื่อ timestamp แรกของ transcript/เสียงมากเกินไป
ไม่ได้แยก "first detectable sound" ออกจาก "first sustained speech"
ไม่ได้บังคับตรวจ opening silence/reset หลังคำแรก
```

Never again:

```text
true start ต้องเป็น sustained speech เท่านั้น
ถ้ามีเสียง/คำสั้นแล้วเงียบหรือ reset ก่อนพูดยาว ต้องตัดออกเสมอ
ต้องใช้ bottom audio ตรวจ false start ก่อน transcript/context/caption
ต้องบันทึก trim reason ว่าเปิดคลิปเริ่มด้วย sustained speech แล้ว
```

Required proof:

```text
silencedetect หรือ equivalent audio analysis ช่วง 0-8s
context/trim report มี falseStartChecked=true หรือเหตุผลว่าไม่มี false start
final QA ต้องรายงาน opening silence/false-start status
```

### 2. v65 noise reduction ไม่ดี เพราะใช้ไฟล์ polished เดิมโดยไม่ verify ใหม่

What happened:

```text
v65 ใช้ assets/video2/bottom_audio_polished.mp4 เป็น source
ไฟล์นั้นเป็น audio ที่เคยผ่าน polish มาแล้ว แต่ยังมี noise/opening issue และ sample rate 96k
เมื่อนำไปตัด/render ต่อ ปัญหา noise ยังติดมาที่ output
```

Root cause:

```text
workflow ถือว่าไฟล์ชื่อ polished สะอาดแล้ว
ไม่ได้พิสูจน์ว่า polished source ดีกว่า raw bottom
audio QA ดู loudness/metadata มากกว่าคุณภาพช่วงต้นและ speech clarity
```

Never again:

```text
ถ้าผู้ใช้ report noise หรือ sync issue ให้กลับไปเริ่มจาก raw bottom audio ก่อน
ห้าม reuse polished source โดยไม่วัด opening noise, silence/reset, sample rate, stream start และ voice clarity
audio polish ต้องใช้ speech-first chain: highpass/lowpass, denoise, noise gate, compressor, loudnorm, limiter
```

Required proof:

```text
ffprobe source audio stream
silencedetect ช่วงต้นก่อน/หลัง polish
spot-check หรือ report ว่า denoise ไม่ทำให้เสียงบาง/robotic
```

### 3. v65 ปากกับเสียงยังไม่ตรง เพราะเช็คแค่ duration/frame ไม่พอ

What happened:

```text
top/bottom intermediate มี frame count เท่ากัน แต่ final MP4 ยังรู้สึกปากกับเสียงไม่ตรง
ffprobe หลัง render พบ video stream start_time 0.021s แต่ audio start_time 0.000s
แปลว่าเสียงอาจนำภาพประมาณ 21ms หรือเกือบ 1 frame
```

Root cause:

```text
QA ตรวจ duration/frame count แต่ไม่ได้ตรวจ stream start_time หลัง final render
ไม่ได้มี gate สำหรับ lip-sync metadata และ visual/audio sync point
สรุป sync pass เร็วเกินไปจากหลักฐานที่ไม่ครบ
```

Never again:

```text
หลัง final render ต้องตรวจ stream start_time ของ video และ audio ทุกครั้ง
ถ้า offset เกินระดับที่รู้สึกได้หรือผู้ใช้ report ต้อง log และแก้ก่อนส่ง
sync compensation ทำได้เฉพาะเมื่อมีค่าที่วัดได้และบันทึกใน context/final report
ห้ามพูดว่า sync pass จาก frame count อย่างเดียว
```

Required proof:

```text
ffprobe final stream start_time/duration/nb_frames
sync status ต้องระบุ frame count + stream start_time + compensation ถ้ามี
ถ้าแก้ offset ต้องบันทึก ms value และ reason
```

### 4. v65 caption timing เสี่ยงเพราะยึด timeline เดิมหลังตัดต้นเพิ่ม

What happened:

```text
เมื่อ v66 ตัด false start 0-2.3s ออก ต้อง shift caption cues ใหม่
ถ้าไม่ shift captions จะไม่ตรงกับ bottom speech
```

Root cause:

```text
caption timing อาจถูกมองเป็น layer แยก ทั้งที่ต้อง map กับ edited bottom-master timeline
```

Never again:

```text
หลัง trim/dead-air/context cut ทุกครั้ง ต้อง regenerate หรือ remap captions to edited timeline
ห้ามใช้ raw transcript timestamps ตรงๆ
```

Required proof:

```text
caption cue source ระบุว่า mapped after cuts
visual contact sheet หรือ inspect pass
spot check caption timing around first 10s and around each cut/B-roll point
```

## Hard Gates

ก่อนส่ง final video ทุกครั้ง ต้องผ่าน gate เหล่านี้:

```text
1. Opening gate: true start is sustained speech, not first detectable sound
2. Audio source gate: raw vs polished source chosen with evidence
3. Noise gate: opening false start/noise checked before and after polish
4. Sync metadata gate: final video/audio stream start_time checked after render
5. Caption map gate: captions mapped to edited timeline after every cut
6. Report gate: final summary includes what failed before and how this run prevents it
```

ถ้า gate ใดไม่ผ่าน ห้ามเรียกงานว่าเสร็จ
