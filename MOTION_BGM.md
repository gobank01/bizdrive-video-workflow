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
1. ใช้เพลงที่มีสิทธิ์ใช้งาน, royalty-free, หรือ generated-with-usage-rights เท่านั้น
2. ไม่มี vocal ชัด ๆ
3. ไม่มี logo/audio tag/watermark
4. loop ได้เนียน
5. mood เข้ากับ Bizdrive: modern, clean, tech, business, optimistic
6. ห้ามสรุปว่า copyright-free ถ้าไม่มี source/license ยืนยัน
```

ค่า default:

```text
bgmEnabled: optional
bgmLoop: true
bgmFadeIn: 0.5s
bgmFadeOut: 1.0s
speechPriority: true
bgmDefaultLevel: 5%
bgmTargetUnderSpeech: very low, ambience only
suggestedBgmGain: -26.02dB default, equivalent to 5% linear amplitude
duckingDuringSpeech: -6dB to -12dB if BGM distracts
finalAudio: bottom polished voice + BGM mixed into final output
```

QA:

```text
เสียงพูดต้องชัดกว่า BGM เสมอ
BGM default ต้องเริ่มที่ 5% เว้นแต่ผู้ใช้อนุมัติให้ดังขึ้น
BGM ห้ามกลบ consonant/คำท้ายประโยค
BGM loop ต้องไม่สะดุดที่รอยต่อ
BGM ต้อง fade out ตอนจบ
ถ้าเสียงพูดต่อเนื่องทั้งคลิป ให้ใช้ BGM เบามากแทนการ duck หนัก ๆ
```

## BGM Source Policy v48

คำตอบมาตรฐานเวลาผู้ใช้ถามว่า "ต้องหาเพลงเองไหม":

```text
ระบบสามารถช่วยเลือก/เตรียม BGM ได้เมื่อมีขั้นตอน source BGM แล้ว
แต่ทุกเพลงต้องมีสิทธิ์ใช้งานชัดเจนก่อน mix จริง
ถ้าไม่มี license/source ยืนยัน ให้ถือว่าใช้ไม่ได้
current mix tool รับ BGM file ที่เตรียมไว้แล้ว และจะไม่รับประกันลิขสิทธิ์แทน source
```

แหล่งที่ใช้ได้:

```text
1. user-provided music พร้อม license/usage rights
2. royalty-free library ที่มี terms ใช้งาน commercial/social ได้
3. generated music ที่ provider ให้สิทธิ์ใช้งานชัดเจน
4. internal stock ที่เคยตรวจ license และบันทึก source ไว้แล้ว
```

ห้ามใช้:

```text
1. เพลงดัง/เพลง commercial ที่ไม่มีสิทธิ์
2. เพลงจากคลิปอื่นโดยไม่มี license
3. เพลงที่มี audio tag, watermark, หรือเสียงพูด
4. เพลงที่ source/license ไม่ชัดเจน
```

## BGM Stock Library v49

ก่อน generate เพลงใหม่ ให้เลือกจาก stock ก่อน:

```text
tracked index: bgm-library/mixkit-stock-v50.json
runtime index: assets/bgm/index.json
runtime media: assets/bgm/stock/mixkit/*.mp3
count: 15 Mixkit tracks
default fallback: mixkit-480 Curiosity
tech fallback: mixkit-1167 Close Up
calm fallback: mixkit-441 Meditation
check command: npm run check:bgm
```

วิธีเลือก:

```text
1. อ่านบริบทเสียงพูดและ clip style
2. เทียบกับ `bestFor` ใน index
3. เลือก energy ต่ำที่สุดที่ยังทำให้คลิปไม่นิ่ง
4. mix ที่ 5%
5. spot-listen ว่าเสียงพูดยังชัด
6. ถ้าไม่เจอ track ที่เหมาะ ค่อยใช้ OpenRouter/Lyria generate แล้วเพิ่มเข้า index
7. ถ้าวิเคราะห์แล้วยังไม่ชัด ให้ใช้ `mixkit-480 Curiosity` ที่ 5%
```

## BGM Mix Implementation v48

คำสั่ง:

```bash
npm run mix:bgm -- \
  --voice assets/bottom_audio_polished.mp4 \
  --bgm assets/bgm/track.mp3 \
  --output assets/bottom_audio_polished_bgm.mp4 \
  --report reports/bgm-mix-v48.json \
  --gain-percent 5 \
  --fade-in 0.5 \
  --fade-out 1.0
```

ถ้า BGM ยังแย่งเสียงพูด ให้เปิด ducking:

```bash
npm run mix:bgm -- \
  --voice assets/bottom_audio_polished.mp4 \
  --bgm assets/bgm/track.mp3 \
  --output assets/bottom_audio_polished_bgm.mp4 \
  --duck true \
  --gain-percent 5
```

ผลลัพธ์:

```text
output ยังเก็บ video stream จาก bottom voice source
audio ถูก mix เป็น voice + BGM
BGM loop ด้วย -stream_loop -1
BGM fade in/out ตาม duration ของ voice source
amix ใช้ normalize=0 เพื่อไม่ลดเสียงพูดหลัก
final limiter default 0.82 และ `level=false` เพื่อคุม peak โดยไม่เร่งเสียงขึ้น
report JSON บันทึก command และค่า mix
```

หลัง mix:

```text
1. ใช้ output เป็น bottom video/audio ใน composition
2. ตรวจ loudness อีกครั้ง
3. ฟัง key phrases และท้ายประโยคว่า BGM ไม่กลบ
4. ตรวจ loop/fade-out
5. หลัง render final MP4 แล้ว ต้อง test BGM กับ final MP4 จริงอีกครั้ง
6. เทียบ original final MP4 กับ BGM final MP4 ด้วย loudness และ preview 20s
```
