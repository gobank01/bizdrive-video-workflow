# Bizdrive Video Steps

สถานะล่าสุด: v39 - expanded execution map

ไฟล์นี้เป็น step-by-step สำหรับ agent ทำงานทีละขั้น ตอนนี้กางออกเป็น 425 steps เพื่อใช้เป็น roadmap พัฒนาต่อเป็น automation/pipeline ได้

## Phase 1 — Project Intake

1. อ่าน `WORKFLOW.md`
2. อ่าน `CONFIG.md`
3. อ่าน `QA.md`
4. อ่าน `AGENTS.md`
5. ตรวจว่ามี `index.html`
6. ตรวจว่ามี `hyperframes.json`
7. ตรวจว่ามี `package.json`
8. ตรวจว่า working directory คือ `stacked-video`
9. ระบุ output goal จากผู้ใช้
10. ระบุว่าผู้ใช้ต้องการ full render หรือ test render
11. ระบุ target duration ถ้าผู้ใช้ให้มา
12. ถ้าผู้ใช้ไม่ fix duration ให้ใช้ meaning-first duration
13. ระบุว่าต้องใช้ B-roll กี่จุด
14. ระบุว่าต้องโหลด B-roll ใหม่หรือ reuse ได้
15. ระบุ version ปัจจุบันก่อนเริ่ม

## Phase 2 — Input Discovery

16. หาไฟล์ background
17. หาไฟล์ top/screen video
18. หาไฟล์ bottom/face video
19. ถ้าชื่อไฟล์ไม่ตรง ให้เดาจาก role อย่างระวัง
20. ยืนยัน top คือ screen recording
21. ยืนยัน bottom คือ face video
22. ยืนยัน bottom มี audio
23. ยืนยัน top ต้อง mute
24. ตรวจว่าไฟล์อยู่ใน `assets/` หรือ source folder
25. ถ้ายังไม่อยู่ใน `assets/` ให้ copy/prepare ตาม workflow
26. ตรวจ path ที่จะใช้ใน composition
27. ตรวจว่าไม่มี API key ถูกเขียนลงไฟล์
28. ตรวจว่า output เก่าที่เกี่ยวข้องมีชื่ออะไร
29. ตรวจ manifest B-roll ล่าสุดถ้ามี
30. ตรวจ context index ล่าสุดถ้ามี

## Phase 3 — Raw Media Inspection

31. รัน `ffprobe` top raw
32. รัน `ffprobe` bottom raw
33. รัน `ffprobe` B-roll source ถ้ามี
34. ตรวจ duration top
35. ตรวจ duration bottom
36. ตรวจ fps top
37. ตรวจ fps bottom
38. ตรวจ resolution top
39. ตรวจ resolution bottom
40. ตรวจ audio stream bottom
41. ตรวจว่า top audio จะไม่ถูกใช้
42. เปรียบเทียบ duration top/bottom
43. ถ้า duration ต่างมาก ให้หยุดหา sync reason
44. ถ้า fps ต่างมาก ให้ note risk
45. บันทึก raw metadata ลง report หรือ notes

## Phase 4 — True Start / End Analysis

46. ใช้ bottom audio เป็น source หลัก
47. ฟังช่วงต้นของ bottom
48. หา cough, throat clear, false start
49. หา pause เพื่อ reset ใหม่
50. หา start ที่เริ่มพูดจริง
51. ยืนยันว่าหลัง start มี speech ต่อเนื่องประมาณ 30s+
52. ถ้าพูดสั้นแล้วเงียบ ไม่ถือเป็น true start
53. ถ้าพูดผิดเล็กน้อยหลัง true start ให้เก็บไว้ได้
54. หา end ที่เนื้อหาจบจริง
55. หา trailing silence ท้ายคลิป
56. กำหนด trimStart
57. กำหนด trimEnd
58. คำนวณ trimmedDuration
59. บันทึกเหตุผลของ trimStart
60. บันทึกเหตุผลของ trimEnd

## Phase 5 — Parallel Trim

61. trim top ด้วย trimStart/trimEnd
62. trim bottom ด้วย trimStart/trimEnd
63. ห้าม trim bottom อย่างเดียว
64. ห้าม trim top อย่างเดียว
65. re-encode top trimmed เป็น 30fps
66. ตั้ง GOP top เป็น 30
67. ตั้ง faststart top
68. re-encode bottom trimmed เป็น 30fps
69. ตั้ง GOP bottom เป็น 30
70. ตั้ง faststart bottom
71. ตรวจ duration top trimmed
72. ตรวจ duration bottom trimmed
73. ตรวจว่า duration ต่างกันแค่ระดับ container/frame
74. ตั้งชื่อไฟล์ trimmed ให้ชัด
75. บันทึกไฟล์ trimmed ลง report

## Phase 6 — Dead Air Detection

76. ใช้ bottom audio เพื่อหา silence
77. ใช้ `deadAirMinDuration` จาก `CONFIG.md`
78. ใช้ `silenceThresholdDefault` จาก `CONFIG.md`
79. รัน silence detection
80. อ่าน silence start/end
81. แยก silence ที่อยู่ก่อน true start ออก
82. แยก silence ที่อยู่หลัง end ออก
83. เลือกเฉพาะ dead air ที่อยู่ในเนื้อหาจริง
84. ตัดเฉพาะ silence ที่ยาวกว่า policy
85. ตรวจว่าการตัดไม่ทำให้คำพูดขาด
86. สร้าง cut list
87. คำนวณ total dead air removed
88. บันทึก cut list แบบ timestamp
89. ถ้าไม่มี dead air ยาวพอ ให้บันทึกว่า no-op
90. ถ้ามี dead air ใกล้ key term ให้ตรวจด้วยเสียงก่อนตัด

## Phase 7 — Parallel Dead Air Cut

91. ใช้ cut list เดียวกันกับ top
92. ใช้ cut list เดียวกันกับ bottom
93. สร้าง `top_deadair_cut.mp4`
94. สร้าง `bottom_deadair_cut.mp4`
95. re-encode top dead-air cut เป็น 30fps/GOP30/faststart
96. re-encode bottom dead-air cut เป็น 30fps/GOP30/faststart
97. ตรวจ duration top clean
98. ตรวจ duration bottom clean
99. ตรวจ audio stream bottom clean
100. ตรวจ top clean ไม่มี audio ที่ใช้จริง
101. rerun silence detection หลัง cut
102. ยืนยันว่าไม่เหลือ silence ยาวเกิน policy
103. บันทึก dead air removed
104. บันทึก clean file paths
105. ถ้า duration หลุด sync ให้หยุดแก้ก่อนทำต่อ

## Phase 8 — Audio Polish

106. ใช้ bottom clean เป็น input
107. preserve video stream เท่าที่ทำได้
108. apply highpass 80Hz
109. apply noise reduction
110. ฟังว่า noise reduction ไม่แรงเกิน
111. apply compressor
112. apply loudness normalization
113. target integrated loudness -16 LUFS
114. target true peak <= -1.5 dBTP
115. apply limiter
116. encode audio AAC 192k
117. สร้าง `bottom_audio_polished.mp4`
118. ตรวจว่า video stream ยังอยู่
119. ตรวจว่า audio stream ยังอยู่
120. รัน loudness report
121. บันทึก integrated loudness
122. บันทึก true peak
123. spot check เสียงพูด
124. ถ้าเสียงเป็นโลหะ ให้ลด noise reduction
125. ถ้าเสียงแตก ให้ปรับ limiter/loudnorm

## Phase 9 — Transcription

126. extract audio จาก bottom polished
127. convert เป็น mono 16kHz wav ถ้าต้องใช้
128. เลือก Whisper model
129. default เป็น large-v3 ภาษาไทย
130. ใส่ prompt คำเฉพาะของคลิป
131. transcribe bottom polished audio
132. เก็บ raw transcript
133. เก็บ word-level transcript ถ้ามี
134. ตรวจภาษาไทยเพี้ยน
135. ตรวจคำอังกฤษ/ทับศัพท์
136. สร้าง cleaned transcript
137. ลบ filler words
138. แก้คำทับศัพท์ตาม config
139. แก้ `พร้อม` เป็น `prompt` เมื่อบริบทคือ prompt
140. บันทึก transcript source

## Phase 10 — Key Term Preservation

141. โหลด editable key terms จาก `CONFIG.md`
142. เพิ่ม key terms เฉพาะคลิปถ้าจำเป็น
143. เพิ่ม variant การออกเสียง เช่น B-roll, b roll, บีโรล
144. mark key terms ใน raw transcript
145. mark key terms ใน cleaned transcript
146. ห้ามลบ key term ในขั้น clean transcript
147. ตรวจ key term ที่อยู่ใกล้ cut candidate
148. ถ้า key term หาย ให้แก้ transcript/cut plan
149. บันทึก key term list ที่ใช้จริง
150. ตั้ง key term QA เป็น required

## Phase 11 — Context Index

151. แบ่ง transcript เป็น meaning segments
152. ให้แต่ละ segment มี originalStart/originalEnd
153. ใส่ speech text
154. ใส่ topic
155. ใส่ intent
156. ใส่ importanceScore
157. ใส่ redundancyScore
158. ใส่ fillerScore
159. ใส่ cutRisk
160. ใส่ captionKeywords
161. ใส่ keyTermsIncluded
162. sample screen ทุกประมาณ 5s
163. sample screen รอบ likely cut points
164. sample screen รอบ likely B-roll points
165. สรุป screenContext
166. กำหนด brollKeyword
167. กำหนด brollQuery
168. กำหนด keepReason หรือ dropReason
169. กำหนด softCutPlan
170. กำหนด brollCoverRecommended
171. สร้าง context index JSON
172. บันทึก context index path
173. ตรวจว่า context index ครบ field สำคัญ
174. ใช้ context index เป็น source กลางต่อจากนี้
175. ห้ามตัดแบบหารเวลาเท่า ๆ กัน

## Phase 12 — Cut Plan

176. รับ target goal จากผู้ใช้
177. รับ target duration ถ้ามี
178. ถ้าไม่มี target duration ให้เน้นสาระครบก่อน
179. ใช้ default cut aggressiveness จาก `CONFIG.md`
180. เลือก keep segments
181. เลือก drop segments
182. ตัด filler/repetition/waiting bridge ก่อน
183. เก็บ hook
184. เก็บ core explanation
185. เก็บ final CTA ถ้ามี
186. เก็บ key spoken terms อย่างน้อย 1 ครั้งในช่วงที่เกี่ยวข้อง
187. ตรวจว่าการตัดไม่ทำให้ logic ขาด
188. ตรวจว่าการตัดไม่ทำให้ caption พูดคนละเรื่อง
189. ตรวจว่าช่วง drop ไม่ใช่สาระหลัก
190. คำนวณ new duration
191. ถ้า new duration สั้นเกิน ให้คืน segment สำคัญ
192. ถ้า new duration ยาวเกิน ให้หา repetition เพิ่ม
193. สร้าง keep/drop map
194. สร้าง cut points
195. บันทึก cut decision reasons

## Phase 13 — Soft Cut Plan

196. วาง soft cut ทุก content cut
197. default video xfade 0.12s
198. default audio acrossfade 0.12s
199. ถ้าเสียงโดด เพิ่มเป็น 0.15-0.18s
200. ถ้าจังหวะย้วย ลดเป็น 0.08-0.10s
201. ห้ามตัดกลางคำ
202. ห้ามตัดกลางวลีสำคัญ
203. ห้ามตัดกลาง key term
204. ถ้าหลีกเลี่ยงไม่ได้ ให้ใช้ B-roll คร่อมจุดตัด
205. ตรวจ caption timing รอบ crossfade
206. ตรวจ audio waveform รอบ cut
207. สร้าง ffmpeg filter plan
208. render softcut top
209. render softcut bottom
210. ตรวจ softcut media duration

## Phase 14 — B-roll Planning

211. กำหนดจำนวน B-roll จากโจทย์
212. default minimum 3
213. default usual 5-10
214. test2 style ใช้ 10
215. เลือก slot จาก context index
216. เลือก slot ที่ช่วยเล่าเรื่อง
217. เลือก slot ที่ช่วยปิด jump cut
218. หลีกเลี่ยงใส่ B-roll ตอน screen สำคัญมาก
219. อ่าน cue ก่อน slot
220. อ่าน cue หลัง slot
221. สรุป intent ของ slot
222. สร้าง broad visual keyword
223. หลีกเลี่ยง keyword แคบเกิน
224. หลีกเลี่ยง keyword ที่ชวนให้ได้ภาพ text/logo
225. บันทึก beforeSpeech/afterSpeech
226. บันทึก brollQuery
227. บันทึก expected visual
228. กำหนด start/duration
229. ถ้าปิด jump cut ให้คร่อม cut 0.5-1.0s
230. บันทึก B-roll plan

## Phase 15 — B-roll Sourcing

231. ตรวจ stock B-roll index
232. หา source เดิมที่ keyword/topic ตรง
233. ตรวจ QA status ของ source เดิม
234. ถ้า source เดิมผ่านและเหมาะ ให้ mark as reusable
235. ถ้างานต้องสดใหม่ ให้โหลด Pexels candidate ใหม่
236. ตั้ง Pexels orientation landscape
237. ตั้ง minimum HD
238. โหลดอย่างน้อย 3 candidates ต่อ final slot
239. บันทึก Pexels video id
240. บันทึก source URL
241. บันทึก creator/photographer
242. ถ้า Pexels ไม่ได้ผล ให้ใช้ OpenRouter veo-3.1-lite
243. ถ้า veo ไม่ดีพอ ใช้ Kling
244. ห้ามเขียน API key ลงไฟล์
245. บันทึก candidate manifest

## Phase 16 — B-roll QA And Optimization

246. สร้าง candidate contact sheet
247. ตรวจ candidate ทุก slot
248. reject visible unrelated text
249. reject logo
250. reject watermark
251. reject other brand
252. reject distracting graphic
253. reject poor relevance
254. reject wrong crop/orientation
255. เลือก final source ต่อ slot
256. บันทึก reject reason
257. re-encode selected B-roll
258. scale/crop เป็น 1920x1080
259. set fps 30
260. set GOP 30
261. remove audio
262. set faststart
263. สร้าง selected contact sheet
264. สร้าง optimized manifest
265. บันทึก downloaded/generated/reused/optimized/rejected counts

## Phase 17 — Caption Build

266. ใช้ cleaned transcript เป็น source
267. split Thai ด้วย tokenizer ที่ไม่ตัดคำกลาง
268. target 14 chars
269. hard max 22 chars
270. preferred max ประมาณ 20 chars
271. ตัด filler ที่ไม่จำเป็น
272. preserve key terms
273. แปลงเลขไทย/คำจำนวนตาม rule
274. highlight numbers
275. highlight AI
276. highlight money/business/tech terms
277. highlight editable key terms ถ้าเหมาะ
278. ตั้ง cue timing ให้ตรงเสียง
279. หลีกเลี่ยง caption overlap crossfade
280. ตรวจ cue ยาวเกิน
281. ตรวจ orphan vowel
282. ตรวจ mid-word break
283. ตรวจ gold baseline
284. ตรวจ spacing รอบ gold text
285. บันทึก caption cue count

## Phase 18 — Composition Assembly

286. ตั้ง composition 1080x1920
287. วาง background full screen
288. วาง top frame ตาม config
289. วาง bottom circle ตาม config
290. ใส่ top source เป็น softcut top
291. ใส่ bottom source เป็น softcut bottom
292. ตั้ง top muted
293. ตั้ง bottom audio enabled
294. ใส่ B-roll clips เหนือ top
295. ให้ B-roll replace top frame only
296. ตั้ง B-roll muted/no audio
297. ใส่ caption layer ใต้ bottom
298. ตั้ง caption z-index เหนือ video/B-roll
299. ตรวจ outro/overlay z-index ถ้ามี
300. ตั้ง duration root
301. ตั้ง duration background
302. ตั้ง duration top
303. ตั้ง duration bottom
304. ตั้ง duration B-roll/caption ตาม plan
305. ตรวจ deterministic animation

## Phase 19 — Pre-render QA

306. รัน `npm run check`
307. อ่าน lint result
308. อ่าน validate result
309. อ่าน inspect result
310. แก้ error ทุกตัวก่อน render
311. ยอมรับ `timeline_track_too_dense` ได้ถ้าไม่มี error
312. ตรวจ selected B-roll contact sheet
313. ตรวจ caption layout sample
314. ตรวจ frame ก่อน/หลัง cut
315. ตรวจ audio file path
316. ตรวจ top ไม่มี audio
317. ตรวจ bottom มี audio
318. ตรวจ key term อยู่ใน planned transcript
319. ตรวจ output filename
320. ถ้าพบ risk ให้แก้ก่อน render

## Phase 20 — Render

321. render draft ถ้าต้อง test เร็ว
322. render standard สำหรับ review/full test
323. render high เฉพาะ final delivery ถ้าจำเป็น
324. ใช้ output path ที่มี version
325. รอ render จนจบ
326. ห้ามจบงานขณะ render session ยังรัน
327. ถ้า render fail ให้อ่าน error
328. ถ้า browser/frame capture ช้า ให้รอหรือปรับ worker ตามเหมาะสม
329. บันทึก render time
330. บันทึก output file path

## Phase 21 — Post-render QA

331. ตรวจ output exists
332. ตรวจ output metadata ด้วย `ffprobe`
333. ตรวจ duration
334. ตรวจ resolution
335. ตรวจ fps
336. ตรวจ video codec
337. ตรวจ audio codec
338. ตรวจ audio sample rate
339. ตรวจ audio channel count
340. ดึง QA frames ช่วง B-roll
341. ดึง QA frames ช่วง soft cut
342. ทำ output B-roll contact sheet
343. ทำ soft cut contact sheet
344. ตรวจ B-roll ไม่ทับ bottom
345. ตรวจ caption ไม่ทับผิดที่
346. ตรวจ B-roll ไม่มี text/logo/brand ใน output
347. ฟัง spot check audio
348. ฟังจุด soft cut
349. ฟัง key terms สำคัญ
350. ตรวจคำว่า B-roll ถ้าอยู่ใน key terms
351. ตรวจ caption timing
352. ตรวจ caption highlight
353. ตรวจ logo/background placement
354. ตรวจ final 3 seconds
355. ถ้า fail ให้แก้และ rerender

## Phase 22 — Reporting

356. สร้าง final report ตาม `REPORT_TEMPLATE.md`
357. ใส่ version
358. ใส่ output path
359. ใส่ duration
360. ใส่ resolution
361. ใส่ video/audio streams
362. ใส่ file size
363. ใส่ source media paths
364. ใส่ trim summary
365. ใส่ dead air summary
366. ใส่ audio polish summary
367. ใส่ transcript/caption summary
368. ใส่ key term QA
369. ใส่ B-roll downloaded count
370. ใส่ B-roll generated count
371. ใส่ B-roll reused count
372. ใส่ B-roll optimized count
373. ใส่ rejected candidate count
374. ใส่ slot keyword/provider/source mapping
375. ใส่ QA artifacts paths
376. ใส่ `npm run check` result
377. ใส่ files updated
378. ใส่ known warnings
379. ใส่ next recommended step
380. ส่งสรุปให้ผู้ใช้แบบกระชับ

## Phase 23 — Versioning And Documentation

381. ถ้าเปลี่ยน rule ให้เพิ่ม version
382. ถ้าแค่ render ตาม rule เดิม ไม่ต้องเพิ่ม version เว้นผู้ใช้ขอ
383. อัปเดต `CHANGELOG.md`
384. อัปเดต `WORKFLOW.md` ถ้า overview/default เปลี่ยน
385. อัปเดต `CONFIG.md` ถ้า config เปลี่ยน
386. อัปเดต `STEPS.md` ถ้า process เปลี่ยน
387. อัปเดต `QA.md` ถ้า checklist เปลี่ยน
388. อัปเดต `AGENTS.md` ถ้า agent rule เปลี่ยน
389. เก็บ archive เฉพาะเมื่อ restructure ใหญ่
390. ตรวจ links/path ใน docs

## Phase 24 — Artifact Management

391. เก็บ raw metadata
392. เก็บ trim/dead-air decision
393. เก็บ audio report
394. เก็บ raw transcript
395. เก็บ cleaned transcript
396. เก็บ context index
397. เก็บ B-roll candidate manifest
398. เก็บ B-roll optimized manifest
399. เก็บ contact sheets
400. เก็บ output render
401. เก็บ final report
402. ตั้งชื่อไฟล์มี version
403. แยก source stock กับ optimized derivative
404. ห้ามลบ user-provided raw files
405. ห้ามลบ artifacts เก่าโดยไม่ถาม

## Phase 25 — Future Automation Targets

406. ทำ `npm run bizdrive:inspect`
407. ทำ `npm run bizdrive:trim`
408. ทำ `npm run bizdrive:deadair`
409. ทำ `npm run bizdrive:audio`
410. ทำ `npm run bizdrive:transcribe`
411. ทำ `npm run bizdrive:context`
412. ทำ `npm run bizdrive:broll`
413. ทำ `npm run bizdrive:captions`
414. ทำ `npm run bizdrive:compose`
415. ทำ `npm run bizdrive:qa`
416. ทำ `npm run bizdrive:render`
417. ทำ `npm run bizdrive:report`
418. ทำ `npm run bizdrive:full`
419. ทำ schema validation สำหรับ config
420. ทำ schema validation สำหรับ context index
421. ทำ schema validation สำหรับ B-roll manifest
422. ทำ key term preservation checker
423. ทำ loudness checker
424. ทำ B-roll source index updater
425. ทำ final delivery bundle
