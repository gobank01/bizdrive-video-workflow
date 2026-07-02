# Bizdrive Mistakes And Prevention Log

ไฟล์นี้บันทึกความผิดพลาดจริงที่เคยเกิดขึ้น เพื่อบังคับไม่ให้ workflow ทำซ้ำ

## v88 Locked Lessons (bizdrive pipeline integration)

### 1. Python on macOS missing SSL certificates by default

What happened:
```text
python3 scripts/transcribe/transcribe.py → urllib.error.URLError: CERTIFICATE_VERIFY_FAILED
```

Why:
```text
Python.org installer ships with /Library/Frameworks/Python.../etc/openssl/cert.pem that's empty.
"Install Certificates.command" needs sudo and can fail with permission denied.
```

Fix (locked at v88):
```text
python3 -m pip install --user --upgrade certifi
The transcribe:el npm script now sets SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
before invoking transcribe.py. Do not remove that line.
```

### 2. Silero VAD venv missing torchcodec on first install

What happened:
```text
torchaudio 2.11.0 requires torchcodec for audio I/O. Install torchcodec or pin torchaudio < 2.9
```

Fix (locked at v88):
```text
After bash scripts/clean-cut/install_vad.sh:
  ~/.ii23/vad-env/bin/pip install --quiet torchcodec
If a fresh install fails again, pin torchaudio<2.9 in install_vad.sh or pre-install torchcodec there.
```

### 3. ElevenLabs raw response has duration: null

What happened:
```text
raw-elevenlabs.json shape includes "duration": null because ElevenLabs API does not return it.
Downstream scripts that read d["duration"] failed or produced bad timing.
```

Fix (locked at v88):
```text
After every transcribe step, patch the field from ffprobe:
  python3 -c "import json; p='.../raw-elevenlabs.json'; d=json.load(open(p)); d['duration']=<ffprobe>; json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)"
```

### 4. Backup HTML at project root pulled into HyperFrames as a second root

What happened:
```text
After backing up index.v87.html alongside index.html, lint failed:
  multiple_root_compositions: Multiple root-level HTML files with data-composition-id
```

Fix (locked at v88):
```text
Backups live in backups/ subfolder. HyperFrames does not scan there.
Never leave a *.html with data-composition-id at the project root other than index.html.
```

### 5. apply_edits.py produces sparse keyframes on visual masters

What happened:
```text
HyperFrames render warns: "Video 'topVideo' has sparse keyframes (max interval: 8.37s).
This causes seek failures and frame freezing."
```

Why:
```text
apply_edits.py re-encodes each segment with -preset fast -crf 18 but concats with -c copy,
inheriting the per-segment GOP. The framework rendered our v88 fine, but the warning is real.
```

Fix (deferred — does not block v88 reference):
```text
After apply_edits.py, re-encode the master:
  ffmpeg -i master.mp4 -c:v libx264 -r 30 -g 30 -keyint_min 30 -movflags +faststart -c:a copy fixed.mp4
Add this as a post-step to apply_edits.py when the warning surfaces on a new clip.
```

### 6. AI subagent invented timestamps that didn't exist in raw.words[]

What happened (during v88 development):
```text
Early editorial subagent tries to "smooth out" boundary timing and rounds to nice numbers.
That produced cuts that landed mid-syllable on subsequent renders.
```

Fix (locked at v88):
```text
SUBAGENT_PROMPTS.md Section A includes the hard rule:
  "Every spoken segment that's kept must come from raw.json.words[] timing — don't invent timestamps."
Do NOT remove this clause when porting.
```

### 7. Step 8 audio-polish alimiter clipped the polished WAV at 0 dBFS

What happened (2026-05-21, antigravity job):
```text
The V88_PLAYBOOK Step 8 pass-2 chain ended with `alimiter=limit=-1.5dB`.
The polished WAV came out with ~25 samples clipped at full scale —
astats "Peak level dB: 0.000000", ebur128 true peak 0.0 dBFS.
```

Why:
```text
ffmpeg's alimiter has `level` ENABLED by default — it auto-normalises the
output peak back to 0 dBFS, undoing the -1.5 dB limit. The playbook chain
as originally written produces a clipping master on every job.
```

Fix (locked 2026-05-21):
```text
Pass 2 must end with `alimiter=limit=-1.5dB:level=disabled`.
With level disabled the linear loudnorm is true-peak-limited and often lands
~-19 LUFS (below the -18 floor) — that is expected. Then run ONE corrective
2-pass dynamic loudnorm on the WAV (analyze → apply measured values +
alimiter=limit=-1.5dB:level=disabled). It lands ~-17.5 LUFS / TP -1.5.
loudnorm cannot reach -16: the TP -1.5 ceiling caps it, and -17.x is the
genuine ceiling for talking-head content.
ALWAYS verify the polished WAV: astats "Peak level dB" must be <= -1.0, not 0.0.
V88_PLAYBOOK.md Step 8 is updated with the corrected chain + verify commands.
```

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
7. Lip-sync zero-tolerance gate: `LIPSYNC_QA.md` checks pass; if uncertain, final is blocked
8. Bottom visible cut gate: bottom face must not be xfade blended while visible; cut contact sheet must show no ghost/double-mouth frames
9. Edit-first master gate: production render must have locked top visual, bottom visual, and speech audio masters before HyperFrames layout
10. BGM frame-lock gate: BGM mix must preserve final video frame count, video duration, video start_time, and audio start_time; frameDelta must be 0
```

ถ้า gate ใดไม่ผ่าน ห้ามเรียกงานว่าเสร็จ

## v82 BGM Mix Shortened The Accepted Proof

What happened:

```text
หลัง v81 golden proof ผ่าน human review แล้ว มีการ mix BGM 5% เพื่อทำ final candidate
BGM candidate แรกมี video frames ลดจาก 2423 เหลือ 2421
video duration ลดจาก 80.766667s เหลือ 80.700000s
สาเหตุนี้เสี่ยงทำให้ final ไม่ตรงกับ golden proof ที่ผู้ใช้ยืนยันแล้ว
```

Root cause:

```text
scripts/mix-bgm.js ใช้ ffmpeg `-shortest`
หลังผสมเสียง audio stream สั้นกว่า video stream เล็กน้อย
`-shortest` จึงทำให้ mux จบตาม audio และ drop video ท้าย 2 frames
```

Never again:

```text
ห้ามใช้ `-shortest` ใน BGM mix ของ final/golden proof
BGM mix ต้อง preserve video stream จากไฟล์ที่ผ่าน review แล้ว
หลัง BGM mix ต้องเปรียบเทียบ frame count, video duration, video start_time และ audio start_time กับไฟล์ต้นฉบับ
ถ้า frameDelta ไม่ใช่ 0 ห้ามส่ง final
```

Required proof:

```text
reports/phase*/...bgm-qa.json ต้องมี frameLock.status=pass
frameLock.frameDelta=0
final ffprobe ต้องรายงาน video frames เท่ากับ baseline
```

## v68 Lip-Sync Zero Tolerance

User rule:

```text
ปัญหา lip sync ห้ามเกิดขึ้นเด็ดขาด
ต้องโฟกัสเป็นพิเศษทุกครั้ง
ถ้าไม่มั่นใจ 100% ห้ามส่ง final
```

Never again:

```text
ห้ามสรุป sync pass จาก duration/frame count อย่างเดียว
ต้องตรวจ final MP4 stream start_time หลัง render ทุกครั้ง
ต้องมี spot-check จุดปาก/เสียงจริงอย่างน้อย 5 จุด
ถ้าเกิด offset ต้อง log ค่า ms และเหตุผลก่อน compensate
ถ้ายังไม่มั่นใจ ให้รายงาน blocked แทนการส่งงาน
```

Required proof:

```text
อ่านและทำตาม LIPSYNC_QA.md
final report มี lipSyncStatus
final summary มี finalStreamStartDeltaMs, compensationMs และ spotCheckPoints
```

## v69 Bottom Xfade Lip-Sync Failure

User rule:

```text
ถ้าปากกับเสียงยังรู้สึกไม่ตรง ต้องรื้อทั้งหมดและหาสาเหตุจริง
```

What happened:

```text
v66 ใช้ soft cut แบบ xfade กับ bottom face และ acrossfade กับ bottom audio
final contact sheet รอบ content cuts พบ ghost/double-mouth frames
ภาพปากที่ถูก blend จากสองช่วงไม่สามารถตรงกับเสียงพยางค์เดียวได้
```

Root cause:

```text
workflow แปลคำว่า soft cut เป็น xfade/acrossfade ทั้ง top และ bottom
แต่ bottom เป็น talking-head lip-sync layer จึงห้าม blend ปากสองช่วงเข้าด้วยกันตอน visible
metadata compensation 21ms แก้ stream start_time ได้บางส่วน แต่แก้ ghost-mouth frames ไม่ได้
```

Never again:

```text
soft cut ต้องเป็น lip-sync-safe เท่านั้น
top/B-roll xfade ได้ แต่ bottom face ห้าม xfade ตอน visible
ถ้าจุดตัด bottom ดูกระโดด ให้ใช้ B-roll/bridge ปิด jump หรือย้าย cut ไป silence/closed-mouth boundary
ห้ามเรียก final ถ้าไม่มี cut contact sheet รอบ content cuts
```

Required proof:

```text
cut contact sheet รอบทุก content cut
รายงานว่า bottomCutMode เป็น hard/covered ไม่ใช่ visible xfade
lipSyncStatus ต้องเป็น pass เฉพาะเมื่อไม่มี ghost/double-mouth frame และ residualRisk=none
```

## v79 Metadata Passed But Human Lip-Sync Failed

User report:

```text
Set A: ปากไม่ตรง
Set B: ปากตรงเป๊ะ
```

What happened:

```text
Set A and Set B both passed metadata checks: fps, frame count, duration, and stream start_time looked aligned.
Phase 5 also cut top and bottom in parallel using the same cut lists.
Despite that, Set A preview still had mouth/audio mismatch, while Set B preview was visually exact.
```

Root cause:

```text
metadata checks only prove container/timeline alignment
they do not prove semantic lip sync between the mouth pixels and spoken audio
because Set A used bottom audio only and the bottom face still looked off, the issue is upstream of layout/top/B-roll
the likely cause is Set A bottom source has internal audio/video offset, or Set A was not the truly synced raw pair
Set B passed because its bottom face and bottom audio are internally synced in the actual pixels/audio, not merely in metadata
```

Never again:

```text
never accept an input set from metadata alone
before Phase 6, create or open a bottom-face preview with bottom audio and require human/visual lip-sync pass
if a human says mouth is not aligned, mark the set blocked immediately
when multiple sets exist, continue with the set that passes human lip-sync gate
do not fix a failed set by guessing an offset; rebuild from synced source or measure/log compensation with proof
```

Required proof:

```text
raw/phase bottom preview path
human lip-sync result: pass/fail
if fail, report blocked set and chosen passing set
if compensation is used, report measured milliseconds, method, and spot-check points
```

## v72 Edit-First Master Architecture

User diagnosis:

```text
ปัญหา workflow เดิมคือควรตัดต่อให้เสร็จก่อน แล้วค่อยวางลง background
ถ้าเสียงไม่ตรงกับปาก แปลว่าจังหวะการตัดและการรวมกลับมาที่เสียงผิดพลาด
```

What changed:

```text
v72 สร้าง editorial masters ก่อนเข้า HyperFrames layout
top_edit_master, bottom_visual_master และ speech_audio_master ถูกตัดจาก EDL เดียวกัน
HyperFrames render เป็น visual-only
หลัง render จึง mux speech_audio_master กลับเข้า final MP4 แล้วค่อย mix BGM
```

Never again:

```text
ห้ามให้ layout/background/render stage เป็นที่ที่เสียงถูกตัดหรือเลื่อนเวลา
ห้าม render production โดยอิง audio element ใน HyperFrames ถ้า edit-first master ยังทำได้
ห้ามเรียก final ถ้ายังไม่มี proof ว่า editorial masters lock กันก่อนเข้า layout
ถ้า master proof fail ต้องแก้ EDL/cut list ไม่ใช่ชดเชยแบบเดาสุ่มใน final
```

Required proof:

```text
ffprobe top_edit_master: start_time 0, duration, nb_frames
ffprobe bottom_visual_master: start_time 0, duration, nb_frames
ffprobe speech_audio_master: duration, sample_rate 48000
top/bottom frame count เท่ากัน
speech audio duration เท่ากับ frame count / fps
final visual-only render ไม่มี audio
final mux stream start_time video/audio = 0 หรือมี offset ที่วัดและ log แล้ว
```

## v88-clip.sh Omitted the Top Visual Master (2026-06-21 → fixed 2026-07-02)

**What happened:** `tools/v88-clip.sh` applied the rough + jump EDLs only to
`bottom.mp4`. Templates with a top frame (T01, T05, T06, T08, T09) reference
`assets/intermediates/top_visual_master.mp4` — every such job errored at render
or (worse) rendered with a stale/unsynced top. The fix was done BY HAND on at
least 4 jobs (claude-code-class-online, claude-code-for-everyone,
claude-collect-data, context-window): run `apply:edits` twice on `top.mp4`
(edl-rough-safe → edl-jump), then ffprobe both masters for identical
`nb_frames`.

**Fix (2026-07-02):** Step 7b added to `v88-clip.sh` — for T01/05/06/08/09 it
requires `input/top.mp4`, applies both EDLs, and hard-fails if top/bottom frame
counts differ (lip-sync zero tolerance, per the v72 edit-first rule).

Never again:

```text
ห้าม render template ที่มี top frame โดยไม่มี master proof (top nb_frames == bottom nb_frames)
ถ้าเพิ่ม template ใหม่ที่ใช้ top_visual_master ต้องเพิ่มเลข template ใน case ของ Step 7b ด้วย
```
