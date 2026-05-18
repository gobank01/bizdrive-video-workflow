# BGM Stock Library

สถานะล่าสุด: v49 - Mixkit royalty-free starter stock 15 tracks

## Goal

เก็บเพลง BGM ที่ใช้ซ้ำได้สำหรับคลิป Bizdrive โดยเลือกจาก stock ก่อน generate ใหม่ เพื่อคุมคุณภาพ เสียงพูด และ license ให้ตรวจสอบย้อนหลังได้

## Current Library

```text
tracked index: bgm-library/mixkit-stock-v49.json
runtime index: assets/bgm/index.json
runtime media: assets/bgm/stock/mixkit/*.mp3
provider: Mixkit
license page: https://mixkit.co/license/
source page: https://mixkit.co/free-stock-music/corporate/
count: 15 tracks
default mix level: 5%
```

ไฟล์ mp3 อยู่ใน `assets/` และถูก ignore จาก git เพื่อไม่ให้ repo หนัก แต่ index ถูก track ใน repo เพื่อใช้พัฒนาต่อและแจก workflow ได้

## Selection Rule

```text
1. อ่าน transcript/context ก่อน
2. เลือก style ของคลิป
3. หา track ที่ `bestFor` ตรงกับ style
4. เลือก energy ต่ำที่สุดที่ยังทำให้คลิปมีชีวิต
5. mix ที่ 5% default ด้วย `npm run mix:bgm -- --gain-percent 5`
6. spot-listen ช่วง hook, ช่วง caption หนา, และท้ายประโยค
7. ถ้า BGM กลบเสียงพูด ให้ลดลงหรือเปลี่ยนเพลง
8. ถ้า stock ไม่มี mood ที่ตรง ค่อยใช้ OpenRouter/Lyria generate แล้วเพิ่มเข้า index
```

## Clip Style Map

```text
tech_explainer:
  AI, prompt, workflow, coding, software, automation, dashboard explanation
  starter tracks: Close Up, Digital Clouds, New Bass 01, Deep Techno Ambience

finance_business:
  investment, dividend, sales, strategy, business planning, case study
  starter tracks: Curiosity, It's Love, Romantic 05, New Bass 01

tutorial_screen:
  screen recording, step-by-step teaching, calm explanation, dense captions
  starter tracks: Curiosity, Meditation, Nature Yoga, Nap Time

product_demo:
  tool walkthrough, app feature, before/after, implementation demo
  starter tracks: Close Up, Digital Clouds, Uplifting Bass, Autofahren

high_energy_recap:
  strong hook, result reveal, short promo, fast B-roll sections
  starter tracks: Pop Track 03, Uplifting Bass, Minimal Techno 01, Deep Urban

calm_learning:
  longer teaching, reflective explanation, low-distraction audio bed
  starter tracks: Meditation, Nature Yoga, Nap Time, Curiosity
```

## QA Gate

ก่อนใช้ BGM ใน final render:

```text
[ ] track exists locally
[ ] source/license recorded
[ ] no obvious vocal, audio tag, watermark, or distracting melody
[ ] mixed at 5% unless user approves otherwise
[ ] speech remains clearly louder than BGM
[ ] BGM loop/fade is smooth
[ ] final report lists track id, title, provider, source, license, and gain percent
```

## Source Caveat

`royalty-free` ไม่ได้แปลว่าไม่มีเงื่อนไขเสมอไป ต้องยึด license ปัจจุบันของ provider และบันทึก source/license ทุกครั้ง ห้ามแจกไฟล์เพลงแบบ standalone นอกเหนือจากการใช้ในคลิปหรือ workflow ที่ license อนุญาต
