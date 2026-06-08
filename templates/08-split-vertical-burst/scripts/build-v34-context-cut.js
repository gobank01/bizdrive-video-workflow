import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const VERSION = 34;
const XFADE = 0.12;
const keepSegments = [
  {
    id: "hook",
    start: 0,
    end: 4.5,
    topic: "AI video editing hook",
    intent: "เปิดคลิปว่า AI กำลังตัดต่อจากไฟล์ที่เพิ่งอัด",
    screenContext: "หน้าจอ AI/workflow พร้อมไฟล์งานบน desktop",
    keepReason: "hook สำคัญ ทำให้คนดูเข้าใจทันทีว่า AI ตัดต่อให้",
  },
  {
    id: "two_sources_and_ai",
    start: 10.38,
    end: 21.48,
    topic: "two video sources and AI handoff",
    intent: "อธิบายว่ามีฟุตหน้าคนและหน้าจอ แล้วกำลังส่งให้ AI ตัดต่อ",
    screenContext: "หน้าจอ workflow/prompt ในเครื่องมือ AI",
    keepReason: "เป็นบริบทหลักของระบบตัดต่อ 2 วิดีโอ",
  },
  {
    id: "simple_prompt",
    start: 24.18,
    end: 28.14,
    topic: "simple edit request prompt",
    intent: "บอกว่าแค่โยนคำสั่งให้ AI ตัดต่อ",
    screenContext: "หน้าจอ prompt/workflow",
    keepReason: "ทำให้เห็นความง่ายของกระบวนการ",
  },
  {
    id: "ai_processing_steps",
    start: 33.24,
    end: 57.36,
    topic: "AI processing steps",
    intent: "AI รอประมวลผล เช็คไฟล์ ตัด Dead Air ปรับเสียง วาง layout และใส่ B-roll",
    screenContext: "หน้าจอ workflow panels และผลลัพธ์งานตัดต่อ",
    keepReason: "เป็นสาระหลักว่าระบบทำอะไรบ้าง",
  },
  {
    id: "captions_overlay",
    start: 63.22,
    end: 67.46,
    topic: "captions and overlay",
    intent: "ทำ caption และ overlay",
    screenContext: "หน้าจอรายละเอียด workflow/steps",
    keepReason: "เก็บฟีเจอร์สำคัญของคลิป final",
  },
  {
    id: "final_checks_and_cta",
    start: 72.42,
    end: 84.46,
    topic: "intro outro thumbnail export and CTA",
    intent: "เช็ครายละเอียด ใส่ intro/outro ทำ thumbnail แล้วสรุปว่าทำได้จริง",
    screenContext: "หน้าจอ workflow ขั้นท้าย",
    keepReason: "เก็บ conclusion และ call to action",
  },
];

const droppedSegments = [
  {
    start: 4.5,
    end: 10.38,
    reason: "พูดซ้ำว่าเป็นคลิปง่ายและ AI ตัดต่อได้ ซึ่ง hook และช่วงถัดไปบอกแล้ว",
  },
  {
    start: 21.48,
    end: 24.18,
    reason: "คำอธิบาย workflow เสร็จ/งานนิ่ง เป็นสะพานซ้ำก่อนเข้าคำสั่งจริง",
  },
  {
    start: 28.14,
    end: 33.24,
    reason: "AI ตอบรับงาน เป็นจังหวะรอที่ไม่จำเป็นต่อสาระ",
  },
  {
    start: 57.36,
    end: 63.22,
    reason: "filler และคำไม่ชัด ไม่เพิ่มสาระหลัก",
  },
  {
    start: 67.46,
    end: 72.42,
    reason: "คำซ้ำเรื่องสีเหลือง/แดงและ transition ก่อนเข้าขั้นตอน final",
  },
];

const oldCaptions = [
  [0, 2.2, "cap-md", 'กำลังตัดต่อด้วย <span class="gold">AI</span>'],
  [2.2, 4.5, "cap-lg", "อัดคลิปเสร็จแล้ว"],
  [10.38, 12.3, "cap-lg", "คลิปแนะนำ"],
  [12.3, 14.4, "cap-lg", '<span class="gold">ตัดต่อ</span>ได้จริง'],
  [14.4, 15.9, "cap-lg", 'มีฟุต <span class="gold">2 ตัว</span>'],
  [15.9, 17.46, "cap-lg", "หน้า + หน้าจอ"],
  [17.46, 19.5, "cap-lg", 'โยนให้ <span class="gold">AI</span>'],
  [19.5, 21.48, "cap-lg", "ตัดต่อจริงๆ"],
  [24.18, 26.2, "cap-lg", "โยนเข้าไปเลย"],
  [26.2, 28.14, "cap-lg", "ตัดต่อให้หน่อย"],
  [33.24, 35.4, "cap-lg", 'รอ <span class="gold">7-10 นาที</span>'],
  [35.4, 38.4, "cap-lg", "ปล่อยเขาทำ"],
  [38.4, 40.5, "cap-lg", "เช็คไฟล์ก่อน"],
  [40.5, 42.48, "cap-md", 'ตัด <span class="gold">Dead Air</span>'],
  [42.48, 44.6, "cap-md", "ตัดเสียงฟุ่มเฟือย"],
  [44.6, 46.68, "cap-lg", "อืม อ่ำ ออก"],
  [46.68, 48.5, "cap-xl", 'ปรับ<span class="gold">เสียง</span>'],
  [48.5, 50.22, "cap-lg", "ให้ดังเสมอกัน"],
  [50.22, 52.3, "cap-lg", 'วาง <span class="gold">layout</span>'],
  [52.3, 54.0, "cap-lg", "ดูภาพรวม"],
  [54.0, 57.36, "cap-lg", 'ใส่ <span class="gold">B-roll</span>'],
  [63.22, 65.4, "cap-lg", 'ทำ <span class="gold">caption</span>'],
  [65.4, 67.46, "cap-lg", 'ทำ <span class="gold">overlay</span>'],
  [72.42, 74.4, "cap-lg", 'ใส่ <span class="gold">intro</span>'],
  [74.4, 76.62, "cap-lg", 'ใส่ <span class="gold">outro</span>'],
  [76.62, 78.8, "cap-md", 'ทำ <span class="gold">thumbnail</span>'],
  [78.8, 81.66, "cap-lg", "ออกมาเป็นคลิป"],
  [81.66, 83.0, "cap-xl", '<span class="gold">สุดจริงๆ</span>'],
  [83.0, 84.46, "cap-lg", "ลองกันครับ"],
];

const brollSlots = [
  ["broll01", 1.2, "ai_video_editing_intro", "assets/broll/optimized/test2-v32/broll-01.mp4"],
  ["broll02", 6.4, "ai_editing_automation", "assets/broll/optimized/test2-v32/broll-02.mp4"],
  ["broll03", 9.0, "two_video_sources", "assets/broll/optimized/test2-v32/broll-03.mp4"],
  ["broll04", 12.2, "workflow_to_ai", "assets/broll/optimized/test2-v32/broll-04.mp4"],
  ["broll05", 20.0, "ai_processing_job", "assets/broll/optimized/test2-v32/broll-05.mp4"],
  ["broll06", 26.4, "dead_air_cleanup", "assets/broll/optimized/test2-v32/broll-06.mp4"],
  ["broll07", 34.0, "audio_polish_normalization", "assets/broll/optimized/test2-v32/broll-07.mp4"],
  ["broll08", 40.1, "broll_video_editing", "assets/broll/optimized/test2-v32/broll-08.mp4"],
  ["broll09", 44.0, "caption_overlay_graphics", "assets/broll/optimized/test2-v32/broll-09.mp4"],
  ["broll10", 48.2, "intro_outro_thumbnail_export", "assets/broll/optimized/test2-v32/broll-10.mp4"],
];

function round(n) {
  return Math.round(n * 1000) / 1000;
}

function buildTimeline() {
  let newStart = 0;
  return keepSegments.map((segment, index) => {
    const duration = segment.end - segment.start;
    const mapped = {
      ...segment,
      originalStart: segment.start,
      originalEnd: segment.end,
      newStart: round(newStart),
      newEnd: round(newStart + duration),
      duration: round(duration),
    };
    newStart += duration - (index < keepSegments.length - 1 ? XFADE : 0);
    return mapped;
  });
}

const timeline = buildTimeline();
const outputDuration = round(timeline.at(-1).newEnd);
const compositionDuration = 59.33;

function mapTime(originalTime) {
  for (const segment of timeline) {
    if (originalTime >= segment.originalStart - 0.001 && originalTime <= segment.originalEnd + 0.001) {
      return round(segment.newStart + (originalTime - segment.originalStart));
    }
  }
  return null;
}

function buildVideoFilter() {
  const trims = keepSegments
    .map((s, i) => `[0:v]trim=start=${s.start}:end=${s.end},setpts=PTS-STARTPTS,fps=30[v${i}]`)
    .join(";");
  let chain = "";
  let current = "v0";
  let currentDuration = keepSegments[0].end - keepSegments[0].start;
  for (let i = 1; i < keepSegments.length; i += 1) {
    const out = i === keepSegments.length - 1 ? "vx" : `vx${i}`;
    const offset = round(currentDuration - XFADE);
    chain += `;[${current}][v${i}]xfade=transition=fade:duration=${XFADE}:offset=${offset}[${out}]`;
    current = out;
    currentDuration += keepSegments[i].end - keepSegments[i].start - XFADE;
  }
  return `${trims}${chain};[${current}]fps=30,format=yuv420p[vout]`;
}

function buildAudioFilter() {
  const trims = keepSegments
    .map((s, i) => `[0:a]atrim=start=${s.start}:end=${s.end},asetpts=PTS-STARTPTS[a${i}]`)
    .join(";");
  let chain = "";
  let current = "a0";
  for (let i = 1; i < keepSegments.length; i += 1) {
    const out = i === keepSegments.length - 1 ? "ax" : `ax${i}`;
    chain += `;[${current}][a${i}]acrossfade=d=${XFADE}:c1=tri:c2=tri[${out}]`;
    current = out;
  }
  return `${trims}${chain};[${current}]anull[aout]`;
}

function run(cmd, args) {
  const result = spawnSync(cmd, args, { stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`${cmd} failed with status ${result.status}`);
  }
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function buildCaptions() {
  const mapped = oldCaptions.map(([start, end, klass, html], index) => {
    const newStart = mapTime(start);
    const newEnd = mapTime(end);
    if (newStart === null || newEnd === null) {
      throw new Error(`Caption cannot map: ${start}-${end}`);
    }
    return { index, newStart, newEnd, klass, html };
  });

  return mapped.map(({ index, newStart, newEnd, klass, html }, i) => {
    const nextStart = mapped[i + 1]?.newStart ?? compositionDuration;
    const safeEnd = Math.min(newEnd, nextStart - 0.01, compositionDuration);
    const duration = round(Math.max(0.3, safeEnd - newStart));
    const id = `subtitle-${String(index + 1).padStart(2, "0")}`;
    return `      <div id="${id}" class="clip subtitle-cue ${klass}" data-start="${newStart.toFixed(3)}" data-duration="${duration.toFixed(3)}" data-track-index="3"><span class="caption-box">${html}</span></div>`;
  });
}

function buildBrollTags() {
  return brollSlots
    .map(([id, start, keyword, src], index) => `      <video
        id="${id}"
        class="clip video-frame top-frame broll-frame"
        src="${src}"
        data-start="${start.toFixed(3)}"
        data-duration="3"
        data-media-start="1"
        data-track-index="${4 + index}"
        data-volume="0"
        muted
        playsinline
      ></video>`)
    .join("\n\n");
}

function updateIndex() {
  let html = fs.readFileSync("index.html", "utf8");
  html = html.replaceAll(/data-duration="(?:84\.5|59\.36|59\.33)"/g, `data-duration="${compositionDuration}"`);
  html = html.replaceAll("assets/top_test2_deadair_cut.mp4", "assets/top_test2_context60_softcut.mp4");
  html = html.replaceAll("assets/bottom_test2_audio_polished.mp4", "assets/bottom_test2_context60_audio_polished_softcut.mp4");
  html = html.replace(
    /      <video\n        id="broll01"[\s\S]*?\n\n      <video\n        id="bottomVideo"/,
    `${buildBrollTags()}\n\n      <video\n        id="bottomVideo"`,
  );
  html = html.replace(
    /      <div id="subtitle-01"[\s\S]*?\n\n    <\/div>\n\n    <script>/,
    `${buildCaptions().join("\n")}\n\n    </div>\n\n    <script>`,
  );
  fs.writeFileSync("index.html", html);
}

function writeContextIndex() {
  ensureDir("assets/context");
  const contextIndex = {
    version: VERSION,
    setId: "test2-v34-context60",
    goal: "Test context-aware reduction from 84.5s to about 60s while preserving core meaning.",
    strategy: "Keep meaning-bearing segments, remove repeated setup/filler/waiting bridges, and use 0.12s video/audio crossfades for soft cuts.",
    originalDuration: 84.5,
    outputDuration,
    xfadeSeconds: XFADE,
    screenSampling: {
      path: "render-checks/test2-v34-screen-sample/contact-sheet.jpg",
      intervalSeconds: 5,
      summary: "Top screen mostly shows AI/workflow panels, prompt/files, and step cards; use speech as primary context and screen as confirmation.",
    },
    keptSegments: timeline,
    droppedSegments: droppedSegments.map((segment) => ({
      ...segment,
      duration: round(segment.end - segment.start),
    })),
    brollSlots: brollSlots.map(([id, start, keyword, src]) => {
      const segment = timeline.find((s) => start >= s.newStart && start < s.newEnd);
      return {
        id,
        start,
        duration: 3,
        keyword,
        provider: "pexels",
        source: src,
        usage: "reused_v32_optimized_source",
        contextSegment: segment?.id ?? null,
        topic: segment?.topic ?? null,
        intent: segment?.intent ?? null,
        qaStatus: "pass",
      };
    }),
  };
  fs.writeFileSync("assets/context/test2-v34-context-index.json", `${JSON.stringify(contextIndex, null, 2)}\n`);

  ensureDir("assets/broll/optimized/test2-v34");
  const v32Manifest = JSON.parse(fs.readFileSync("assets/broll/optimized/test2-v32/manifest.json", "utf8"));
  const manifest = {
    version: VERSION,
    setId: "test2-v34-context60",
    createdFor: "stacked-output-v34-test2-context60-softcut-full-test.mp4",
    basedOn: "assets/broll/optimized/test2-v32/manifest.json",
    summary: {
      externalDownloadsNew: 0,
      selectedFreshSourceCount: 0,
      reusedSourceCount: brollSlots.length,
      openRouterGenerationsNew: 0,
      optimizedDerivativeCount: 0,
      rejectedCandidateCount: 0,
      note: "v34 reuses QA-passed v32 optimized B-roll but retimes slots using the context index.",
    },
    qaRule: v32Manifest.qaRule,
    slots: brollSlots.map(([id, start, keyword, src], index) => {
      const previous = v32Manifest.slots.find((slot) => slot.keyword === keyword);
      const segment = timeline.find((s) => start >= s.newStart && start < s.newEnd);
      return {
        slot: index + 1,
        id,
        start,
        duration: 3,
        output: src,
        source: previous?.source ?? src,
        provider: previous?.provider ?? "pexels",
        keyword,
        query: previous?.query ?? null,
        beforeSpeech: previous?.beforeSpeech ?? null,
        afterSpeech: previous?.afterSpeech ?? null,
        sourceUrl: previous?.sourceUrl ?? null,
        usage: "reused_v32_optimized_source",
        contextSegment: segment?.id ?? null,
        topic: segment?.topic ?? null,
        intent: segment?.intent ?? null,
        qaStatus: "pass",
        qaReason: null,
      };
    }),
  };
  fs.writeFileSync("assets/broll/optimized/test2-v34/manifest.json", `${JSON.stringify(manifest, null, 2)}\n`);
}

function main() {
  writeContextIndex();

  const videoFilter = buildVideoFilter();
  const audioFilter = buildAudioFilter();
  run("ffmpeg", [
    "-y",
    "-i",
    "assets/top_test2_deadair_cut.mp4",
    "-filter_complex",
    videoFilter,
    "-map",
    "[vout]",
    "-an",
    "-c:v",
    "libx264",
    "-preset",
    "veryfast",
    "-crf",
    "18",
    "-g",
    "30",
    "-keyint_min",
    "30",
    "-movflags",
    "+faststart",
    "assets/top_test2_context60_softcut.mp4",
  ]);

  run("ffmpeg", [
    "-y",
    "-i",
    "assets/bottom_test2_audio_polished.mp4",
    "-filter_complex",
    `${videoFilter};${audioFilter}`,
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
    "-g",
    "30",
    "-keyint_min",
    "30",
    "-c:a",
    "aac",
    "-b:a",
    "192k",
    "-movflags",
    "+faststart",
    "assets/bottom_test2_context60_audio_polished_softcut.mp4",
  ]);

  updateIndex();
  console.log(`Built v${VERSION} context cut at ${outputDuration}s`);
}

main();
