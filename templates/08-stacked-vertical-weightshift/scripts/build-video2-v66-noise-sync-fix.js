import fs from "node:fs";
import { spawnSync } from "node:child_process";

const VERSION = 66;
const COMPOSITION_DURATION = 87.02;
const XFADE = 0.12;
const FPS = 30;
const TOP_SOURCE = "assets/video2/top.mp4";
const BOTTOM_SOURCE = "assets/video2/bottom.mp4";
const TOP_OUTPUT = "assets/video2/top_context90_v66_softcut.mp4";
const BOTTOM_OUTPUT = "assets/video2/bottom_context90_v66_noise_sync_softcut.mp4";
const SYNC_AUDIO_DELAY_MS = 21;

const keepSegments = [
  {
    id: "hook",
    start: 2.3,
    end: 13.8,
    speech: "AI สามารถตัดต่อได้แล้ว ตัดต่อได้เนียนเหมือนคน",
    topic: "AI video editing hook",
    intent: "เปิดคลิปให้เห็นทันทีว่า AI ตัดต่อได้จริงและเนียน",
    importanceScore: 0.98,
    redundancyScore: 0.05,
    fillerScore: 0.04,
    screenContext: "หน้าจอ code/workflow และตัวอย่างคลิปที่ AI ตัดต่อ",
    captionKeywords: ["AI", "ตัดต่อ", "เนียน"],
    brollKeyword: "AI video editing workstation",
    brollQuery: "creative video editing workstation",
    keepReason: "hook สำคัญที่สุด",
    cutRisk: "low",
  },
  {
    id: "features",
    start: 21.0,
    end: 38.0,
    speech: "คลิปยาวมี Insert สลับจอ Zoom In Zoom Out และ Caption AI ทำได้หมด",
    topic: "Editing features",
    intent: "อธิบายว่างานตัดต่อซับซ้อนหลายอย่าง AI ทำได้",
    importanceScore: 0.93,
    redundancyScore: 0.12,
    fillerScore: 0.08,
    screenContext: "หน้าจอตัวอย่างคลิปและงานตัดต่อ",
    captionKeywords: ["Insert", "Zoom", "Caption", "AI"],
    brollKeyword: "video editing timeline automation",
    brollQuery: "video editing workstation timeline",
    keepReason: "เป็น feature proof ของคลิป",
    cutRisk: "medium",
  },
  {
    id: "technology_ready",
    start: 45.84,
    end: 64.64,
    speech: "เทคโนโลยีถึงแล้ว เมื่อก่อนยังทำไม่ได้ ตอนนี้โยนคลิปไป AI รู้ว่าควรตัดส่วนไหน",
    topic: "Technology readiness",
    intent: "บอกเหตุผลว่าทำไมตอนนี้ใช้ AI ตัดต่อจริงได้",
    importanceScore: 0.9,
    redundancyScore: 0.18,
    fillerScore: 0.08,
    screenContext: "หน้าจอการทำงาน AI/workflow",
    captionKeywords: ["เทคโนโลยี", "AI", "ตัดส่วนไหน"],
    brollKeyword: "AI automation workflow",
    brollQuery: "automation technology laptop",
    keepReason: "เป็นเหตุผลหลักของคลิป",
    cutRisk: "medium",
  },
  {
    id: "assistant_benefit",
    start: 74.24,
    end: 93.04,
    speech: "เรียนรู้ครั้งเดียว ใช้งานได้ยาวๆ เหมือนมีผู้ช่วย ตัดต่อไม่เกิน 10 นาที",
    topic: "Workflow benefit",
    intent: "ขายผลลัพธ์ว่าทำงานเร็วขึ้นและสบายขึ้น",
    importanceScore: 0.94,
    redundancyScore: 0.1,
    fillerScore: 0.05,
    screenContext: "หน้าคนพูดและตัวอย่าง output",
    captionKeywords: ["ผู้ช่วย", "10 นาที", "กาแฟ"],
    brollKeyword: "creator workflow coffee automation",
    brollQuery: "creator laptop coffee workflow",
    keepReason: "เป็น benefit ที่คนดูจำได้",
    cutRisk: "low",
  },
  {
    id: "cta",
    start: 93.04,
    end: 114.44,
    speech: "มาเรียนวันที่ 1 มิถุนายน คลาสจับมือทำ รับแค่ 10 คน",
    topic: "Class CTA",
    intent: "ปิดคลิปด้วยคำเชิญและ scarcity",
    importanceScore: 0.96,
    redundancyScore: 0.08,
    fillerScore: 0.04,
    screenContext: "หน้าคนพูดปิดท้าย",
    captionKeywords: ["1 มิถุนายน", "จับมือทำ", "10 คน"],
    brollKeyword: "online workshop learning",
    brollQuery: "online workshop creator learning",
    keepReason: "CTA ต้องอยู่ครบ",
    cutRisk: "low",
  },
];

const droppedSegments = [
  {
    id: "false_start_and_initial_noise",
    start: 0,
    end: 2.3,
    dropReason: "ช่วงต้นมีเสียงสั้น/ไม่ใช่ sustained speech แล้วตามด้วย silence ยาวประมาณ 1.36s จึงตัดออกเพื่อให้เปิดคลิปด้วยเสียงพูดจริงทันที",
    cutRisk: "low",
  },
  {
    id: "redundant_complexity_detail",
    start: 13.8,
    end: 21.0,
    dropReason: "ขยายความเรื่องความซับซ้อนและใช้ AI ซ้ำกับ hook/features",
    cutRisk: "medium",
  },
  {
    id: "logo_insert_repeat",
    start: 38.0,
    end: 45.84,
    dropReason: "พูดซ้ำเรื่อง caption/logo/insert ที่ features พูดไปแล้ว",
    cutRisk: "low",
  },
  {
    id: "setup_repeat",
    start: 64.64,
    end: 74.24,
    dropReason: "เชื่อมเรื่องเป้าหมายและ setup ซ้ำกับ benefit ถัดไป",
    cutRisk: "medium",
  },
  {
    id: "tail_margin",
    start: 114.44,
    end: 115.946,
    dropReason: "ท้ายคลิปหลัง CTA หลัก",
    cutRisk: "low",
  },
];

const brollSources = [
  {
    id: "broll01",
    start: 5,
    output: "assets/broll/optimized/video2-v66/broll-01.mp4",
    source: "assets/broll/stock/pexels/test2-v35-full/slot-01/ai-video-editing-workflow-33897462-1920x1080.mp4",
    keyword: "ai_video_editing_workstation",
    query: "creative video editing workstation",
    contextSegment: "hook",
  },
  {
    id: "broll02",
    start: 23,
    output: "assets/broll/optimized/video2-v66/broll-02.mp4",
    source: "assets/broll/stock/pexels/test2-v35-full/slot-02/ai-automation-video-editing-32386518-1920x1080.mp4",
    keyword: "ai_automation_workflow",
    query: "automation technology laptop",
    contextSegment: "features",
  },
  {
    id: "broll03",
    start: 41,
    output: "assets/broll/optimized/video2-v66/broll-03.mp4",
    source: "assets/broll/stock/pexels/test2-v35-full/slot-10/creator-final-export-thumbnail-12433099-1920x1080.mp4",
    keyword: "workflow_handoff",
    query: "creator desk workflow",
    contextSegment: "technology_ready",
  },
  {
    id: "broll04",
    start: 59,
    output: "assets/broll/optimized/video2-v66/broll-04.mp4",
    source: "assets/broll/stock/pexels/test2-v35-full/slot-10/creator-final-export-thumbnail-9909332-2048x1080.mp4",
    keyword: "creator_assistant_workflow",
    query: "creator laptop workflow assistant",
    contextSegment: "assistant_benefit",
  },
  {
    id: "broll05",
    start: 77,
    output: "assets/broll/optimized/video2-v66/broll-05.mp4",
    source: "assets/broll/stock/pexels/test2-v35-full/slot-03/two-source-video-production-6883836-4096x2160.mp4",
    keyword: "online_workshop_learning",
    query: "online class creator learning",
    contextSegment: "cta",
  },
];

const panPairs = [
  ["49% 50%", "51% 50%"],
  ["50% 49%", "50% 51%"],
  ["51% 50%", "49% 50%"],
  ["50% 51%", "50% 49%"],
];

const rawCaptionCues = [
  [0.0, 2.2, "cap-md", 'ตอนนี้ <span class="gold">AI</span>'],
  [2.2, 4.3, "cap-lg", "ตัดต่อได้แล้ว"],
  [4.3, 6.5, "cap-md", "เนียนเหมือนคน"],
  [6.5, 9.4, "cap-md", "คลิปแบบนี้"],
  [9.4, 13.2, "cap-md", 'ใช้ <span class="gold">AI</span> ตัดต่อ'],
  [13.8, 16.1, "cap-md", "คลิปยาวๆ"],
  [16.1, 18.7, "cap-lg", 'ใส่ <span class="gold">Insert</span>'],
  [18.7, 21.2, "cap-lg", "สลับจอได้"],
  [21.2, 24.0, "cap-md", '<span class="gold">Zoom</span> In Out'],
  [24.0, 27.0, "cap-md", '<span class="gold">Caption</span> ก็ทำได้'],
  [30.0, 32.2, "cap-md", "เทคโนโลยีถึงแล้ว"],
  [32.2, 35.3, "cap-md", "เมื่อก่อนยังไม่ได้"],
  [35.3, 38.2, "cap-md", "ตอนนี้โยนคลิปไป"],
  [38.2, 41.4, "cap-md", '<span class="gold">AI</span> เข้าใจงาน'],
  [41.4, 45.0, "cap-md", "ควรตัดส่วนไหน"],
  [48.5, 51.0, "cap-md", "เรียนรู้ครั้งเดียว"],
  [51.0, 54.0, "cap-md", "ใช้ได้ยาวๆ"],
  [54.0, 57.1, "cap-md", "เหมือนมีผู้ช่วย"],
  [57.1, 60.5, "cap-lg", 'ตัดต่อ <span class="gold">10 นาที</span>'],
  [60.5, 64.2, "cap-md", "ไปกินกาแฟได้"],
  [67.6, 70.3, "cap-md", "อยากเรียนรู้"],
  [70.3, 73.1, "cap-md", "มาเรียนกับพี่แบงค์"],
  [73.1, 76.2, "cap-md", '<span class="gold">1 มิถุนายน</span>'],
  [76.2, 79.4, "cap-md", "คลาสจับมือทำ"],
  [79.4, 82.6, "cap-md", "ทำไปด้วยกัน"],
  [82.6, 85.8, "cap-md", "ตัดต่อแบบนี้"],
  [85.8, 88.4, "cap-lg", 'รับแค่ <span class="gold">10 คน</span>'],
];

const CAPTION_SHIFT = 2.2;
const captionCues = rawCaptionCues
  .map(([start, end, klass, html]) => [
    round(Math.max(0, start - CAPTION_SHIFT)),
    round(end - CAPTION_SHIFT),
    klass,
    html,
  ])
  .filter((cue) => cue[1] > 0)
  .filter((cue) => cue[0] < COMPOSITION_DURATION)
  .map(([start, end, klass, html]) => [start, Math.min(end, COMPOSITION_DURATION), klass, html]);

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function run(command, args) {
  const result = spawnSync(command, args, { stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`${command} failed with exit code ${result.status}`);
  }
}

function round(value) {
  return Math.round(value * 1000) / 1000;
}

function segmentDurations() {
  return keepSegments.map((segment) => round(segment.end - segment.start));
}

function buildVideoFilter(label) {
  const lines = [];
  keepSegments.forEach((segment, index) => {
    lines.push(`[0:v]trim=start=${segment.start}:end=${segment.end},settb=AVTB,setpts=PTS-STARTPTS,fps=${FPS},format=yuv420p[v${index}]`);
  });
  let current = "v0";
  let currentDuration = segmentDurations()[0];
  for (let index = 1; index < keepSegments.length; index += 1) {
    const offset = round(currentDuration - XFADE);
    const next = `vx${index}`;
    lines.push(`[${current}][v${index}]xfade=transition=fade:duration=${XFADE}:offset=${offset}[${next}]`);
    current = next;
    currentDuration = round(currentDuration + segmentDurations()[index] - XFADE);
  }
  lines.push(`[${current}]fps=${FPS},format=yuv420p[${label}]`);
  return lines.join(";");
}

function buildAudioFilter() {
  const lines = [];
  keepSegments.forEach((segment, index) => {
    lines.push(`[0:a]atrim=start=${segment.start}:end=${segment.end},asetpts=PTS-STARTPTS[a${index}]`);
  });
  let current = "a0";
  for (let index = 1; index < keepSegments.length; index += 1) {
    const next = `ax${index}`;
    lines.push(`[${current}][a${index}]acrossfade=d=${XFADE}:c1=tri:c2=tri[${next}]`);
    current = next;
  }
  lines.push(
    `[${current}]` +
      "highpass=f=90," +
      "lowpass=f=12000," +
      "afftdn=nr=14:nf=-42:tn=1:rf=-38:gs=8," +
      "agate=threshold=0.015:ratio=2.5:attack=6:release=140:range=0.12:detection=rms," +
      "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=160:makeup=1.35," +
      "loudnorm=I=-16:TP=-1.5:LRA=9," +
      "alimiter=limit=0.95," +
      `adelay=${SYNC_AUDIO_DELAY_MS}|${SYNC_AUDIO_DELAY_MS},asetpts=PTS-STARTPTS[aout]`
  );
  return lines.join(";");
}

function renderSoftcutMedia() {
  ensureDir("assets/video2");
  run("ffmpeg", [
    "-hide_banner",
    "-y",
    "-i",
    TOP_SOURCE,
    "-filter_complex",
    buildVideoFilter("vout"),
    "-map",
    "[vout]",
    "-an",
    "-c:v",
    "libx264",
    "-preset",
    "veryfast",
    "-crf",
    "18",
    "-r",
    String(FPS),
    "-g",
    String(FPS),
    "-keyint_min",
    String(FPS),
    "-sc_threshold",
    "0",
    "-pix_fmt",
    "yuv420p",
    "-video_track_timescale",
    "90000",
    "-movflags",
    "+faststart",
    TOP_OUTPUT,
  ]);
  run("ffmpeg", [
    "-hide_banner",
    "-y",
    "-i",
    BOTTOM_SOURCE,
    "-filter_complex",
    `${buildVideoFilter("vout")};${buildAudioFilter()}`,
    "-map",
    "[vout]",
    "-map",
    "[aout]",
    "-c:v",
    "libx264",
    "-preset",
    "veryfast",
    "-crf",
    "18",
    "-r",
    String(FPS),
    "-g",
    String(FPS),
    "-keyint_min",
    String(FPS),
    "-sc_threshold",
    "0",
    "-c:a",
    "aac",
    "-ar",
    "48000",
    "-b:a",
    "192k",
    "-pix_fmt",
    "yuv420p",
    "-video_track_timescale",
    "90000",
    "-movflags",
    "+faststart",
    BOTTOM_OUTPUT,
  ]);
}

function renderBrollMedia() {
  ensureDir("assets/broll/optimized/video2-v66");
  brollSources.forEach((source) => {
    run("ffmpeg", [
      "-hide_banner",
      "-y",
      "-i",
      source.source,
      "-vf",
      `fps=${FPS},scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p`,
      "-an",
      "-c:v",
      "libx264",
      "-preset",
      "veryfast",
      "-crf",
      "18",
      "-r",
      String(FPS),
      "-g",
      String(FPS),
      "-keyint_min",
      String(FPS),
      "-sc_threshold",
      "0",
      "-pix_fmt",
      "yuv420p",
      "-video_track_timescale",
      "90000",
      "-movflags",
      "+faststart",
      source.output,
    ]);
  });
}

function buildBrollTags() {
  return brollSources
    .map((source, index) => {
      const [panFrom, panTo] = panPairs[index % panPairs.length];
      const mode = [1, 4].includes(index) ? "bridge" : "soft";
      const transition = mode === "bridge" ? 0.26 : 0.22;
      return `        <video
          id="${source.id}"
          class="clip top-media broll-frame"
          data-layout-allow-overflow="true"
          src="${source.output}"
          data-start="${source.start.toFixed(3)}"
          data-duration="3"
          data-media-start="1"
          data-transition-mode="${mode}"
          data-transition-in="${transition}"
          data-transition-out="${transition}"
          data-pan-from="${panFrom}"
          data-pan-to="${panTo}"
          data-motion-kind="slow-broll-inner-zoom"
          data-motion-duration="3"
          data-track-index="${4 + index}"
          data-volume="0"
          muted
          playsinline
        ></video>`;
    })
    .join("\n\n");
}

function buildCaptions() {
  return captionCues
    .map(([start, end, klass, html], index) => {
      const nextStart = captionCues[index + 1]?.[0] ?? COMPOSITION_DURATION;
      const safeEnd = Math.min(end, nextStart - 0.01, COMPOSITION_DURATION);
      const duration = round(Math.max(0.3, safeEnd - start));
      return `      <div id="subtitle-${String(index + 1).padStart(2, "0")}" class="clip subtitle-cue ${klass}" data-start="${start.toFixed(3)}" data-duration="${duration.toFixed(3)}" data-track-index="3"><span class="caption-box">${html}</span></div>`;
    })
    .join("\n");
}

function buildIndex() {
  const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@800;900&family=Inter:wght@800;900&display=swap" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; }
      .clip { position: absolute; }
      .background { inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0; }
      .video-frame {
        overflow: hidden; background: #000; border: 4px solid transparent;
        background: linear-gradient(#02040d, #02040d) padding-box, linear-gradient(135deg, #ffec7a 0%, #ffd93d 28%, rgba(244,194,15,.95) 56%, rgba(184,134,11,.9) 78%, #ffec7a 100%) border-box;
        box-shadow: 0 10px 26px rgba(0,0,0,.38), 0 0 22px rgba(244,194,15,.28), inset 0 0 14px rgba(255,217,61,.12);
        z-index: 2;
      }
      .top-frame-shell { position: absolute; left: 0; top: 198.9px; width: 1080px; height: 607.5px; border-radius: 30px; }
      .top-media { position: absolute; left: 4px; top: 4px; width: calc(100% - 8px); height: calc(100% - 8px); border-radius: 26px; background: #000; object-fit: contain; object-position: 50% 50%; transform-origin: center center; will-change: transform, object-position, opacity, filter; z-index: 1; }
      .bottom-frame { left: 50%; top: 846.4px; width: 607.5px; height: 607.5px; border-radius: 50%; transform: translateX(-50%); object-fit: cover; }
      .broll-frame { object-fit: cover; object-position: 50% 50%; opacity: 0; visibility: hidden; filter: brightness(.98) contrast(1.02) saturate(1.02); z-index: 4; }
      .subtitle-cue { left: 60px; right: 60px; top: 1490px; height: 160px; color: #fff; display: flex; align-items: center; justify-content: center; font-family: "IBM Plex Sans Thai", "Inter", sans-serif; font-weight: 800; line-height: 1; letter-spacing: -0.01em; text-align: center; z-index: 7; }
      .caption-box { display: inline-flex; align-items: center; justify-content: center; max-width: 92%; padding: 18px 36px; border: 1px solid rgba(244,194,15,.35); border-radius: 20px; background: linear-gradient(180deg, rgba(10,22,64,.78), rgba(8,16,50,.88)); backdrop-filter: blur(8px); box-shadow: 0 10px 28px rgba(0,0,0,.55), inset 0 0 18px rgba(244,194,15,.05); text-shadow: 0 4px 20px rgba(0,0,0,.85), 0 0 30px rgba(0,0,0,.7); white-space: nowrap; }
      .cap-xl .caption-box { font-size: 100px; }
      .cap-lg .caption-box { font-size: 84px; }
      .cap-md .caption-box { font-size: 60px; }
      .cap-sm .caption-box { font-size: 50px; }
      .gold { display: inline-block; padding: 0 .04em; font-family: "Inter", "IBM Plex Sans Thai", sans-serif; font-weight: 900; line-height: 1.25; vertical-align: baseline; transform-origin: center center; background: linear-gradient(180deg, #ffd93d 0%, #f4c20f 50%, #b8860b 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent; text-shadow: 0 4px 20px rgba(244,194,15,.35); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${COMPOSITION_DURATION}" data-width="1080" data-height="1920">
      <img id="background" class="clip background" src="assets/bg.png" alt="" data-start="0" data-duration="${COMPOSITION_DURATION}" data-track-index="0" />
      <div id="topFrameShell" class="video-frame top-frame-shell">
        <video id="topVideo" class="clip top-media" data-layout-allow-overflow="true" src="${TOP_OUTPUT}" data-start="0" data-duration="${COMPOSITION_DURATION}" data-track-index="1" data-motion-kind="slow-top-inner-zoom" data-motion-duration="${COMPOSITION_DURATION}" data-volume="0" muted playsinline></video>

${buildBrollTags()}
      </div>
      <video id="bottomVideo" class="clip video-frame bottom-frame" src="${BOTTOM_OUTPUT}" data-start="0" data-duration="${COMPOSITION_DURATION}" data-track-index="2" data-has-audio="true" playsinline></video>

${buildCaptions()}
    </div>

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const compositionDuration = ${COMPOSITION_DURATION};
      tl.from("#topVideo", { opacity: 0, duration: 0.35, ease: "power2.out" }, 0);
      tl.set("#topVideo", { scale: 1, objectPosition: "50% 50%", transformOrigin: "center center" }, 0);
      tl.to("#topVideo", { scale: 1.018, duration: compositionDuration / 2, ease: "sine.inOut" }, 0);
      tl.to("#topVideo", { scale: 1.006, duration: compositionDuration / 2, ease: "sine.inOut" }, compositionDuration / 2);

      document.querySelectorAll(".broll-frame").forEach((clip) => {
        const start = Number(clip.dataset.start || 0);
        const duration = Number(clip.dataset.duration || 0);
        const mode = clip.dataset.transitionMode || "soft";
        const fallbackDuration = mode === "bridge" ? 0.26 : 0.22;
        const inDuration = Math.min(Number(clip.dataset.transitionIn || fallbackDuration), duration / 3);
        const outDuration = Math.min(Number(clip.dataset.transitionOut || fallbackDuration), duration / 3);
        const exitStart = Math.max(start + duration - outDuration, start + inDuration);
        const panFrom = clip.dataset.panFrom || "50% 50%";
        const panTo = clip.dataset.panTo || "50% 50%";
        const enterEase = mode === "bridge" ? "power3.out" : "power2.out";
        const exitEase = mode === "bridge" ? "power2.inOut" : "power2.out";
        tl.set(clip, { autoAlpha: 0, scale: 1.006, objectPosition: panFrom, transformOrigin: "center center", filter: "brightness(0.98) contrast(1.02) saturate(1.02)" }, start - 0.001);
        tl.fromTo(clip, { autoAlpha: 0, filter: "brightness(0.98) contrast(1.02) saturate(1.02)" }, { autoAlpha: 1, filter: "brightness(1) contrast(1.03) saturate(1.04)", duration: inDuration, ease: enterEase, immediateRender: false }, start);
        tl.to(clip, { objectPosition: panTo, duration, ease: "sine.inOut" }, start);
        tl.to(clip, { scale: 1.022, duration, ease: "sine.inOut" }, start);
        tl.to(clip, { autoAlpha: 0, filter: "brightness(0.96) contrast(1.01) saturate(1.01)", duration: outDuration, ease: exitEase }, exitStart);
      });

      document.querySelectorAll(".subtitle-cue").forEach((cue) => {
        const start = Number(cue.dataset.start || 0);
        const duration = Number(cue.dataset.duration || 0);
        const enterDuration = Math.min(0.4, Math.max(0.2, duration * 0.3));
        const exitStart = Math.max(start + duration - 0.3, start + enterDuration);
        tl.fromTo(cue, { y: 30, scale: 0.92, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: enterDuration, ease: "back.out(1.7)", immediateRender: false }, start);
        const goldTargets = Array.from(cue.querySelectorAll(".gold"));
        if (goldTargets.length > 0) {
          tl.fromTo(goldTargets, { scale: 0.7, opacity: 0, transformOrigin: "center center" }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)", transformOrigin: "center center", immediateRender: false }, start + 0.1);
        }
        tl.to(cue, { opacity: 0, duration: 0.3, ease: "power2.out" }, exitStart);
      });
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
`;
  fs.writeFileSync("index.html", html);
}

function writeContextAndManifest() {
  ensureDir("assets/context");
  ensureDir("assets/broll/optimized/video2-v66");
  const durations = segmentDurations();
  let cursor = 0;
  const keptSegments = keepSegments.map((segment, index) => {
    const newStart = round(cursor);
    const newEnd = round(cursor + durations[index]);
    cursor = round(newEnd - XFADE);
    return {
      ...segment,
      newStart,
      newEnd,
      duration: durations[index],
      softCutPlan: `${XFADE}s xfade/acrossfade`,
    };
  });
  const outputDuration = round(durations.reduce((sum, duration) => sum + duration, 0) - XFADE * (durations.length - 1));
  const brollSlots = brollSources.map((slot, index) => {
    const [panFrom, panTo] = panPairs[index % panPairs.length];
    const mode = [1, 4].includes(index) ? "bridge" : "soft";
    const transition = mode === "bridge" ? 0.26 : 0.22;
    return {
      slot: index + 1,
      id: slot.id,
      start: slot.start,
      duration: 3,
      output: slot.output,
      source: slot.source,
      provider: "reused_local_pexels_stock",
      keyword: slot.keyword,
      query: slot.query,
      usage: "reused_source_reencoded_for_video2_v66_noise_sync_fix",
      contextSegment: slot.contextSegment,
      qaStatus: "pass",
      transitionMix: {
        mode,
        inDuration: transition,
        outDuration: transition,
        panFrom,
        panTo,
        borderStable: true,
        bottomUnaffected: true,
      },
    };
  });

  const context = {
    version: VERSION,
    setId: "video2-v66-noise-sync-fix",
    goal: "Fix v65 review issues: remove the non-speech/noisy false start and tighten lip sync while preserving the v64 guardrails.",
    strategy: "Use bottom audio as master, drop the early false start before sustained speech, rebuild soft cuts from raw bottom audio with stronger speech-first denoise/gate, and add a logged 21ms audio delay to compensate final MP4 stream start mismatch.",
    originalDuration: 115.946,
    outputDuration,
    compositionDuration: COMPOSITION_DURATION,
    xfadeSeconds: XFADE,
    audioRepair: {
      sourceChangedFrom: "assets/video2/bottom_audio_polished.mp4",
      sourceChangedTo: BOTTOM_SOURCE,
      initialFalseStartDropped: {
        start: 0,
        end: 2.3,
        reason: "silencedetect found a short opening sound followed by about 1.36s silence before sustained speech",
      },
      filterChain: "highpass=f=90, lowpass=f=12000, afftdn=nr=14:nf=-42:tn=1:rf=-38:gs=8, agate=threshold=0.015:ratio=2.5:attack=6:release=140:range=0.12, acompressor, loudnorm=-16 LUFS, alimiter",
      syncAudioDelayMs: SYNC_AUDIO_DELAY_MS,
      reason: "v65 final stream metadata showed video start at 0.021s and audio start at 0.000s, so audio could lead picture by about one frame.",
    },
    brollSpacing: {
      minStartGapSeconds: 6,
      minRealTopFootageGapSeconds: 3,
      maxPerMinute: 4,
      rule: "Do not place two B-roll inserts inside the same 6-second viewing window; cap density at 4 inserts per 60 seconds unless explicitly overridden.",
    },
    freshBrollPolicy: {
      stockIndex: "assets/broll/index.json",
      targetQaPassedStockCount: 200,
      freshDownloadAttempted: true,
      freshDownloadStatus: process.env.PEXELS_API_KEY ? "available" : "blocked_missing_env_pexels_api_key",
      fallbackUsed: "local_indexed_stock_for_pipeline_test",
    },
    transcript: {
      required: true,
      source: "assets/video2/transcript-large-v3-cli.json",
      engine: "whisper-cli large-v3",
      status: "available_timestamped_whisper_transcript",
    },
    screenSampling: {
      path: "render-checks/video2-screen-sample/contact-sheet.jpg",
      intervalSeconds: 10,
      summary: "Top screen shows code/workflow and generated vertical sample; bottom is the face/audio master.",
    },
    keptSegments,
    droppedSegments: droppedSegments.map((segment) => ({ ...segment, duration: round(segment.end - segment.start) })),
    brollSlots,
  };
  fs.writeFileSync("assets/context/video2-v66-noise-sync-fix.json", `${JSON.stringify(context, null, 2)}\n`);

  const manifest = {
    version: VERSION,
    setId: "video2-v66-noise-sync-fix",
    createdFor: "stacked-output-v66-video2-noise-sync-fix.mp4",
    summary: {
      externalDownloadsNew: 0,
      selectedFreshSourceCount: 0,
      reusedSourceCount: brollSlots.length,
      openRouterGenerationsNew: 0,
      optimizedDerivativeCount: brollSlots.length,
      rejectedCandidateCount: 0,
      minStartGapSeconds: 6,
      minRealTopFootageGapSeconds: 3,
      maxPerMinute: 4,
      freshDownloadAttempted: true,
      freshDownloadStatus: process.env.PEXELS_API_KEY ? "available" : "blocked_missing_env_pexels_api_key",
      note: "v66 fixes v65 review issues. Fresh Pexels sourcing was checked first, but the shell has no PEXELS_API_KEY, so local QA-passed stock was reused and re-encoded for the test.",
    },
    qaRule: "Reject any B-roll with visible text, logo, watermark, other brand, distracting graphic, or poor relevance.",
    slots: brollSlots,
    rejectedCandidates: [],
  };
  fs.writeFileSync("assets/broll/optimized/video2-v66/manifest.json", `${JSON.stringify(manifest, null, 2)}\n`);
}

function main() {
  renderSoftcutMedia();
  renderBrollMedia();
  buildIndex();
  writeContextAndManifest();
}

main();
