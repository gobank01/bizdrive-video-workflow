# Motion Zoom And BGM Loop

ใช้สำหรับเพิ่มความน่าสนใจให้คลิป โดยต้องไม่ทำให้สาระ เสียงพูด หรือ caption เสีย

## Zoom Motion

หลักคิด:

```text
zoom คือ emphasis ไม่ใช่ decoration
ใช้เพื่อเน้นประโยคสำคัญ, key term, B-roll, screen action, หรือช่วยปิด jump cut
ต้อง subtle และ deterministic
```

ตำแหน่งที่ควรใช้:

```text
1. top screen ตอนพูด key term หรือเห็น action สำคัญ
2. B-roll insert เพื่อให้ stock footage มีชีวิตขึ้น
3. ช่วงก่อน/หลัง soft cut เพื่อช่วยให้ cut เนียนขึ้น
4. caption highlight สำคัญ เช่น AI, B-roll, prompt, ตัวเลข
```

ตำแหน่งที่ควรเลี่ยง:

```text
1. bottom face video เว้นแต่ผู้ใช้ขอ เพราะอาจทำให้หน้าคนกระตุก/เวียนหัว
2. ช่วง caption ยาวหรือข้อมูลแน่น
3. zoom แรงพร้อมกันหลาย layer
4. zoom ที่ทำให้ border/layout ขยับ
```

ค่า default:

```text
subtleZoom: scale 1.00 -> 1.035
maxZoom: 1.06
punchZoom: scale 1.00 -> 1.045 -> 1.00
slowZoomDuration: 2.0s - 3.0s
punchDuration: 0.45s - 0.80s
ease: power2.out / sine.inOut
applyTo: inner media layer, not frame wrapper
```

QA:

```text
ไม่ทำให้กรอบ top/bottom ขยับ
ไม่ทำให้ caption อ่านยาก
ไม่ zoom เกินจน crop สิ่งสำคัญออก
ไม่ใช้ motion ถี่เกิน 1 ครั้งทุก 2-3 วินาที
```

## BGM Loop

หลักคิด:

```text
BGM ต้องช่วยให้คลิปดูมีพลังขึ้น แต่เสียงพูดยังเป็นพระเอก
bottom audio ยังคือ master
BGM เป็น background mix เท่านั้น
```

กฎเลือกเพลง:

```text
1. ใช้เพลงที่มีสิทธิ์ใช้งาน หรือ royalty-free เท่านั้น
2. ไม่มี vocal ชัด ๆ
3. ไม่มี logo/audio tag/watermark
4. loop ได้เนียน
5. mood เข้ากับ Bizdrive: modern, clean, tech, business, optimistic
```

ค่า default:

```text
bgmEnabled: optional
bgmLoop: true
bgmFadeIn: 0.5s
bgmFadeOut: 1.0s
speechPriority: true
bgmTargetUnderSpeech: very low
suggestedBgmGain: -24dB to -18dB depending on source
duckingDuringSpeech: -6dB to -12dB if BGM distracts
finalAudio: bottom polished voice + BGM mixed into final output
```

QA:

```text
เสียงพูดต้องชัดกว่า BGM เสมอ
BGM ห้ามกลบ consonant/คำท้ายประโยค
BGM loop ต้องไม่สะดุดที่รอยต่อ
BGM ต้อง fade out ตอนจบ
ถ้าเสียงพูดต่อเนื่องทั้งคลิป ให้ใช้ BGM เบามากแทนการ duck หนัก ๆ
```

