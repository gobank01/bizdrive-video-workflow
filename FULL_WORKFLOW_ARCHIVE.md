# Workflow: Bizdrive Stacked Video

ใช้ไฟล์นี้เป็น brief สำหรับสั่งงานรอบหน้า เมื่ออยากทำวิดีโอแนวตั้งจาก 2 คลิปแนวนอน + PNG background ด้วย HyperFrames

สถานะล่าสุด: v37 VIDEO WORKFLOW - แยก key terms เป็น config block ที่แก้ไข/แจกต่อได้ง่าย

หมายเหตุ version: v37 ต่อจาก v36 และแยกรายการ key terms ออกจากกฎ preservation เพื่อให้ปรับใช้กับโปรเจกต์อื่นได้

อัปเดตล่าสุด v37: key terms ต้องอยู่ใน section `Editable Key Terms v37` เพื่อให้แก้คำหลักได้ง่ายก่อนนำ workflow ไปแจกต่อ

## เป้าหมาย

สร้าง MP4 แนวตั้ง `1080x1920` โดยมี layer ดังนี้:

1. `bg.png` เป็น background layer ล่างสุด เต็มจอ
2. `top.mp4` เป็นวิดีโอแนวนอนด้านบน
3. `bottom.mp4` เป็นวิดีโอวงกลมอยู่ด้านล่างของ `top.mp4`
4. ไม่มี mark สีแดง
5. `top.mp4` ต้อง mute
6. `bottom.mp4` เป็นเสียงหลักของงาน
7. Trim เวลาเดียวกันทั้ง `top.mp4` และ `bottom.mp4` เพื่อให้ภาพหน้าจอ + หน้าคน + เสียง sync กัน
8. ถ้าตัด dead air ต้องตัดแบบคู่ขนานเสมอ: ตัดช่วงเวลาเดียวกันออกจากทั้ง `top.mp4` และ `bottom.mp4`
9. หลังตัด dead air ให้ทำ audio polish กับเสียงจาก `bottom.mp4`: noise reduction + loudness normalization
10. ถอดเสียงจาก `bottom.mp4` แล้วทำ subtitle ใต้ `bottom.mp4`

## ผลลัพธ์ baseline ก่อนตัด dead air

ไฟล์ output:

```text
/Users/gobank01/Documents/Video V2/stacked-output.mp4
```

ค่าที่ตรวจแล้ว:

```text
size: 1080x1920
duration: ประมาณ 104.59s
audio: 1 track จาก bottom.mp4
file size: ประมาณ 47.3 MB
```

หมายเหตุ: ค่า `data-duration` ใน `index.html` ตอน final ใช้ `104.542` แต่ไฟล์ MP4 ที่ตรวจด้วย `ffprobe` อาจแสดง duration ประมาณ `104.59s` จากการปัดเศษ frame/audio container ซึ่งถือว่าปกติ

## Dead Air Cut ล่าสุด

หลัง trim start/end แล้ว งานนี้ตัด dead air เพิ่มแบบคู่ขนาน โดยใช้เสียงจาก `bottom.mp4` เป็นตัวหา silence และตัดเวลาเดียวกันจากทั้งสองคลิป

กฎหลัก: ตัดความเงียบที่นานกว่า `0.5s` ออก โดยใช้ threshold ประมาณ `-35dB` สำหรับตรวจ silence

สรุปปริมาณ dead air ที่ตัดออกจริง:

```text
ช่วงต้น: 0.5158545s
ช่วงกลาง: 0.506917s
รวม: 1.0227715s หรือประมาณ 1.02s
```

ช่วงที่ตัดออก:

```text
ช่วงต้นหลัง trim เดิม: 0.0171875s - 0.533042s
raw time: 24.0171875s - 24.533042s

ช่วงกลาง:
raw time: 118.393771s - 118.900688s
```

ช่วงที่เก็บไว้:

```text
24.533042s - 118.393771s
118.900688s - 128.542s
```

ไฟล์ clean ที่สร้างไว้:

```text
stacked-video/assets/top_deadair_cut.mp4
stacked-video/assets/bottom_deadair_cut.mp4
```

ผลตรวจไฟล์ clean:

```text
top_deadair_cut.mp4: video 103.500s, no audio
bottom_deadair_cut.mp4: video 103.500s, audio 103.508s
```

ไฟล์ clean ถูก re-encode ให้มี keyframe ทุก 1 วินาที เพื่อให้ HyperFrames seek frame ได้แม่น:

```bash
ffmpeg -i input.mp4 -c:v libx264 -r 30 -g 30 -keyint_min 30 -movflags +faststart output.mp4
```

ไฟล์ output ล่าสุดหลังตัด dead air:

```text
/Users/gobank01/Documents/Video V2/stacked-output-deadair-cut.mp4
```

ค่าที่ตรวจแล้ว:

```text
size: 1080x1920
duration: ประมาณ 103.52s
audio: 1 track จาก bottom_deadair_cut.mp4
file size: ประมาณ 37.0 MB
silence check: ไม่พบ silence ยาว 0.5s+ ด้วย threshold -35dB
```

เมื่อตัด dead air เป็นไฟล์ clean แล้ว ถ้ายังไม่ได้ทำ audio polish สามารถใช้ไฟล์ clean โดยตรงชั่วคราว:

```html
<video id="topVideo" src="assets/top_deadair_cut.mp4" data-duration="103.5" data-volume="0" muted />
<video id="bottomVideo" src="assets/bottom_deadair_cut.mp4" data-duration="103.5" data-has-audio="true" />
```

หลักสำคัญ: ห้ามตัด dead air จาก `bottom.mp4` อย่างเดียว ต้องตัด `top.mp4` ด้วยช่วงเวลาเดียวกันทุกครั้ง ไม่อย่างนั้นภาพหน้าจอจะไม่ตรงกับหน้าและเสียง

## Audio Polish

หลังตัด dead air แล้ว ให้ทำ audio polish กับไฟล์เสียงหลักเสมอ โดยใช้ `bottom_deadair_cut.mp4` เป็น input แล้วสร้างไฟล์ใหม่สำหรับ render:

```text
stacked-video/assets/bottom_audio_polished.mp4
```

เป้าหมายเสียง:

```text
noise reduction: ลด noise คงที่/เสียงพื้นหลังเบา ๆ
high-pass: ตัด rumble ต่ำกว่า 80Hz
compression: ทำให้เสียงพูดดังเสถียรขึ้น
loudness normalization: target -16 LUFS, true peak ไม่เกิน -1.5dB
limiter: กันเสียงแตก/peak เกิน
```

คำสั่งมาตรฐาน:

```bash
ffmpeg -y -i assets/bottom_deadair_cut.mp4 \
  -map 0:v:0 -map 0:a:0 \
  -c:v copy \
  -af "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-18dB:ratio=3:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95" \
  -c:a aac -b:a 192k \
  assets/bottom_audio_polished.mp4
```

ตรวจ loudness หลังทำเสร็จ:

```bash
ffmpeg -i assets/bottom_audio_polished.mp4 -af ebur128=peak=true -f null -
```

ค่าเป้าหมายที่ควรเห็น:

```text
Integrated loudness: ใกล้ -16 LUFS
True peak: ไม่เกิน -1.5 dBTP
เสียงพูดดังสม่ำเสมอ ไม่มีแตก ไม่มี noise reduction แรงจนเสียงเป็นโลหะ
```

ถ้า noise reduction แรงเกินไปจนเสียงพูดแปลก ให้ลดความแรงของ `afftdn` เช่น:

```text
afftdn=nf=-20
```

ถ้าเสียงยังเบา ให้คง `loudnorm=I=-16:TP=-1.5:LRA=11` เป็นหลัก อย่าเพิ่ม volume ตรง ๆ จน peak แตก

เมื่อมีไฟล์ audio polished แล้ว ให้ `index.html` ใช้ไฟล์นี้แทน `bottom_deadair_cut.mp4` สำหรับ bottom video/audio:

```html
<video id="topVideo" src="assets/top_deadair_cut.mp4" data-duration="103.5" data-volume="0" muted />
<video id="bottomVideo" src="assets/bottom_audio_polished.mp4" data-duration="103.5" data-has-audio="true" />
```

หมายเหตุ: ยังต้องใช้ `top_deadair_cut.mp4` ตัวเดิมสำหรับหน้าจอ และใช้ `bottom_audio_polished.mp4` สำหรับหน้า + เสียง เพราะไฟล์ polished ควรมี video stream เดิมพร้อม audio ที่ผ่านการปรับแล้ว

## B-roll Insert v23

ใช้ B-roll เป็น insert ทดแทนตำแหน่ง `topVideo` โดยวางทับ top frame เดิมเท่านั้น ไม่ทับหน้า speaker และไม่ทับ caption

กฎหลัก:

```text
จำนวนต่อคลิป: ค่าแนะนำ 5 B-roll, ขั้นต่ำ 3 B-roll
ความยาวต่อชิ้น: 3s สูงสุด
ตำแหน่งภาพ: ใช้ตำแหน่ง top เดิม 1080x607.5px
กรอบ: ใช้ class video-frame + top-frame เหมือน top, border 4px, radius 30px
เสียง: B-roll ต้อง mute / data-volume=0
layer: B-roll อยู่เหนือ topVideo แต่ใต้ subtitle
```

ตำแหน่ง v23 ที่เลือก:

```text
06.000s - 09.000s: AI stock analysis dashboard
18.750s - 21.750s: passive dividend income / long-term investing
34.000s - 37.000s: one prompt workflow / AI creates web app
68.000s - 71.000s: US stock investing / market screens
84.750s - 87.750s: S&P 500 / dividend investing
```

เหตุผลที่เลือก:

```text
06s: ตรงกับช่วง "พี่แบงค์ให้ AI"
18.75s: ตรงกับช่วง "มีเงินปันผล" / "แค่ลงทุนไว้"
34s: ตรงกับช่วง "แค่หนึ่ง prompt"
68s: ตรงกับช่วง "เอาไปลงทุน" / "ในหุ้นสหรัฐ"
84.75s: ตรงกับช่วง "S&P 500"
```

ไฟล์ B-roll:

```text
assets/broll/v23-broll-01.mp4
assets/broll/v23-broll-02.mp4
assets/broll/v23-broll-03.mp4
assets/broll/v23-broll-04.mp4
assets/broll/v23-broll-05.mp4
```

ถ้ายังไม่มี API key ให้ใช้ placeholder เพื่อทดสอบ layout ได้ แต่ final production ต้อง generate ใหม่ด้วย OpenRouter

สถานะทดสอบ API v23:

```text
OpenRouter API: generate สำเร็จครบ 5 B-roll
model ที่ใช้จริง: bytedance/seedance-2.0-fast
ไฟล์ output: assets/broll/v23-broll-01.mp4 ถึง assets/broll/v23-broll-05.mp4
ไฟล์แต่ละชิ้น: 1280x720, ประมาณ 5.04s, no audio
HyperFrames ใช้แค่ 3s แรกของแต่ละไฟล์
```

OpenRouter model order:

```text
primary: bytedance/seedance-2.0-fast
fallback 1: alibaba/wan-2.6
fallback 2: alibaba/wan-2.7
```

ตั้ง API key แล้ว generate:

```bash
export OPENROUTER_API_KEY="ใส่-key-ตรงนี้"
npm run generate:broll
```

request default:

```json
{
  "aspect_ratio": "16:9",
  "duration": 5,
  "resolution": "720p",
  "generate_audio": false
}
```

หมายเหตุ: OpenRouter generate 5s ได้ แต่ใน HyperFrames จำกัด `data-duration="3"` เพื่อใช้เฉพาะ 3 วินาทีแรก ถ้าต้องเลือกช่วงในไฟล์ B-roll เองให้ใช้ `data-media-start`

## Stock B-roll Library v24

เป้าหมาย:

```text
เนื้อหา Bizdrive มักใช้ภาพซ้ำกลุ่มเดิม เช่น AI, หุ้น, ปันผล, S&P 500, prompt, workflow
ดังนั้นต้องทำ stock B-roll library แล้ว index ตาม keyword
ทุกครั้งก่อน generate ใหม่ ให้ค้นใน index ก่อน
ถ้าเจอภาพที่ใช้ได้ ให้ reuse
ถ้าไม่เจอ ให้ generate ใหม่ แล้วบันทึกกลับเข้า index
```

ไฟล์หลัก:

```text
scripts/openrouter-broll-library.js
assets/broll/index.json
assets/broll/model-tests/
```

คำสั่งทดสอบ model:

```bash
export OPENROUTER_API_KEY="ใส่-key-ตรงนี้"
npm run generate:broll:test-models
```

request default สำหรับ stock B-roll:

```json
{
  "aspect_ratio": "16:9",
  "duration": 4,
  "resolution": "720p",
  "generate_audio": false
}
```

เหตุผลที่ generate 4s:

```text
Veo 3.1 Lite รองรับ 4-8s
Kling v3.0 Standard รองรับ 3-15s
ใช้ 4s เป็นค่ากลางที่ทั้งสองรุ่นรับได้ และตอน insert จริงเลือกใช้ไม่เกิน 3s
```

ราคาจาก OpenRouter ณ 2026-05-18:

```text
google/veo-3.1-lite: from $0.05/s
kwaivgi/kling-v3.0-std: from $0.126/s
```

ต้นทุนโดยประมาณ:

```text
1 B-roll 4s:
Veo 3.1 Lite = $0.20
Kling v3.0 Standard = $0.504

5 B-roll ต่อคลิป:
Veo 3.1 Lite = $1.00
Kling v3.0 Standard = $2.52
```

ข้อสรุปเบื้องต้นก่อนดูภาพจริง:

```text
ถูกกว่า: google/veo-3.1-lite
ใช้ production default: google/veo-3.1-lite
ใช้ fallback / special shot: kwaivgi/kling-v3.0-std
เหตุผล: Kling แพงกว่า แต่ควรเก็บไว้เทียบคุณภาพจริง โดยเฉพาะ shot ที่ต้องการ motion หรือ first/last-frame control
```

## Pexels Stock B-roll v25

ใช้ Pexels เป็น source แรกของ stock B-roll เพราะได้วิดีโอจริงทันที ไม่ต้องรอ text-to-video และต้นทุนต่อคลิปเป็น 0 ภายใต้โควตา API

กฎการเลือก:

```text
1. ค้น `assets/broll/index.json` ก่อนทุกครั้ง
2. ถ้า keyword เดิมมีไฟล์ที่ยังอยู่ ให้ reuse
3. ถ้าไม่มี ให้ค้น Pexels ด้วย keyword/query ที่กว้างพอ
4. เลือก video landscape, อย่างน้อย HD, duration >= 3s
5. download เก็บใน `assets/broll/stock/pexels/<keyword>/`
6. บันทึก metadata กลับเข้า index เช่น provider, query, path, Pexels video id, source URL, creator
7. ถ้า Pexels หาไม่ตรงจริง ๆ ค่อยใช้ OpenRouter generate
```

คำสั่ง:

```bash
export PEXELS_API_KEY="ใส่-key-ตรงนี้"
npm run search:broll:pexels
```

Pexels request default:

```json
{
  "orientation": "landscape",
  "size": "medium",
  "locale": "en-US",
  "per_page": 8
}
```

keyword ชุดแรก:

```text
stock_market -> stock market trading screen
investment_money -> investment money finance
business_dashboard -> business analytics dashboard
coding_workflow -> coding laptop workflow
wall_street -> wall street finance
```

ข้อสรุป provider:

```text
Primary: Pexels API
เหตุผล: ถูกสุด/เร็วสุด/ภาพจริง เหมาะกับ stock B-roll ซ้ำตาม keyword

Fallback: OpenRouter google/veo-3.1-lite
เหตุผล: ถูกกว่า Kling และเหมาะกับ shot เฉพาะที่ Pexels ไม่มี

Premium fallback: OpenRouter kwaivgi/kling-v3.0-std
เหตุผล: แพงกว่า แต่เก็บไว้เทียบคุณภาพหรือใช้เฉพาะ shot ที่ต้องการมาก
```

ข้อควรจำ:

```text
Pexels attribution ไม่บังคับ แต่ควรเก็บ creator/source URL ใน index เสมอเพื่อ audit ภายหลัง
ไม่ใช้ Pexels API เพื่อกวาดข้อมูลจำนวนมากหรือทำ dataset/ML training
```

ผลทดสอบ v25:

```text
Pexels API: download สำเร็จ 5 keyword
index: assets/broll/index.json
preview: stacked-video/render-checks/pexels-v25/contact-sheet.jpg
reuse test: รันซ้ำแล้ว reuse ทั้ง 5 ไฟล์ ไม่ download ซ้ำ
```

ไฟล์ที่ได้:

```text
assets/broll/stock/pexels/stock_market/stock-market-30289537-1920x1080.mp4
assets/broll/stock/pexels/investment_money/investment-money-3752538-1920x1080.mp4
assets/broll/stock/pexels/business_dashboard/business-dashboard-34128979-1920x1080.mp4
assets/broll/stock/pexels/coding_workflow/coding-workflow-36328529-1920x1080.mp4
assets/broll/stock/pexels/wall_street/wall-street-4319342-1920x1080.mp4
```

metadata ที่ตรวจแล้ว:

```text
ทุกไฟล์: 1920x1080 landscape
duration: 10.09s - 20.02s
ใช้ insert จริง: เลือกช่วงที่ดีที่สุดไม่เกิน 3s ด้วย data-media-start + data-duration
```

ผลทดสอบ v26:

```text
คำสั่ง: FORCE_BROLL=1 npm run search:broll:pexels
ผลลัพธ์: download variation ใหม่สำเร็จ 5 keyword
index: assets/broll/index.json อัปเดตเป็น version 26
จำนวนใน library: 10 ไฟล์ รวม 2 variation ต่อ keyword
reuse test: รันซ้ำแบบไม่ FORCE แล้ว reuse latest ทั้ง 5 keyword
preview: stacked-video/render-checks/pexels-v26/contact-sheet.jpg
```

ไฟล์ v26 ที่ได้:

```text
assets/broll/stock/pexels/stock_market/stock-market-8480232-1920x1080.mp4
assets/broll/stock/pexels/investment_money/investment-money-5849642-1920x1080.mp4
assets/broll/stock/pexels/business_dashboard/business-dashboard-34129037-1920x1080.mp4
assets/broll/stock/pexels/coding_workflow/coding-workflow-7989703-1920x1080.mp4
assets/broll/stock/pexels/wall_street/wall-street-5630360-1920x1080.mp4
```

metadata v26:

```text
ทุกไฟล์: 1920x1080 landscape
duration: 10.02s - 20.03s
size: ประมาณ 3.4 MB - 13.1 MB
```

QA note v26:

```text
Pexels เร็วและคุ้มมากสำหรับ stock B-roll แต่ต้องทำ visual QA ก่อนใช้จริง
โดยเฉพาะเช็ค no text / no logo / no distracting graphic / no other brand
ถ้าเจอ text/logo/graphic/brand อื่น ต้อง reject และเปลี่ยนใหม่เสมอ ห้ามใช้ใน final
ตัวอย่างรอบนี้ investment_money มี graphic/text ติดมา จึงต้องเลือก variation อื่นหรือใช้ OpenRouter เฉพาะ shot นี้
```

## Full Video With 10 B-roll v27

ใช้ stock B-roll จาก `assets/broll/index.json` ครบ 10 ไฟล์ วางทับตำแหน่ง `topVideo` ครั้งละ 3 วินาที

ตำแหน่ง v27:

```text
06.000s - 09.000s: business dashboard / AI data
18.750s - 21.750s: stock market
29.000s - 32.000s: business dashboard / AI calculation
34.000s - 37.000s: coding workflow / prompt
45.000s - 48.000s: investment money
58.000s - 61.000s: investment money variation
68.000s - 71.000s: Wall Street / US stocks
75.000s - 78.000s: coding workflow / AI helper
84.750s - 87.750s: stock market / S&P 500
95.600s - 98.600s: Wall Street / AI recommendation
```

กฎ v27:

```text
B-roll ทุกตัวใช้ top frame เดิม
B-roll ทุกตัว muted และ data-volume=0
B-roll ทุกตัวอยู่เหนือ topVideo แต่ใต้ subtitle
ใช้ data-media-start เพื่อเลือกช่วงกลางไฟล์ stock
```

ไฟล์ full test v27:

```text
/Users/gobank01/Documents/Video V2/stacked-output-v27-pexels-broll10-full-test.mp4
```

ผล test v27:

```text
duration: 103.521s
video: 1080x1920, 103.500s
audio: 1 track จาก bottom, 103.509s
file size: ประมาณ 55.8 MB
render time: ประมาณ 2m26s
check: 0 errors, no console errors, 0 layout issues
warning เดิม: timeline_track_too_dense จาก subtitle track 3
```

frame check v27:

```text
stacked-video/render-checks/v27-broll10/007.jpg
stacked-video/render-checks/v27-broll10/020.jpg
stacked-video/render-checks/v27-broll10/030.jpg
stacked-video/render-checks/v27-broll10/035.jpg
stacked-video/render-checks/v27-broll10/046.jpg
stacked-video/render-checks/v27-broll10/059.jpg
stacked-video/render-checks/v27-broll10/069.jpg
stacked-video/render-checks/v27-broll10/076.jpg
stacked-video/render-checks/v27-broll10/086.jpg
stacked-video/render-checks/v27-broll10/096.jpg
stacked-video/render-checks/v27-broll10/contact-sheet.jpg
```

QA note v27:

```text
Pexels source บางไฟล์มี sparse keyframes ทำให้ HyperFrames เตือนว่าอาจ seek/freeze ได้
รอบ test render ผ่านและ frame check แสดง B-roll ครบ 10 จุด
ก่อน production final ควร re-encode stock B-roll เป็น 30fps / GOP 30 / faststart เพื่อลดปัญหา seek
ตัวอย่างคำสั่ง:
ffmpeg -i input.mp4 -c:v libx264 -r 30 -g 30 -keyint_min 30 -movflags +faststart -an output.mp4

Pexels บาง variation อาจมี text/logo/graphic ติดมา ต้องตรวจ contact sheet ก่อนใช้ final
```

## Strict B-roll QA v29

กฎนี้ต้องทำทุกครั้งก่อนนำ B-roll เข้า render final:

```text
1. ทำ contact sheet หรือ preview frame ของ B-roll ทุกจุด
2. ตรวจด้วยตาอย่างน้อย 1 frame ต่อ B-roll และควรดูช่วงที่จะใช้จริง 1-3s
3. B-roll ต้องไม่มี text แปลก ๆ
4. B-roll ต้องไม่มี logo
5. B-roll ต้องไม่มี graphic ที่ทำให้เข้าใจผิดหรือแย่งซีน
6. B-roll ต้องไม่มี brand อื่น / watermark / UI ที่มีแบรนด์อื่น
7. ถ้าเจอข้อใดข้อหนึ่ง ให้เปลี่ยน B-roll ใหม่เสมอ
8. ห้ามใช้ไฟล์ที่ fail QA ใน final แม้ภาพจะสวย
```

ลำดับการแก้เมื่อ B-roll fail QA:

```text
1. หา variation อื่นใน `assets/broll/index.json` keyword เดียวกันก่อน
2. ถ้าไม่มี variation ที่ผ่าน ให้ค้น Pexels API ใหม่ด้วย keyword/query ที่ปรับให้กว้างขึ้น
3. ถ้า Pexels ยังไม่ได้ ให้ generate ด้วย OpenRouter `google/veo-3.1-lite`
4. ถ้ายังไม่ได้คุณภาพ ให้ลอง `kwaivgi/kling-v3.0-std`
5. เมื่อได้ไฟล์ใหม่แล้ว ต้องบันทึกเข้า index พร้อม note ว่าไฟล์เก่า fail เพราะอะไร
```

สถานะ QA ของไฟล์ใน index ควรใช้คำเหล่านี้:

```text
qaStatus: "pass" | "fail" | "needs_review"
qaReason: "text" | "logo" | "graphic" | "other_brand" | "watermark" | "poor_relevance"
```

## B-roll Reporting Rule v31

ทุกครั้งที่ทำงานเกี่ยวกับ B-roll ต้องสรุปท้ายงานเสมอ:

```text
โหลดใหม่จาก stock provider: กี่ไฟล์
generate ใหม่ด้วย AI video model: กี่ไฟล์
ใช้ source เดิม: กี่ไฟล์
สร้าง optimized/re-encoded derivative: กี่ไฟล์
แต่ละ slot ใช้ keyword อะไร
แต่ละ slot มาจาก provider/source path ไหน
QA pass/fail/reject เพราะอะไร
```

กฎ metadata:

```text
ทุก B-roll set ต้องมี manifest หรือ index entry ที่อ่านกลับได้
Pexels stock ใช้ `assets/broll/index.json`
optimized derivative ต้องมี `manifest.json` อยู่ข้างไฟล์
ถ้าใช้ไฟล์เก่าที่ไม่มี keyword เดิม ให้ใส่ keyword ใน manifest พร้อม `keywordConfidence`
```

manifest ล่าสุด:

```text
assets/broll/optimized/test2-v34/manifest.json
```

## Default Context Edit Decisions v35

สรุป decision ที่ใช้เป็น default ต่อจากนี้:

```text
target duration: ไม่ fix ตายตัว ผู้ใช้จะบอกเป้าหมายทุกครั้ง
cut aggressiveness: Medium
B-roll sourcing: พยายามโหลดใหม่ทุกครั้ง ถ้าต้องการคุณภาพ/ความตรงบริบทสูงกว่า stock เดิม
B-roll keyword: ใช้คำจากบริบทที่เข้าใจ ไม่ใช้คำเจาะจงแคบหรือคำเดี่ยวจาก transcript
screen analysis: B+C = sample ทุก ~5s + เพิ่ม frame รอบจุด cut/B-roll สำคัญ
soft cut: ใช้เสมอเมื่อมี content cut
B-roll cover jump: ใช้ B-roll ช่วยปิดช่วง jump cut เมื่อภาพ/เสียงอาจโดด
context index: Full
stock B-roll memory/index: ใช้ตามข้อเสนอ ให้เก็บ keyword/topic/intent/source/visual/QA/timesUsed/bestForTopics
default workflow: เอาข้อเสนอ v34 เข้าเป็นกติกาหลัก
```

หลักการตัด:

```text
1. ผู้ใช้บอกเป้าหมายความยาวหรือโจทย์ของคลิปทุกครั้ง เช่น "ประมาณ 60s", "สั้นลงแต่ครบ", "เอาไว้ลง Shorts"
2. ระบบไม่บังคับเวลาตายตัว ถ้าจบความที่ 58s หรือ 65s ดีกว่า 60s เป๊ะ ให้เลือกจบความก่อน
3. ใช้ระดับ Medium: ตัด filler, ความซ้ำ, bridge ที่ไม่เพิ่มสาระ, waiting section และคำอธิบายรอง
4. ห้ามตัดจนสาระหลักหาย ถ้าเป้าหมายสั้นเกินไป ให้รายงาน trade-off ก่อน final
5. ตัดจาก meaning-bearing segments ใน context index ไม่ตัดแบบหารเวลาเท่า ๆ กัน
```

Full context index ต้องมีอย่างน้อย:

```text
id
originalStart / originalEnd
newStart / newEnd
speech
topic
intent
importanceScore
redundancyScore
fillerScore
screenContext
captionKeywords
brollKeyword
brollQuery
keepReason หรือ dropReason
cutRisk
softCutPlan
brollCoverRecommended
```

Screen analysis default:

```text
ใช้ transcript/audio เป็น source หลักของความหมาย
sample top/screen ทุก ~5s เพื่อเข้าใจว่าหน้าจอกำลังโชว์อะไร
เพิ่ม frame รอบจุด cut และ B-roll ทั้งก่อน/หลังประมาณ 1-2s
ใช้ screenContext เพื่อช่วยเลือก B-roll, ตรวจว่า top frame สำคัญไหม, และตัดสินใจว่าต้องใช้ B-roll ปิด jump หรือไม่
```

B-roll default:

```text
พยายามโหลดใหม่ทุกครั้งเมื่อทำงาน final หรือเมื่อผู้ใช้ต้องการคุณภาพดีที่สุด
เลือก keyword จากบริบทแบบกว้างและเข้าใจ intent เช่น "AI processing workflow", "audio cleanup", "content creator editing"
หลีกเลี่ยง keyword แคบเกินไปที่ทำให้ได้ภาพไม่เป็นธรรมชาติ
ถ้า stock เดิมตรงและผ่าน QA สามารถใช้เป็น fallback ได้ แต่ต้องรายงานว่า reuse เท่าไร
ถ้า B-roll ช่วยปิด jump cut ได้ ให้ retime ให้คร่อมจุดตัด 0.5-1.0s ตามความเหมาะสม
ทุก B-roll ต้องไม่มี text/logo/watermark/brand อื่น/graphic รบกวน
```

Soft cut default:

```text
ใช้เสมอเมื่อมี content cut
default: video xfade + audio acrossfade 0.12s
ถ้าเสียงโดดมาก เพิ่มเป็น 0.15-0.18s
ถ้ารู้สึกย้วย ลดเป็น 0.08-0.10s
หลีกเลี่ยงตัดกลางคำหรือกลางวลี
ถ้าหลีกเลี่ยงไม่ได้ ให้ใช้ B-roll คร่อมจุดตัด
หลัง soft cut ต้อง re-encode top/bottom เป็น 30fps / GOP 30 / faststart ก่อน render
caption ต้องไม่ overlap ช่วง crossfade
```

Stock B-roll memory/index ควรเก็บ:

```text
keyword
topic
intent
source
provider
visualDescription
qaStatus
qaReason
timesUsed
lastUsedAt
bestForTopics
rejectReason
```

Decision summary:

```text
ระบบนี้จะเปลี่ยนจาก "ตัด dead air + ใส่ B-roll" เป็น "ตัดต่อเชิงบริบท"
context index คือแหล่งกลางสำหรับ cut plan, caption, B-roll, thumbnail, post caption และ QA
คุณภาพงานจะวัดจากการเล่าเรื่องครบ กระชับ เนียน และ B-roll ตรงบริบท ไม่ใช่แค่ความยาวสั้นลง
```

## Editable Key Terms v37

รายการนี้แก้ได้ตามโปรเจกต์ ก่อนเริ่ม context cut ให้ตรวจและปรับให้ตรงกับเนื้อหาของคลิปนั้น

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

วิธีแก้ตอนใช้กับโปรเจกต์อื่น:

```text
1. เพิ่มคำที่เป็นชื่อ feature, product, service, framework, model, หรือขั้นตอนสำคัญของคลิป
2. ลบคำที่ไม่เกี่ยวกับคลิปนั้นออกได้
3. เก็บตัวสะกดจริงที่ผู้พูดใช้ เช่น B-roll, b roll, บีโรล ถ้าพูดหลายแบบให้ใส่หลาย variant
4. ถ้ามีคำทับศัพท์สำคัญ ให้ใส่ทั้งรูปเสียงพูดและรูป caption ที่ต้องการ เช่น พร้อม -> prompt
5. ห้ามเอา filler word เช่น อืม, อะ, เอ่อ มาใส่ในรายการนี้
```

## Key Spoken Term Preservation v36

ข้อแก้จาก QA หลังดู v35 full test:

```text
คลิปใช้ได้แล้ว แต่ไม่อยากให้ตัดเสียงพูดคำว่า "B-roll" ออก
คำที่เป็นชื่อขั้นตอนหรือ key term ของ workflow ต้องพยายามเก็บไว้ในเสียงพูดจริง
```

กฎตัดต่อ:

```text
1. ก่อนตัดแบบ context cut ให้ mark key spoken terms ใน transcript ก่อนเสมอ
2. ใช้รายการคำจาก section `Editable Key Terms v37` เป็น source of truth
3. ถ้า key term เป็นหัวข้อของช่วงนั้น ให้เก็บประโยคหรือวลีที่พูดคำเต็มไว้ อย่างน้อย 1 ครั้ง
4. ห้ามตัดจนเหลือแต่ caption/ภาพประกอบ แต่เสียงพูดไม่มีคำสำคัญนั้น
5. ถ้าจำเป็นต้องตัดเพื่อความยาว ให้ตัดคำอธิบายรอบ ๆ แทน ไม่ตัดตัว key term
6. หลัง render ให้ QA ด้วยการฟังช่วงที่มี key term สำคัญ โดยเฉพาะช่วงที่พูดว่า "B-roll"
```

วิธีคิด:

```text
คำว่า B-roll ไม่ใช่ filler แต่เป็นชื่อ feature/ขั้นตอนของงาน
ถ้าตัดคำนี้ออก คนดูจะเห็นภาพ B-roll แต่เสียงเล่าไม่ครบ ทำให้จังหวะอธิบาย workflow ขาด
ในการตัดแบบ Medium ให้ตัดความซ้ำและช่วงรอได้ แต่ต้องรักษาชื่อขั้นตอนหลักของ workflow ให้ได้ยินครบ
```

## Full Context Test v35

โจทย์:

```text
ทดสอบ full ด้วยกติกา v35:
ไม่ fix duration ตายตัว แต่ใช้เป้าหมายประมาณ 60s
ใช้ Full context index ก่อนตัด
ใช้ soft cut ทุก content cut
โหลด B-roll ใหม่ทั้งหมดจาก Pexels ด้วย keyword จากบริบท
ให้ B-roll ปิดช่วง jump cut สำคัญ
```

ผล:

```text
original composition หลัง dead air: 84.5s
v35 output: 59.354s container
ลดลงประมาณ: 25.17s
soft cut: video xfade + audio acrossfade 0.12s ทุกจุดตัด
B-roll: 10 จุด, จุดละ 3s, replace top frame เท่านั้น
```

ไฟล์ใหม่:

```text
assets/context/test2-v35-full-context-index.json
assets/top_test2_context60_v35_softcut.mp4
assets/bottom_test2_context60_v35_audio_polished_softcut.mp4
assets/broll/stock/pexels/test2-v35-full/candidates-manifest.json
assets/broll/optimized/test2-v35/manifest.json
scripts/pexels-test2-v35-full-broll.js
scripts/build-v35-full-context-test.js
```

คำสั่ง:

```bash
PEXELS_API_KEY="ใส่-key-ตรงนี้" CANDIDATES_PER_SLOT=3 npm run search:broll:test2-v35-full
npm run build:context60:v35-full
npm run check
npx --yes hyperframes@0.6.16 render --output ../stacked-output-v35-test2-full-context-softcut-broll-full-test.mp4 --quality standard
```

ช่วงที่เก็บไว้:

```text
0.00-4.50s: hook ว่า AI กำลังตัดต่อ
10.38-21.48s: ฟุต 2 ตัว + ส่งให้ AI
24.18-28.14s: สั่ง AI ตัดต่อแบบง่าย
33.24-57.36s: รอประมวลผล, Dead Air, ปรับเสียง, layout, B-roll
63.22-67.46s: caption + overlay
72.42-84.46s: intro/outro, thumbnail, output จริง, CTA
```

ช่วงที่ตัดออก:

```text
4.50-10.38s: พูดซ้ำเรื่องคลิปง่ายและ AI ตัดต่อได้
21.48-24.18s: bridge ซ้ำเรื่อง workflow เสร็จ/งานนิ่ง
28.14-33.24s: AI ตอบรับงาน เป็นช่วงรอที่ไม่เพิ่มสาระ
57.36-63.22s: filler และคำไม่ชัด
67.46-72.42s: คำซ้ำเรื่องสี/transition ก่อน final
```

B-roll report v35:

```text
โหลดใหม่จาก stock provider: 30 candidates จาก Pexels
generate ใหม่ด้วย AI video model: 0
ใช้ source เดิม: 0
เลือก source ใหม่สำหรับ final: 10
สร้าง optimized/re-encoded derivative: 10
rejected candidate: 20
QA: pass ทั้ง 10 จุดหลังเปลี่ยน candidate ที่มี text/UI รบกวนออก
```

B-roll keyword mapping v35:

```text
slot 01: 01.0s / ai_video_editing_workflow / Pexels / assets/broll/stock/pexels/test2-v35-full/slot-01/ai-video-editing-workflow-33897462-1920x1080.mp4
slot 02: 03.9s / ai_automation_video_editing / Pexels / assets/broll/stock/pexels/test2-v35-full/slot-02/ai-automation-video-editing-32386590-1920x1080.mp4 / covers cut 04.38s
slot 03: 08.4s / two_source_video_production / Pexels / assets/broll/stock/pexels/test2-v35-full/slot-03/two-source-video-production-6883836-4096x2160.mp4
slot 04: 14.8s / workflow_handoff_to_ai / Pexels / assets/broll/stock/pexels/test2-v35-full/slot-04/workflow-handoff-to-ai-7252677-1920x1080.mp4 / covers cut 15.36s
slot 05: 18.7s / ai_processing_workflow / Pexels / assets/broll/stock/pexels/test2-v35-full/slot-05/ai-processing-workflow-36252897-1920x1080.mp4 / covers cut 19.20s
slot 06: 25.9s / audio_cleanup_dead_air / Pexels / assets/broll/stock/pexels/test2-v35-full/slot-07/audio-loudness-polish-7859988-2048x1080.mp4
slot 07: 32.7s / audio_loudness_polish / Pexels / assets/broll/stock/pexels/test2-v35-full/slot-07/audio-loudness-polish-37014189-1920x1080.mp4
slot 08: 39.8s / editing_layout_broll_insert / Pexels / assets/broll/stock/pexels/test2-v35-full/slot-08/editing-layout-broll-insert-15517230-1920x1080.mp4
slot 09: 42.7s / caption_overlay_design / Pexels / assets/broll/stock/pexels/test2-v35-full/slot-09/caption-overlay-design-11206661-1920x1080.mp4 / covers cut 43.20s
slot 10: 46.9s / creator_final_export_thumbnail / Pexels / assets/broll/stock/pexels/test2-v35-full/slot-10/creator-final-export-thumbnail-9909332-2048x1080.mp4 / covers cut 47.32s
```

QA / render:

```text
npm run check: ผ่าน
warning เดิม: timeline_track_too_dense จาก subtitle track 3
render output: /Users/gobank01/Documents/Video V2/stacked-output-v35-test2-full-context-softcut-broll-full-test.mp4
duration: 59.354s container
video: 1080x1920, 30fps, h264
audio: AAC, 48kHz, stereo
file size: 35,837,593 bytes
candidate contact sheet: stacked-video/render-checks/test2-v35-full-candidates/contact-sheet.jpg
selected B-roll contact sheet: stacked-video/render-checks/test2-v35-broll/contact-sheet.jpg
output B-roll contact sheet: stacked-video/render-checks/v35-test2-broll/contact-sheet.jpg
soft cut contact sheet: stacked-video/render-checks/v35-test2-cuts/contact-sheet.jpg
```

Rule update:

```text
v35 ยืนยันว่า Full context index + Medium cut ใช้ได้ดีสำหรับลดคลิปประมาณ 85s เหลือประมาณ 60s
ถ้าต้องการงานคุณภาพ ให้โหลด B-roll candidate ใหม่อย่างน้อย 3 candidate ต่อ slot แล้วเลือกจากบริบท
ให้ตรวจ contact sheet ก่อน render และหลัง render ทุกครั้ง
ถ้า candidate มี text/logo/watermark/brand อื่น หรือ graphic รบกวน ให้ reject และเลือกใหม่เสมอ
ถ้าจุดตัดตรงกับภาพหน้าหรือ screen ที่โดด ให้ retime B-roll ให้คร่อมจุดตัดประมาณ 0.5-1.0s
```

## Context Index Short Edit v34

โจทย์:

```text
ทดสอบว่าการวิเคราะห์บริบทก่อนตัด จะช่วยตัดคลิปจากประมาณ 85s เหลือประมาณ 60s โดยยังคงสาระครบได้ไหม
ต้องการ B-roll เข้ากับเนื้อหามากขึ้น และจุดตัดเนียนขึ้นแบบ soft cut
```

ผล:

```text
ใช้ได้: context index ช่วยให้ตัดเป็นช่วงความหมาย ไม่ใช่ตัดตามเวลาเท่า ๆ กัน
original composition: 84.5s
v34 output: 59.354s container
ลดลงประมาณ: 25.17s
soft cut: video xfade + audio acrossfade 0.12s ทุกจุดตัด
```

ไฟล์ใหม่:

```text
assets/context/test2-v34-context-index.json
assets/top_test2_context60_softcut.mp4
assets/bottom_test2_context60_audio_polished_softcut.mp4
assets/broll/optimized/test2-v34/manifest.json
scripts/build-v34-context-cut.js
```

คำสั่ง:

```bash
npm run build:context60:test2
npm run check
npx --yes hyperframes@0.6.16 render --output ../stacked-output-v34-test2-context60-softcut-full-test.mp4 --quality standard
```

ช่วงที่เก็บไว้:

```text
0.00-4.50s: hook ว่า AI กำลังตัดต่อ
10.38-21.48s: ฟุต 2 ตัว + ส่งให้ AI
24.18-28.14s: สั่ง AI ตัดต่อแบบง่าย
33.24-57.36s: รอประมวลผล, Dead Air, ปรับเสียง, layout, B-roll
63.22-67.46s: caption + overlay
72.42-84.46s: intro/outro, thumbnail, output จริง, CTA
```

ช่วงที่ตัดออก:

```text
4.50-10.38s: พูดซ้ำว่าเป็นคลิปง่ายและ AI ตัดต่อได้
21.48-24.18s: bridge ซ้ำเรื่อง workflow เสร็จ/งานนิ่ง
28.14-33.24s: AI ตอบรับงาน เป็นช่วงรอที่ไม่เพิ่มสาระ
57.36-63.22s: filler และคำไม่ชัด
67.46-72.42s: คำซ้ำเรื่องสี/transition ก่อนขั้นตอน final
```

Screen analysis:

```text
sample top/screen ทุก 5s
contact sheet: stacked-video/render-checks/test2-v34-screen-sample/contact-sheet.jpg
ข้อสรุป: ใช้เสียง/transcript เป็นตัวหลัก และใช้ screen เป็นตัวช่วยยืนยันว่าเป็น workflow/prompt/step panels
```

B-roll v34:

```text
ใช้ B-roll 10 จุดจาก v32 ที่ผ่าน QA แล้ว แต่ retime ใหม่ตาม context index
โหลดใหม่จาก stock provider: 0
generate ใหม่ด้วย AI video model: 0
ใช้ source เดิม: 10
สร้าง optimized/re-encoded derivative ใหม่: 0
rejected candidate: 0
```

B-roll keyword mapping v34:

```text
slot 01: 01.2s / ai_video_editing_intro / hook
slot 02: 06.4s / ai_editing_automation / two_sources_and_ai
slot 03: 09.0s / two_video_sources / two_sources_and_ai
slot 04: 12.2s / workflow_to_ai / two_sources_and_ai
slot 05: 20.0s / ai_processing_job / ai_processing_steps
slot 06: 26.4s / dead_air_cleanup / ai_processing_steps
slot 07: 34.0s / audio_polish_normalization / ai_processing_steps
slot 08: 40.1s / broll_video_editing / ai_processing_steps
slot 09: 44.0s / caption_overlay_graphics / captions_overlay
slot 10: 48.2s / intro_outro_thumbnail_export / final_checks_and_cta
```

QA / render:

```text
npm run check: ผ่าน
warning เดิม: timeline_track_too_dense จาก subtitle track 3
render output: /Users/gobank01/Documents/Video V2/stacked-output-v34-test2-context60-softcut-full-test.mp4
duration: 59.354s container
video: 1080x1920, 59.333s
audio: 59.349s
file size: 39,492,866 bytes
B-roll contact sheet: stacked-video/render-checks/v34-test2-broll/contact-sheet.jpg
soft cut contact sheet: stacked-video/render-checks/v34-test2-cuts/contact-sheet.jpg
```

Rule update:

```text
เมื่อต้องตัดคลิปให้สั้นลงโดยยังคงสาระ ให้สร้าง context index ก่อนเสมอ
context index ต้องเก็บ keptSegments, droppedSegments, reason, topic, intent, screenContext, B-roll keyword
ใช้ transcript/audio เป็นหลัก และใช้ screen sampling ทุก ~5s เป็นตัวช่วย
หลัง soft cut ต้อง re-encode top/bottom เป็น 30fps / GOP 30 / faststart ก่อน render
```

## Codex Skill v33

สร้าง reusable skill สำหรับ session ใหม่:

```text
skill name: bizdrive-video
path: ~/.codex/skills/bizdrive-video
```

ใช้เมื่อต้องทำหรือแก้ไขวิดีโอ Bizdrive แบบ stacked vertical:

```text
trim คู่ขนาน top/bottom
dead air removal
audio polish
Thai caption ตาม Bizdrive spec
contextual B-roll จากคำพูดก่อน/หลัง
B-roll QA และ manifest report
HyperFrames render
version/workflow update
```

ไฟล์ใน skill:

```text
~/.codex/skills/bizdrive-video/SKILL.md
~/.codex/skills/bizdrive-video/references/pipeline.md
~/.codex/skills/bizdrive-video/references/broll.md
~/.codex/skills/bizdrive-video/references/caption-spec.md
~/.codex/skills/bizdrive-video/scripts/broll_manifest_report.py
~/.codex/skills/bizdrive-video/agents/openai.yaml
```

ตรวจแล้ว:

```text
quick_validate.py: Skill is valid
broll_manifest_report.py: ทดสอบกับ assets/broll/optimized/test2-v32/manifest.json ผ่าน
```

## Fresh Context B-roll v32

เป้าหมาย:

```text
ทำ B-roll ใหม่ทั้งหมด ไม่ reuse source เก่า
เลือก keyword จากคำพูดก่อนหน้า + คำพูดหลังจากจุดที่จะ insert
ดูบริบทว่าช่วงนั้นกำลังพูดถึงอะไร เพื่อให้ B-roll เข้ากับเนื้อหาที่สุด
```

วิธีคิด keyword:

```text
1. อ่าน transcript รอบจุด insert อย่างน้อย 1 cue ก่อนหน้า และ 1 cue หลังจากนั้น
2. สรุป intent ของช่วงนั้น เช่น AI editing, workflow, dead air, audio polish, caption, thumbnail
3. ใช้ keyword ที่สื่อ action/visual ไม่ใช่แค่คำตรงตัว
4. ถ้าค้นแล้วเจอ text/logo/brand/UI รบกวน ให้เปลี่ยน query ใหม่หรือโหลด candidate เพิ่ม
5. เลือกตัวที่ผ่าน QA และเข้ากับบริบทมากที่สุดก่อน re-encode
```

ผลรอบ v32:

```text
download ใหม่จาก Pexels: 42 candidate
generate ใหม่ด้วย AI video model: 0 ไฟล์
ใช้ source เดิม: 0 ไฟล์
เลือก source ใหม่สำหรับ final: 10 ไฟล์
สร้าง optimized/re-encoded derivative: 10 ไฟล์
rejected candidate: 32 ไฟล์
```

ไฟล์สำคัญ:

```text
candidate manifest:
assets/broll/stock/pexels/test2-v32/candidates-manifest.json
assets/broll/stock/pexels/test2-v32-extra/extra-candidates-manifest.json

final manifest:
assets/broll/optimized/test2-v32/manifest.json

final B-roll:
assets/broll/optimized/test2-v32/broll-01.mp4
assets/broll/optimized/test2-v32/broll-02.mp4
assets/broll/optimized/test2-v32/broll-03.mp4
assets/broll/optimized/test2-v32/broll-04.mp4
assets/broll/optimized/test2-v32/broll-05.mp4
assets/broll/optimized/test2-v32/broll-06.mp4
assets/broll/optimized/test2-v32/broll-07.mp4
assets/broll/optimized/test2-v32/broll-08.mp4
assets/broll/optimized/test2-v32/broll-09.mp4
assets/broll/optimized/test2-v32/broll-10.mp4
```

B-roll keyword mapping v32:

```text
slot 01: ai_video_editing_intro / Pexels / context "กำลังตัดต่อด้วย AI" -> "AI ตัดต่อได้แล้ว"
slot 02: ai_editing_automation / Pexels / context "AI สามารถตัดต่อได้แล้ว" -> "คลิปแนะนำการตัดต่อด้วย AI"
slot 03: two_video_sources / Pexels / context "มีฟุตอยู่สองตัว" -> "หน้าคน + หน้าจอ"
slot 04: workflow_to_ai / Pexels / context "โยนให้ AI ตัดต่อ" -> "workflow เสร็จแล้ว"
slot 05: ai_processing_job / Pexels / context "AI รับงานต่อ" -> "รอ 7-10 นาที"
slot 06: dead_air_cleanup / Pexels / context "เช็คไฟล์ก่อน" -> "ตัด Dead Air"
slot 07: audio_polish_normalization / Pexels / context "ตัดเสียงฟุ่มเฟือย" -> "ปรับเสียงให้ดังเสมอกัน"
slot 08: broll_video_editing / Pexels / context "วาง layout" -> "ใส่ B-roll"
slot 09: caption_overlay_graphics / Pexels / context "ทำ caption/overlay" -> "ตัวเหลืองเด่น"
slot 10: intro_outro_thumbnail_export / Pexels / context "ใส่ intro/outro" -> "ทำ thumbnail/export"
```

QA / render:

```text
npm run check: ผ่าน
warning เดิม: timeline_track_too_dense จาก subtitle track 3
render output: /Users/gobank01/Documents/Video V2/stacked-output-v32-test2-fresh-broll10-full-test.mp4
duration: 84.521s container
video: 1080x1920, 84.500s
audio: 84.501s
file size: 49,759,555 bytes
candidate contact sheet: stacked-video/render-checks/test2-v32-broll/contact-sheet.jpg
output contact sheet: stacked-video/render-checks/v32-test2/contact-sheet.jpg
```

## Test 2 Full Edit v30

Raw input:

```text
/Users/gobank01/Documents/Video V2/test 2/top screen - video 2.mp4
/Users/gobank01/Documents/Video V2/test 2/botton screen - video 2.mp4
```

Raw metadata:

```text
top: 1920x1080, 30fps, duration 91.733s
bottom: 1920x1080, 30fps, duration 91.733s
```

Trim / dead air decision:

```text
ตรวจจากเสียง bottom เป็นหลัก
ตัดแบบคู่ขนานเวลาเดียวกันทั้ง top และ bottom
threshold ที่ใช้วิเคราะห์: silencedetect -30dB / -35dB, d=0.5s
```

ช่วงที่เก็บไว้:

```text
2.888187s - 30.975021s
31.562875s - 37.526229s
38.183312s - 40.748438s
41.893417s - 71.030854s
71.592750s - 86.354667s
86.855792s - 90.762208s
```

ผลรวม:

```text
raw duration: 91.733s
clean duration: 84.433s video / 84.5s composition
cut total: ประมาณ 7.31s
```

ไฟล์ clean / polished:

```text
assets/top_test2_deadair_cut.mp4
assets/bottom_test2_deadair_cut.mp4
assets/bottom_test2_audio_polished.mp4
assets/bottom_test2_audio_polished.wav
assets/transcript_test2.large-v3.json
```

Audio polish:

```text
highpass 80Hz
noise reduction: afftdn
compressor
loudness normalization target -16 LUFS
limiter / final volume safety
sample rate: 48kHz AAC สำหรับ video, 16kHz mono WAV สำหรับ whisper
ตรวจ volumedetect หลัง polish: mean ประมาณ -18.8dB, max ประมาณ -1.3dB
```

Subtitle:

```text
ถอดเสียงด้วย whisper large-v3 ภาษาไทย
สร้าง subtitle ใหม่ 40 cues
ทุก cue ไม่เกิน 20-22 ตัวอักษรโดยประมาณ
ตัดคำฟุ่มเฟือย เช่น เออ อ่า เนอะ นะครับ ออกเท่าที่ไม่เสียความหมาย
highlight คำหลัก: AI, ตัดต่อ, workflow, Dead Air, เสียง, B-roll, caption, overlay, intro, outro, thumbnail
```

B-roll:

```text
ใช้ 10 B-roll slots จุดละ 3s
ใช้ตำแหน่ง top frame เดิม
ทุกตัว muted / data-volume=0
เลือกจาก candidate ที่ผ่าน visual QA: ไม่มี logo/brand/watermark/text ใหญ่ชัด
ไม่ใช้ candidate ที่มี money graphic/text หรือ Wall Street sign
โหลดใหม่จาก Pexels/OpenRouter: 0 ไฟล์
ใช้ source เดิม: 10 ไฟล์
สร้าง optimized/re-encoded derivative: 10 ไฟล์
```

B-roll optimized files:

```text
assets/broll/optimized/test2-v30/broll-01.mp4
assets/broll/optimized/test2-v30/broll-02.mp4
assets/broll/optimized/test2-v30/broll-03.mp4
assets/broll/optimized/test2-v30/broll-04.mp4
assets/broll/optimized/test2-v30/broll-05.mp4
assets/broll/optimized/test2-v30/broll-06.mp4
assets/broll/optimized/test2-v30/broll-07.mp4
assets/broll/optimized/test2-v30/broll-08.mp4
assets/broll/optimized/test2-v30/broll-09.mp4
assets/broll/optimized/test2-v30/broll-10.mp4
```

B-roll keyword mapping:

```text
slot 01: business_dashboard / Pexels / source business-dashboard-34128979
slot 02: business_dashboard / Pexels / source business-dashboard-34129037
slot 03: ai_stock_dashboard / OpenRouter old v22 / inferred keyword
slot 04: market_chart / OpenRouter old v22 / inferred keyword
slot 05: data_visualization / OpenRouter old v22 / inferred keyword
slot 06: ai_stock_dashboard / OpenRouter v23
slot 07: passive_dividend_investing / OpenRouter v23
slot 08: ai_prompt_workflow / OpenRouter v23
slot 09: us_stock_investing / OpenRouter v23
slot 10: sp500_dividend / OpenRouter v23
```

หมายเหตุ B-roll:

```text
re-encode ทุกตัวเป็น 30fps / GOP 30 / faststart แล้ว
ผล render ไม่มี warning sparse keyframes
```

ตำแหน่ง B-roll v30:

```text
01.500s - 04.500s
08.000s - 11.000s
14.500s - 17.500s
22.000s - 25.000s
31.000s - 34.000s
39.000s - 42.000s
47.000s - 50.000s
56.000s - 59.000s
66.000s - 69.000s
76.000s - 79.000s
```

Check:

```text
npm run check
0 errors
No console errors
0 layout issues
warning เดิม: timeline_track_too_dense จาก subtitle track 3
```

Output:

```text
/Users/gobank01/Documents/Video V2/stacked-output-v30-test2-broll10-full-test.mp4
duration: 84.521s container
video: 1080x1920, 84.500s
audio: 84.501s
file size: ประมาณ 45.1 MB
render time: ประมาณ 4m08s
```

Frame QA:

```text
stacked-video/render-checks/test2-v30-broll/contact-sheet.jpg
stacked-video/render-checks/v30-test2/contact-sheet.jpg
```

## Saved Baseline v28

สถานะที่ต้องถือเป็น baseline ล่าสุด:

```text
composition: index.html มี B-roll 10 slots จาก Pexels stock library
workflow: ใช้ index ก่อน -> Pexels API -> OpenRouter fallback
render baseline: /Users/gobank01/Documents/Video V2/stacked-output-v27-pexels-broll10-full-test.mp4
frame QA: stacked-video/render-checks/v27-broll10/contact-sheet.jpg
status: save แล้ว ใช้ต่อเป็นจุดเริ่มงานรอบหน้า
```

ไฟล์ test v22:

```text
/Users/gobank01/Documents/Video V2/stacked-output-v22-broll-test-10s.mp4
/Users/gobank01/Documents/Video V2/stacked-output-v22-broll-openrouter-test-10s.mp4
```

ผล test v22:

```text
duration: ประมาณ 10.02s
video: 1080x1920
audio: 1 track จาก bottom
B-roll slot 01 แสดงช่วง 6-9s ทับตำแหน่ง top ถูกต้อง
frame check: stacked-video/render-checks/v22-broll-test-007.jpg
OpenRouter frame check: stacked-video/render-checks/v22-broll-openrouter-test-007.jpg
```

ไฟล์ full test v23:

```text
/Users/gobank01/Documents/Video V2/stacked-output-v23-broll5-full-test.mp4
```

ผล full test v23:

```text
duration: 103.521s
video: 1080x1920, 103.500s
audio: 1 track จาก bottom, 103.509s
file size: ประมาณ 49.9 MB
B-roll: 5 จุด จุดละ 3s แทนตำแหน่ง top สำเร็จ
render time: ประมาณ 3m17s
```

frame check v23:

```text
stacked-video/render-checks/v23-broll5-007.jpg
stacked-video/render-checks/v23-broll5-020.jpg
stacked-video/render-checks/v23-broll5-035.jpg
stacked-video/render-checks/v23-broll5-069.jpg
stacked-video/render-checks/v23-broll5-086.jpg
```

## Subtitle ล่าสุด

ไฟล์ output ล่าสุดแบบ perfect:

```text
/Users/gobank01/Documents/Video V2/stacked-output-caption-v4-perfect.mp4
```

ไฟล์ test 10 วินาทีแรกของ perfect workflow ล่าสุด:

```text
/Users/gobank01/Documents/Video V2/stacked-output-caption-v4-border-4px-test-10s.mp4
```

ค่าที่ตรวจแล้ว:

```text
size: 1080x1920
duration: ประมาณ 103.52s
audio: 1 track จาก bottom_deadair_cut.mp4
subtitle cues: 59 cues
max subtitle length: 19 ตัวอักษร
caption spec: BIZDRIVE VIDEO CAPTION SPEC v4.1
file size: ประมาณ 41.6 MB
perfect full render: 1080x1920, duration 103.521s, video 103.500s, audio 103.509s, file size ประมาณ 41.6 MB
perfect 10s test: 1080x1920, duration ประมาณ 10.02s, audio จาก bottom, ผ่าน npm run check โดยมีแค่ warning track 3 dense
```

กฎ subtitle:

- วาง subtitle ใต้ `bottom.mp4`
- แสดงผลทีละ cue ไม่เกิน `20` ตัวอักษร
- ต้องเป็นคำไทยเต็มคำ ห้ามตัดคำครึ่งคำ
- ตัดคำไม่จำเป็นออก เช่น `อืม`, `อะ`, `อ่ะ`, คำฟุ่มเฟือยที่ไม่จำเป็นต่อใจความ
- คำทับศัพท์ที่ระบบถอดเสียงเป็นไทยผิดให้แก้เป็นอังกฤษ เช่น `พร้อม` ต้องเป็น `prompt`
- ตั้งเวลา cue ให้ตรงกับเสียงและภาพมากที่สุด

Caption style v4.1:

```text
font: IBM Plex Sans Thai + Inter
weight: 800 normal, 900 gold highlight
position: top 1490px, height 160px, left/right margin 60px
z-index: 7
box: glass panel, yellow border, radius 20px, blur 8px
highlight: .gold gradient #FFD93D -> #F4C20F -> #B8860B
tiers: xl 100px, lg 84px, md 60px, sm 50px, xs 38px
animation: entrance y=30 scale=.92 opacity=0, gold pop scale=.7, exit opacity=0
```

หมายเหตุ: ใน `index.html` ให้ `.gold` ใช้ `vertical-align: baseline` และ padding แบบ `0 0.04em` เพื่อให้คำสีเหลืองวางระดับเดียวกับข้อความปกติและช่องว่างดูสม่ำเสมอ ส่วน `line-height: 1.25` ยังเก็บไว้เพื่อให้ glyph ไทย/อังกฤษผ่าน HyperFrames inspect

วิธีถอดเสียงที่ใช้:

```bash
ffmpeg -y -i assets/bottom_audio_polished.mp4 -vn -ac 1 -ar 16000 assets/bottom_audio_polished.wav
/opt/homebrew/bin/whisper-cli --model ~/.cache/hyperframes/whisper/models/ggml-large-v3.bin --language th --output-json-full --output-file assets/transcript.large-v3 --suppress-nst --prompt "ภาษาไทย การลงทุน หุ้นอเมริกา AI S&P 500 เงินปันผล prompt พี่แบงค์" assets/bottom_audio_polished.wav
```

หมายเหตุ: ใช้ไฟล์ polished สำหรับถอดเสียงเมื่อมีแล้ว เพราะเป็นเสียงเดียวกับ final render และยัง sync กับวิดีโอเดิมจากการ copy video stream. ใช้โมเดล `large-v3` ภาษาไทย เพราะรอบ `small` มีตัวอักษรไทยเพี้ยนหลายจุด

## ไฟล์ที่ต้องมี

วางไฟล์ต้นฉบับไว้ในโฟลเดอร์หลัก:

```text
video/bg.png
video/top.mp4
video/bottom.mp4
```

ในโปรเจกต์ HyperFrames ให้ copy เข้า:

```text
stacked-video/assets/bg.png
stacked-video/assets/top.mp4
stacked-video/assets/bottom.mp4
```

## Layout ที่ได้ผลแล้ว

Composition:

```text
width: 1080
height: 1920
```

Background:

```css
inset: 0;
width: 100%;
height: 100%;
object-fit: cover;
z-index: 0;
```

Top video:

```css
left: 0;
top: 198.9px;
width: 1080px;
height: 607.5px;
object-fit: contain;
border: 4px solid transparent;
border-radius: 30px;
background: yellow/gold gradient border ชัด;
z-index: 2;
```

Bottom video:

```css
left: 50%;
top: 846.4px;
width: 607.5px;
height: 607.5px;
border-radius: 50%;
transform: translateX(-50%);
object-fit: cover;
border: 4px solid transparent;
background: yellow/gold gradient border ชัด;
z-index: 2;
```

ระยะห่างระหว่าง `top` กับ `bottom` ประมาณ `40px`

## Trim ที่ใช้ในงานนี้

ไฟล์ `top.mp4` และ `bottom.mp4` ต้องตัดด้วยเวลาเดียวกัน เพราะเป็นคลิปที่บันทึกพร้อมกัน:

```text
trim start: 24s
trim end: 128.542s
final duration หลัง trim: 104.542s
```

เหตุผล:

- `top.mp4` คือหน้าจอ และ `bottom.mp4` คือหน้าคน + เสียง จึงต้อง map ด้วย timestamp เดียวกันเสมอ
- ช่วงต้นมีการเริ่มใหม่หลายครั้ง จึงใช้จุดเริ่มจริงที่ `24s`
- เสียงฝั่ง `bottom.mp4` เข้าช่วงเงียบท้ายคลิปตั้งแต่ประมาณ `128.541958s` จึงใช้เป็นจุดตัดท้าย
- ตอน render final ให้เปลี่ยน `data-duration` ทุกจุดเป็น `104.542`

## หลักคิดการหา trim start จากไฟล์ดิบ

ไฟล์ดิบที่ส่งเข้ามามักมีช่วงต้นที่ยังไม่ใช่เนื้อหาจริง เช่น ไอ เคลียร์คอ พูดผิด ลองเริ่มใหม่ เงียบเพื่อทำสมาธิ แล้วค่อยเริ่มพูดใหม่อีกครั้ง

ดังนั้นห้ามใช้ “เสียงแรกที่ได้ยิน” เป็นจุดเริ่มโดยอัตโนมัติ ให้หา “จุดที่เริ่มพูดจริงแล้วพูดยาวต่อเนื่อง” แทน

วิธีคิด:

- ฟัง/ดู `bottom.mp4` เป็นหลัก เพราะเป็นไฟล์หน้าคน + เสียง
- มองหาช่วงต้นที่มีเสียงสั้น ๆ แล้วเงียบ หรือพูดแล้วหยุดเพื่อเริ่มใหม่ ให้ตัดทิ้ง
- จุดเริ่มจริงคือจังหวะที่เริ่มพูดแล้วต่อเนื่องยาว ไม่กลับไปเงียบเพื่อ reset ใหม่
- เกณฑ์ยืนยัน: หลังจุดเริ่มจริง ควรมีเสียงพูดต่อเนื่องยาวระดับประมาณ `30s` ขึ้นไปแน่นอน ถ้าพูดสั้น ๆ แล้วเงียบ ยังไม่นับเป็นจุดเริ่มจริง
- ถ้าหลังจากเริ่มพูดยาวแล้วมีพูดผิดเล็กน้อย ให้เก็บไว้ ไม่ต้องตัด เพราะถือว่าอยู่ในเนื้อหาจริงแล้ว
- เมื่อได้เวลาเริ่มจริง ต้องใส่เวลาเดียวกันเป็น `data-media-start` ให้ทั้ง `topVideo` และ `bottomVideo`
- ห้าม trim เฉพาะไฟล์ใดไฟล์หนึ่ง เพราะภาพหน้าจอ หน้า และเสียงจะหลุด sync

สรุปสั้น ๆ: ตัดเฉพาะช่วง “ก่อนเริ่มจริง” ออก โดยจุดเริ่มจริงต้องมีการพูดยาวต่อเนื่องประมาณ `30s+` หลังจากนั้นไม่ต้องไล่ตัดทุกจุดที่พูดผิด

ตัวอย่าง media attributes:

```html
<video id="topVideo" data-media-start="24" data-volume="0" muted />
<video id="bottomVideo" data-media-start="24" data-has-audio="true" />
```

## HyperFrames rules ที่ต้องจำ

- วิดีโอที่มี `data-start` ต้องเป็น direct child ของ stage ไม่ควรซ้อนใน timed wrapper
- วิดีโอที่ต้องการเสียงให้ใส่ `data-has-audio="true"`
- วิดีโอที่ไม่เอาเสียงให้ใส่ `muted` และ `data-volume="0"`
- ใช้ `data-track-index` แยกกันทุก clip
- ใช้ CSS `z-index` สำหรับ layer จริง ไม่ใช่ `data-track-index`

## Final mode

ถ้า render baseline ที่ trim แค่ต้น/ท้าย ให้ตั้ง `data-duration` ทุกจุดเป็นความยาวหลัง trim:

```text
104.542
```

ถ้า render เวอร์ชันล่าสุดที่ตัด dead air แล้ว ให้ใช้ไฟล์ clean และเปลี่ยน `data-duration` ทุกจุดเป็น:

```text
103.5
```

ต้องเปลี่ยนให้ครบทุกจุด:

```text
root
background
topVideo
bottomVideo
```

render baseline:

```bash
npx --yes hyperframes@0.6.16 render --output ../stacked-output.mp4 --quality standard
```

render เวอร์ชันตัด dead air ล่าสุด:

```bash
npx --yes hyperframes@0.6.16 render --output ../stacked-output-deadair-cut.mp4 --quality standard
```

ทำ audio polish หลังตัด dead air:

```bash
ffmpeg -y -i assets/bottom_deadair_cut.mp4 \
  -map 0:v:0 -map 0:a:0 \
  -c:v copy \
  -af "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-18dB:ratio=3:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95" \
  -c:a aac -b:a 192k \
  assets/bottom_audio_polished.mp4
```

render เวอร์ชันพร้อม subtitle ล่าสุด:

```bash
npx --yes hyperframes@0.6.16 render --output ../stacked-output-subtitle.mp4 --quality standard
```

render เวอร์ชัน caption spec v4.1:

```bash
npx --yes hyperframes@0.6.16 render --output ../stacked-output-caption-v4-perfect.mp4 --quality standard
```

render test 10 วินาทีแรกของ perfect workflow:

```bash
# ชั่วคราวให้ตั้ง duration ของ root/background/topVideo/bottomVideo เป็น 10 ก่อน render
npx --yes hyperframes@0.6.16 render --output ../stacked-output-caption-v4-border-4px-test-10s.mp4 --quality draft
# หลัง render test ให้คืน duration กลับเป็น 103.5
```

## Check ก่อน render

รันทุกครั้งหลังแก้ `index.html`:

```bash
npm run check
```

หลังเพิ่ม subtitle จำนวนมาก อาจมี warning เรื่อง `timeline_track_too_dense` ได้ แต่ต้องไม่มี error:

```text
0 errors
No console errors
0 layout issues
```

## Prompt template สำหรับสั่ง Codex รอบหน้า

```text
ใช้ HyperFrames ในโปรเจกต์นี้

มีไฟล์:
- video/bg.png
- video/top.mp4
- video/bottom.mp4

ต้องการ output MP4 แนวตั้ง 1080x1920:
- bg.png เป็น background เต็มจอ layer ล่างสุด
- top.mp4 เป็นวิดีโอแนวนอน กว้าง 1080px สูง 607.5px
- bottom.mp4 เป็นวิดีโอวงกลม ขนาด 607.5px x 607.5px อยู่ด้านล่างของ top
- ตำแหน่ง top: 198.9px
- ตำแหน่ง bottom: 846.4px
- มีช่องว่างระหว่าง top กับ bottom ประมาณ 40px
- top ใส่มุมโค้ง 30px และกรอบ gradient สีเหลืองทอง 4px พร้อม glow ให้เห็นชัด
- bottom เป็นวงกลมและมีกรอบ gradient สีเหลืองทอง 4px พร้อม glow ให้เห็นชัด
- มี B-roll insert 10 จุด จุดละ 3 วินาที แทนตำแหน่ง top และใช้กรอบ/มุมโค้งเหมือน top
- ตรวจ B-roll ทุกครั้งก่อน final: ถ้ามี text/logo/graphic/brand อื่น ๆ ต้องเปลี่ยนใหม่เสมอ ห้ามใช้ใน final
- ก่อนโหลดหรือเลือก B-roll ให้ใช้คำพูดก่อนหน้า + คำพูดหลังจากจุด insert เพื่อเลือก keyword ที่ตรงบริบทที่สุด
- ถ้าต้องการทำใหม่ ให้โหลด candidate ใหม่ทั้งหมด แล้วสรุปว่าโหลดใหม่/generate ใหม่/reuse/re-encode กี่ไฟล์
- ใช้ stock B-roll จาก `assets/broll/index.json` ก่อน ถ้าไม่มี keyword ที่เหมาะสม ให้ค้น Pexels API ก่อน แล้วค่อย fallback ไป OpenRouter
- Provider order: Pexels API -> OpenRouter `google/veo-3.1-lite` -> OpenRouter `kwaivgi/kling-v3.0-std`
- mute top.mp4
- ใช้เสียงจาก bottom_audio_polished.mp4 หลังทำ audio polish
- trim ทั้งสองคลิปพร้อมกัน: start 24s, end 128.542s
- ตัด dead air / ความเงียบที่นานกว่า 0.5 วินาที แบบคู่ขนานจากทั้งสองคลิปเสมอ
- ใช้ไฟล์ clean: top_deadair_cut.mp4 และ bottom_deadair_cut.mp4
- หลังตัด dead air ให้ทำ audio polish: highpass 80Hz, noise reduction, compressor, loudness normalization -16 LUFS, true peak -1.5dB, limiter
- ใช้ไฟล์เสียง/วิดีโอ polished เป็น bottom: bottom_audio_polished.mp4
- ถอดเสียงด้วย large-v3 ภาษาไทย แล้วทำ subtitle ใต้ bottom
- subtitle แสดงไม่เกิน 20 ตัวอักษรต่อ cue ห้ามตัดคำไทยครึ่งคำ
- ตัดคำฟุ่มเฟือย เช่น อืม อะ อ่ะ
- คำทับศัพท์ เช่น พร้อม ให้แก้เป็น prompt
- ใช้ BIZDRIVE VIDEO CAPTION SPEC v4.1
- caption font IBM Plex Sans Thai + Inter, glass panel, gold highlight, auto font tier
- `.gold` ต้องวาง baseline ให้เท่ากับข้อความธรรมดา และใช้ช่องว่างแบบ proportional เช่น `0.04em`
- ไม่ต้องมี mark สีแดง

ตั้ง duration เป็น 103.5 และ render เป็น stacked-output-caption-v4-perfect.mp4

ผลลัพธ์ที่ต้องได้:
- output: /Users/gobank01/Documents/Video V2/stacked-output-caption-v4-perfect.mp4
- 1080x1920
- ยาวประมาณ 103.52s
- มีเสียง 1 track จาก bottom_audio_polished.mp4
- เสียงผ่าน loudness normalization และ noise reduction แล้ว เสียงพูดดังสม่ำเสมอและไม่แตก
- ไม่พบ silence / ความเงียบยาวกว่า 0.5 วินาที หลังตัด dead air
- มี subtitle ใต้ bottom และทุก cue ไม่เกิน 20 ตัวอักษร
- caption style ตรง BIZDRIVE v4.1
```
