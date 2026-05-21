const API_KEY = process.env.PEXELS_API_KEY;

const VERSION = 35;
const CANDIDATES_PER_SLOT = Number(process.env.CANDIDATES_PER_SLOT || 3);
const INDEX_PATH = "assets/broll/index.json";
const OUTPUT_ROOT = `assets/broll/stock/pexels/test2-v${VERSION}-full`;

const REQUEST = {
  orientation: "landscape",
  size: "medium",
  locale: "en-US",
  per_page: "18",
};

const slots = [
  {
    slot: 1,
    start: 1.0,
    keyword: "ai_video_editing_workflow",
    beforeSpeech: "กำลังตัดต่อด้วย AI เพิ่งอัดคลิปเสร็จ",
    afterSpeech: "AI สามารถตัดต่อได้จริง",
    intent: "เปิดเรื่องว่า AI ช่วยตัดต่อวิดีโอได้",
    broadContext: "AI video editing workflow on a creator workstation",
    queries: ["creative video editing workstation", "AI technology workflow", "video editing computer setup"],
  },
  {
    slot: 2,
    start: 4.0,
    keyword: "ai_automation_video_editing",
    beforeSpeech: "AI สามารถตัดต่อได้แล้ว",
    afterSpeech: "คลิปแนะนำการตัดต่อด้วย AI",
    intent: "AI automation ทำงานแทนคน",
    broadContext: "automation and AI processing replacing repetitive editing work",
    queries: ["automation technology laptop", "artificial intelligence data", "digital technology workflow"],
  },
  {
    slot: 3,
    start: 8.4,
    keyword: "two_source_video_production",
    beforeSpeech: "มีฟุตสองตัว",
    afterSpeech: "หน้าคนและหน้าจอ",
    intent: "อธิบาย input สองวิดีโอคือ face + screen",
    broadContext: "multi-source video production and editing setup",
    queries: ["video production monitor", "content creator computer setup", "dual monitor video editing"],
  },
  {
    slot: 4,
    start: 12.4,
    keyword: "workflow_handoff_to_ai",
    beforeSpeech: "โยนให้ AI",
    afterSpeech: "ตัดต่อจริงๆ",
    intent: "ส่งงานให้ AI ทำงานต่อ",
    broadContext: "software workflow automation handoff to AI",
    queries: ["workflow automation laptop", "software automation computer", "developer workflow laptop"],
  },
  {
    slot: 5,
    start: 18.6,
    keyword: "ai_processing_workflow",
    beforeSpeech: "สั่ง AI ตัดต่อให้หน่อย",
    afterSpeech: "รอ 7-10 นาที ปล่อยเขาทำ",
    intent: "AI รับงานและประมวลผล",
    broadContext: "AI processing job and rendering workflow",
    queries: ["AI processing data visualization", "computer processing data", "server data processing"],
  },
  {
    slot: 6,
    start: 25.8,
    keyword: "audio_cleanup_dead_air",
    beforeSpeech: "เช็คไฟล์ก่อน",
    afterSpeech: "ตัด Dead Air และเสียงฟุ่มเฟือย",
    intent: "ลบความเงียบและเสียงไม่จำเป็น",
    broadContext: "audio cleanup waveform editing",
    queries: ["audio waveform editing", "sound editing computer", "audio production waveform"],
  },
  {
    slot: 7,
    start: 32.0,
    keyword: "audio_loudness_polish",
    beforeSpeech: "ตัดเสียงฟุ่มเฟือย",
    afterSpeech: "ปรับเสียงให้ดังเสมอกัน",
    intent: "audio polish และ loudness normalization",
    broadContext: "sound wave normalization and audio polish",
    queries: ["sound wave abstract", "audio mixer studio", "sound engineer mixing"],
  },
  {
    slot: 8,
    start: 38.8,
    keyword: "editing_layout_broll_insert",
    beforeSpeech: "วาง layout ดูภาพรวม",
    afterSpeech: "ใส่ B-roll",
    intent: "จัด layout และใส่ B-roll ในงานตัดต่อ",
    broadContext: "editing timeline and B-roll insertion",
    queries: ["video editing timeline", "video editor computer", "filmmaker editing workstation"],
  },
  {
    slot: 9,
    start: 42.8,
    keyword: "caption_overlay_design",
    beforeSpeech: "ทำ caption และ overlay",
    afterSpeech: "ตัวเหลืองเด่น",
    intent: "สร้าง caption/overlay ภาพประกอบ",
    broadContext: "digital captions and overlay motion graphics",
    queries: ["motion graphics animation", "digital abstract animation", "video graphics editing"],
  },
  {
    slot: 10,
    start: 48.0,
    keyword: "creator_final_export_thumbnail",
    beforeSpeech: "ใส่ intro/outro",
    afterSpeech: "ทำ thumbnail แล้วออกมาเป็นคลิป",
    intent: "ขั้นตอนสุดท้ายของ content production",
    broadContext: "content creator final edit export thumbnail",
    queries: ["content creator camera laptop", "video production computer", "creator studio editing"],
  },
];

if (!API_KEY) {
  console.error("PEXELS_API_KEY is missing.");
  process.exit(1);
}

function slug(input) {
  return input.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

async function readJson(path, fallback) {
  try {
    const fs = await import("node:fs/promises");
    return JSON.parse(await fs.readFile(path, "utf8"));
  } catch {
    return fallback;
  }
}

async function writeJson(path, data) {
  const fs = await import("node:fs/promises");
  await fs.mkdir(path.split("/").slice(0, -1).join("/"), { recursive: true });
  await fs.writeFile(path, `${JSON.stringify(data, null, 2)}\n`);
}

function collectUsedPexelsIds(...objects) {
  const ids = new Set();
  function visit(value) {
    if (!value || typeof value !== "object") return;
    if (value.provider === "pexels" && value.pexelsVideoId) ids.add(value.pexelsVideoId);
    if (value.pexelsVideoId) ids.add(value.pexelsVideoId);
    for (const child of Object.values(value)) {
      if (Array.isArray(child)) child.forEach(visit);
      else visit(child);
    }
  }
  objects.forEach(visit);
  return ids;
}

async function search(query) {
  const params = new URLSearchParams({ ...REQUEST, query });
  const response = await fetch(`https://api.pexels.com/v1/videos/search?${params}`, {
    headers: { Authorization: API_KEY },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}: ${JSON.stringify(body)}`);
  }
  return body.videos || [];
}

function scoreFile(file) {
  if (!file?.link || file.file_type !== "video/mp4") return -Infinity;
  const width = file.width || 0;
  const height = file.height || 0;
  const ratio = height ? width / height : 0;
  const ratioPenalty = Math.abs(ratio - 16 / 9) * 1200;
  const hdBonus = width >= 1280 && height >= 720 ? 2000 : 0;
  const tooLargePenalty = width > 1920 ? 400 : 0;
  return hdBonus + Math.min(width, 1920) - ratioPenalty - tooLargePenalty;
}

function bestFile(video) {
  return [...(video.video_files || [])].sort((a, b) => scoreFile(b) - scoreFile(a))[0];
}

async function download(url, output) {
  const fs = await import("node:fs/promises");
  await fs.mkdir(output.split("/").slice(0, -1).join("/"), { recursive: true });
  const response = await fetch(url);
  if (!response.ok) throw new Error(`download failed ${response.status} ${response.statusText}`);
  await fs.writeFile(output, new Uint8Array(await response.arrayBuffer()));
}

const index = await readJson(INDEX_PATH, { keywords: {} });
const v32Manifest = await readJson("assets/broll/optimized/test2-v32/manifest.json", {});
const v34Manifest = await readJson("assets/broll/optimized/test2-v34/manifest.json", {});
const usedIds = collectUsedPexelsIds(index, v32Manifest, v34Manifest);
const downloadedIds = new Set();
const manifest = {
  version: VERSION,
  setId: `test2-v${VERSION}-full-candidates`,
  createdAt: new Date().toISOString(),
  candidatesPerSlot: CANDIDATES_PER_SLOT,
  rule: "Fresh Pexels candidates for every slot using broad context keywords, not narrow literal transcript words.",
  slots: [],
};

for (const slot of slots) {
  const picked = [];
  for (const query of slot.queries) {
    if (picked.length >= CANDIDATES_PER_SLOT) break;
    console.log(`slot ${slot.slot}: search "${query}"`);
    const videos = await search(query);
    for (const video of videos) {
      if (picked.length >= CANDIDATES_PER_SLOT) break;
      if (video.duration < 3 || usedIds.has(video.id) || downloadedIds.has(video.id)) continue;
      const file = bestFile(video);
      if (!file || scoreFile(file) <= 0) continue;
      downloadedIds.add(video.id);
      const output = `${OUTPUT_ROOT}/slot-${String(slot.slot).padStart(2, "0")}/${slug(slot.keyword)}-${video.id}-${file.width}x${file.height}.mp4`;
      await download(file.link, output);
      console.log(`slot ${slot.slot}: downloaded ${output}`);
      picked.push({
        candidate: picked.length + 1,
        provider: "pexels",
        keyword: slot.keyword,
        query,
        path: output,
        pexelsVideoId: video.id,
        sourceUrl: video.url,
        photographer: video.user?.name || null,
        photographerUrl: video.user?.url || null,
        duration: video.duration,
        width: file.width,
        height: file.height,
        qaStatus: "needs_review",
      });
    }
  }
  manifest.slots.push({ ...slot, candidates: picked });
}

await writeJson(`${OUTPUT_ROOT}/candidates-manifest.json`, manifest);
console.log(`saved ${OUTPUT_ROOT}/candidates-manifest.json`);
