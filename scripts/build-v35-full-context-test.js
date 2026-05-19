import fs from "node:fs";
import { spawnSync } from "node:child_process";

const VERSION = 35;
const XFADE = 0.12;
const COMPOSITION_DURATION = 59.33;

const keepSegments = [
  {
    id: "hook",
    start: 0,
    end: 4.5,
    speech: "อันนี้กำลังตัดต่อด้วย AI อยู่ทุกคน เมื่อกี้อัดคลิปเสร็จแล้ว",
    topic: "AI video editing hook",
    intent: "เปิดคลิปให้รู้ทันทีว่า AI กำลังช่วยตัดต่อจากไฟล์ที่เพิ่งอัด",
    importanceScore: 0.95,
    redundancyScore: 0.05,
    fillerScore: 0.05,
    screenContext: "หน้าจอ workflow/AI และไฟล์งานบน desktop",
    captionKeywords: ["AI", "ตัดต่อ"],
    brollKeyword: "AI video editing workflow",
    brollQuery: "creative video editing workstation",
    keepReason: "hook สำคัญ ทำให้คนดูเข้าใจ value proposition ทันที",
    cutRisk: "medium",
    softCutPlan: "0.12s xfade/acrossfade into two_sources_and_ai",
    brollCoverRecommended: true,
  },
  {
    id: "two_sources_and_ai",
    start: 10.38,
    end: 21.48,
    speech: "คลิปแนะนำว่าสามารถตัดต่อได้ มีฟุตสองตัว คือหน้าพี่แบงค์กับหน้าจอ แล้วโยนให้ AI ตัดต่อจริงๆ",
    topic: "two source video production and AI handoff",
    intent: "อธิบาย input หลักคือ face + screen และส่งให้ AI ทำงานต่อ",
    importanceScore: 0.94,
    redundancyScore: 0.1,
    fillerScore: 0.08,
    screenContext: "หน้าจอแสดง workflow/prompt และเครื่องมือ AI",
    captionKeywords: ["ฟุต 2 ตัว", "หน้า", "หน้าจอ", "AI"],
    brollKeyword: "two source video production",
    brollQuery: "video production monitor",
    keepReason: "เป็น setup สำคัญของ stacked-video workflow",
    cutRisk: "medium",
    softCutPlan: "0.12s xfade/acrossfade from hook and into simple_prompt",
    brollCoverRecommended: true,
  },
  {
    id: "simple_prompt",
    start: 24.18,
    end: 28.14,
    speech: "โยนเข้าไปเลยว่า ตัดต่อให้หน่อย แค่นี้เองทุกคน",
    topic: "simple edit request prompt",
    intent: "ทำให้เห็นว่าการสั่ง AI ตัดต่อง่ายมาก",
    importanceScore: 0.82,
    redundancyScore: 0.2,
    fillerScore: 0.12,
    screenContext: "หน้าจอ prompt/workflow",
    captionKeywords: ["ตัดต่อให้หน่อย"],
    brollKeyword: "workflow handoff to AI",
    brollQuery: "workflow automation laptop",
    keepReason: "เก็บ promise ว่างานใช้ prompt สั้นๆ ก็เริ่มได้",
    cutRisk: "high",
    softCutPlan: "0.12s xfade/acrossfade into AI processing; B-roll should cover the jump",
    brollCoverRecommended: true,
  },
  {
    id: "ai_processing_steps",
    start: 33.24,
    end: 57.36,
    speech: "รอเจ็ดถึงสิบนาที ปล่อยเขาทำ เช็คไฟล์ ตัด Dead Air ตัดเสียงฟุ่มเฟือย ปรับเสียง วาง layout และใส่ B-roll",
    topic: "AI processing steps",
    intent: "อธิบายขั้นตอนหลักที่ AI ทำให้ครบตั้งแต่ cleanup ถึง layout/B-roll",
    importanceScore: 0.98,
    redundancyScore: 0.08,
    fillerScore: 0.18,
    screenContext: "หน้าจอ workflow panels และ step cards",
    captionKeywords: ["7-10 นาที", "Dead Air", "เสียง", "layout", "B-roll"],
    brollKeyword: "AI processing workflow",
    brollQuery: "AI processing data visualization",
    keepReason: "เป็นสาระหลักของคลิป ต้องเก็บครบ",
    cutRisk: "low",
    softCutPlan: "0.12s xfade/acrossfade from simple_prompt and into captions_overlay",
    brollCoverRecommended: true,
  },
  {
    id: "captions_overlay",
    start: 63.22,
    end: 67.46,
    speech: "จากนั้นก็มาทำ caption ทำ overlay",
    topic: "captions and overlay design",
    intent: "ย้ำ feature สำคัญของ output วิดีโอ",
    importanceScore: 0.82,
    redundancyScore: 0.15,
    fillerScore: 0.2,
    screenContext: "หน้าจอ workflow/step details",
    captionKeywords: ["caption", "overlay"],
    brollKeyword: "caption overlay design",
    brollQuery: "motion graphics animation",
    keepReason: "เชื่อมจาก processing ไป output styling",
    cutRisk: "medium",
    softCutPlan: "0.12s xfade/acrossfade into final_checks_and_cta",
    brollCoverRecommended: true,
  },
  {
    id: "final_checks_and_cta",
    start: 72.42,
    end: 84.46,
    speech: "เช็ครายละเอียด ใส่ intro/outro ทำ thumbnail ออกมาเป็นคลิปจริง โลกเปลี่ยนไปเยอะ อยากให้ทุกคนได้ลอง",
    topic: "final export thumbnail and CTA",
    intent: "ปิดท้ายว่าระบบสร้างวิดีโอครบจน export และชวนลอง",
    importanceScore: 0.9,
    redundancyScore: 0.08,
    fillerScore: 0.1,
    screenContext: "หน้าจอ workflow ขั้นท้ายและรายละเอียดงาน",
    captionKeywords: ["intro", "outro", "thumbnail", "สุดจริงๆ"],
    brollKeyword: "creator final export thumbnail",
    brollQuery: "content creator camera laptop",
    keepReason: "ต้องมี conclusion/CTA เพื่อปิดคลิป",
    cutRisk: "medium",
    softCutPlan: "0.12s xfade/acrossfade from captions_overlay",
    brollCoverRecommended: true,
  },
];

const droppedSegments = [
  {
    start: 4.5,
    end: 10.38,
    speech: "จะเป็นคลิปแบบง่ายๆ วันนี้ AI สามารถตัดต่อได้แล้ว",
    topic: "repeated AI can edit setup",
    dropReason: "ซ้ำกับ hook และ setup ถัดไป",
    importanceScore: 0.45,
    redundancyScore: 0.9,
    fillerScore: 0.35,
    cutRisk: "medium",
  },
  {
    start: 21.48,
    end: 24.18,
    speech: "พอทำ workflow เสร็จเรียบร้อยแล้ว มันนิ่งละ",
    topic: "workflow bridge",
    dropReason: "bridge ซ้ำก่อนเข้าคำสั่งจริง",
    importanceScore: 0.35,
    redundancyScore: 0.75,
    fillerScore: 0.35,
    cutRisk: "medium",
  },
  {
    start: 28.14,
    end: 33.24,
    speech: "AI ตอบรับว่าโอเค เดี๋ยวทำการตัดต่อให้",
    topic: "AI accepts the job",
    dropReason: "ช่วงรับงาน/รอ ไม่เพิ่มสาระเท่าขั้นตอนที่ AI ทำจริง",
    importanceScore: 0.4,
    redundancyScore: 0.72,
    fillerScore: 0.45,
    cutRisk: "high",
  },
  {
    start: 57.36,
    end: 63.22,
    speech: "ใส่ส่วนต่างๆ ใครเคยใช้พวก...ก็ นั่นแหละ",
    topic: "unclear filler bridge",
    dropReason: "คำไม่ชัดและ filler สูง",
    importanceScore: 0.2,
    redundancyScore: 0.55,
    fillerScore: 0.9,
    cutRisk: "low",
  },
  {
    start: 67.46,
    end: 72.42,
    speech: "ทำตัวเหลืองเหลืองแดงแดง จากนั้นสุดท้ายก็...",
    topic: "repeated visual styling bridge",
    dropReason: "ซ้ำกับ caption/overlay และเป็น transition ก่อน final checks",
    importanceScore: 0.32,
    redundancyScore: 0.78,
    fillerScore: 0.55,
    cutRisk: "medium",
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

const selectedCandidates = [
  { slot: 1, candidate: 2 },
  { slot: 2, candidate: 2 },
  { slot: 3, candidate: 3 },
  { slot: 4, candidate: 3 },
  { slot: 5, candidate: 3 },
  { slot: 6, sourceSlot: 7, candidate: 2, keyword: "audio_cleanup_dead_air" },
  { slot: 7, candidate: 1 },
  { slot: 8, candidate: 2 },
  { slot: 9, candidate: 1 },
  { slot: 10, candidate: 3 },
];

const panPairs = [
  ["49% 50%", "51% 50%"],
  ["50% 49%", "50% 51%"],
  ["51% 50%", "49% 50%"],
  ["50% 51%", "50% 49%"],
];

const brollTiming = [
  { id: "broll01", start: 1.0, contextSegment: "hook", coverCut: null },
  { id: "broll02", start: 3.9, contextSegment: "hook_to_two_sources", coverCut: 4.38 },
  { id: "broll03", start: 8.4, contextSegment: "two_sources_and_ai", coverCut: null },
  { id: "broll04", start: 14.8, contextSegment: "two_sources_to_prompt", coverCut: 15.36 },
  { id: "broll05", start: 18.7, contextSegment: "prompt_to_processing", coverCut: 19.2 },
  { id: "broll06", start: 25.9, contextSegment: "ai_processing_steps", coverCut: null },
  { id: "broll07", start: 32.7, contextSegment: "ai_processing_steps", coverCut: null },
  { id: "broll08", start: 39.8, contextSegment: "ai_processing_steps", coverCut: null },
  { id: "broll09", start: 42.7, contextSegment: "processing_to_captions", coverCut: 43.2 },
  { id: "broll10", start: 46.9, contextSegment: "captions_to_final", coverCut: 47.32 },
].map((timing, index) => {
  const isBridge = Boolean(timing.coverCut);
  const [panFrom, panTo] = panPairs[index % panPairs.length];
  return {
    ...timing,
    transitionMode: isBridge ? "bridge" : "soft",
    transitionIn: isBridge ? 0.26 : 0.22,
    transitionOut: isBridge ? 0.26 : 0.22,
    panFrom,
    panTo,
  };
});

function round(n) {
  return Math.round(n * 1000) / 1000;
}

function run(cmd, args) {
  const result = spawnSync(cmd, args, { stdio: "inherit" });
  if (result.status !== 0) throw new Error(`${cmd} failed with status ${result.status}`);
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
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

function candidateForSlot(slot, candidate) {
  const manifest = JSON.parse(fs.readFileSync("assets/broll/stock/pexels/test2-v35-full/candidates-manifest.json", "utf8"));
  return manifest.slots.find((item) => item.slot === slot).candidates.find((item) => item.candidate === candidate);
}

function optimizeBroll() {
  ensureDir("assets/broll/optimized/test2-v35");
  return selectedCandidates.map(({ slot, sourceSlot, candidate, keyword }) => {
    const source = candidateForSlot(sourceSlot || slot, candidate);
    const output = `assets/broll/optimized/test2-v35/broll-${String(slot).padStart(2, "0")}.mp4`;
    run("ffmpeg", [
      "-y",
      "-i",
      source.path,
      "-an",
      "-c:v",
      "libx264",
      "-preset",
      "veryfast",
      "-crf",
      "18",
      "-r",
      "30",
      "-g",
      "30",
      "-keyint_min",
      "30",
      "-vf",
      "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
      "-pix_fmt",
      "yuv420p",
      "-movflags",
      "+faststart",
      output,
    ]);
    return { ...source, slot, keyword: keyword || source.keyword, sourceSlot: sourceSlot || slot, output };
  });
}

function buildCaptions() {
  const mapped = oldCaptions.map(([start, end, klass, html], index) => {
    const newStart = mapTime(start);
    const newEnd = mapTime(end);
    if (newStart === null || newEnd === null) throw new Error(`Caption cannot map: ${start}-${end}`);
    return { index, newStart, newEnd, klass, html };
  });

  return mapped.map(({ index, newStart, newEnd, klass, html }, i) => {
    const nextStart = mapped[i + 1]?.newStart ?? COMPOSITION_DURATION;
    const safeEnd = Math.min(newEnd, nextStart - 0.01, COMPOSITION_DURATION);
    const duration = round(Math.max(0.3, safeEnd - newStart));
    const id = `subtitle-${String(index + 1).padStart(2, "0")}`;
    return `      <div id="${id}" class="clip subtitle-cue ${klass}" data-start="${newStart.toFixed(3)}" data-duration="${duration.toFixed(3)}" data-track-index="3"><span class="caption-box">${html}</span></div>`;
  });
}

function buildBrollTags() {
  return brollTiming
    .map((timing, index) => `      <video
        id="${timing.id}"
        class="clip video-frame top-frame broll-frame"
        src="assets/broll/optimized/test2-v35/broll-${String(index + 1).padStart(2, "0")}.mp4"
        data-start="${timing.start.toFixed(3)}"
        data-duration="3"
        data-media-start="1"
        data-transition-mode="${timing.transitionMode}"
        data-transition-in="${timing.transitionIn}"
        data-transition-out="${timing.transitionOut}"
        data-pan-from="${timing.panFrom}"
        data-pan-to="${timing.panTo}"
        data-track-index="${4 + index}"
        data-volume="0"
        muted
        playsinline
      ></video>`)
    .join("\n\n");
}

function updateIndex() {
  let html = fs.readFileSync("index.html", "utf8");
  html = html.replaceAll(/data-duration="(?:84\.5|59\.36|59\.33)"/g, `data-duration="${COMPOSITION_DURATION}"`);
  html = html.replaceAll(/assets\/top_test2_(?:deadair_cut|context60_softcut|context60_v35_softcut)\.mp4/g, "assets/top_test2_context60_v35_softcut.mp4");
  html = html.replaceAll(
    /assets\/bottom_test2_(?:audio_polished|context60_audio_polished_softcut|context60_v35_audio_polished_softcut)\.mp4/g,
    "assets/bottom_test2_context60_v35_audio_polished_softcut.mp4",
  );
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

function writeContextAndManifest(selected) {
  ensureDir("assets/context");
  const contextIndex = {
    version: VERSION,
    setId: "test2-v35-full-context",
    goal: "Full v35 test: target about 60s, Medium cut, Full context index, fresh B-roll, B-roll cover for jump cuts.",
    strategy: "Use transcript/audio as primary context, screen sampling as confirmation, remove repeated/filler/bridge segments, soft cut all content cuts, and retime B-roll over key jumps.",
    originalDuration: 84.5,
    outputDuration,
    compositionDuration: COMPOSITION_DURATION,
    xfadeSeconds: XFADE,
    screenSampling: {
      path: "render-checks/test2-v34-screen-sample/contact-sheet.jpg",
      intervalSeconds: 5,
      extraAroundCutAndBrollSeconds: 2,
      summary: "Top screen shows AI/workflow panels, prompt/files, step cards, and export-related workflow; transcript remains primary context.",
    },
    keptSegments: timeline,
    droppedSegments: droppedSegments.map((segment) => ({ ...segment, duration: round(segment.end - segment.start) })),
    brollSlots: brollTiming.map((timing, index) => {
      const source = selected[index];
      const segment = timeline.find((item) => timing.start >= item.newStart && timing.start < item.newEnd);
      return {
        slot: index + 1,
        id: timing.id,
        start: timing.start,
        duration: 3,
        keyword: source.keyword,
        query: source.query,
        provider: "pexels",
        source: source.path,
        output: source.output,
        contextSegment: timing.contextSegment,
        topic: segment?.topic ?? null,
        intent: segment?.intent ?? null,
        coverCut: timing.coverCut,
        brollCoverRecommended: Boolean(timing.coverCut),
        transitionMix: {
          mode: timing.transitionMode,
          inDuration: timing.transitionIn,
          outDuration: timing.transitionOut,
          panFrom: timing.panFrom,
          panTo: timing.panTo,
        },
        qaStatus: "pass",
      };
    }),
  };
  fs.writeFileSync("assets/context/test2-v35-full-context-index.json", `${JSON.stringify(contextIndex, null, 2)}\n`);

  const candidateManifest = JSON.parse(fs.readFileSync("assets/broll/stock/pexels/test2-v35-full/candidates-manifest.json", "utf8"));
  const selectedPaths = new Set(selected.map((item) => item.path));
  const rejectedCandidates = candidateManifest.slots.flatMap((slot) =>
    slot.candidates
      .filter((candidate) => !selectedPaths.has(candidate.path))
      .map((candidate) => ({
        slot: slot.slot,
        candidate: candidate.candidate,
        keyword: candidate.keyword,
        path: candidate.path,
        pexelsVideoId: candidate.pexelsVideoId,
        qaStatus: "rejected",
        qaReason: "not_best_context_or_visual_qa",
      })),
  );
  const manifest = {
    version: VERSION,
    setId: "test2-v35-full-context",
    createdFor: "stacked-output-v35-test2-full-context-softcut-broll-full-test.mp4",
    summary: {
      externalDownloadsNew: candidateManifest.slots.reduce((sum, slot) => sum + slot.candidates.length, 0),
      selectedFreshSourceCount: selected.length,
      reusedSourceCount: 0,
      openRouterGenerationsNew: 0,
      optimizedDerivativeCount: selected.length,
      rejectedCandidateCount: rejectedCandidates.length,
      note: "Full v35 test uses fresh Pexels sources selected from broad context keywords and retimed to cover important jump cuts.",
    },
    qaRule: "Reject any B-roll with visible text, logo, watermark, other brand, distracting graphic, or poor relevance.",
    slots: brollTiming.map((timing, index) => {
      const source = selected[index];
      return {
        slot: index + 1,
        id: timing.id,
        start: timing.start,
        duration: 3,
        output: source.output,
        source: source.path,
        provider: "pexels",
        keyword: source.keyword,
        query: source.query,
        beforeSpeech: candidateManifest.slots.find((item) => item.slot === source.slot)?.beforeSpeech ?? null,
        afterSpeech: candidateManifest.slots.find((item) => item.slot === source.slot)?.afterSpeech ?? null,
        broadContext: candidateManifest.slots.find((item) => item.slot === source.slot)?.broadContext ?? null,
        pexelsVideoId: source.pexelsVideoId,
        sourceUrl: source.sourceUrl,
        photographer: source.photographer,
        usage: "fresh_download_reencoded",
        selectedCandidate: source.candidate,
        coverCut: timing.coverCut,
        contextSegment: timing.contextSegment,
        transitionMix: {
          mode: timing.transitionMode,
          inDuration: timing.transitionIn,
          outDuration: timing.transitionOut,
          panFrom: timing.panFrom,
          panTo: timing.panTo,
          borderStable: true,
        },
        qaStatus: "pass",
        qaReason: null,
      };
    }),
    rejectedCandidates,
  };
  fs.writeFileSync("assets/broll/optimized/test2-v35/manifest.json", `${JSON.stringify(manifest, null, 2)}\n`);
}

function buildSoftCutMedia() {
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
    "assets/top_test2_context60_v35_softcut.mp4",
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
    "assets/bottom_test2_context60_v35_audio_polished_softcut.mp4",
  ]);
}

function main() {
  const selected = optimizeBroll();
  writeContextAndManifest(selected);
  buildSoftCutMedia();
  updateIndex();
  console.log(`Built v${VERSION} full context test at ${COMPOSITION_DURATION}s`);
}

main();
