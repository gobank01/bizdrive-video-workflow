const API_KEY = process.env.PEXELS_API_KEY;

const VERSION = 32;
const CANDIDATES_PER_SLOT = Number(process.env.CANDIDATES_PER_SLOT || 3);
const INDEX_PATH = "assets/broll/index.json";
const OUTPUT_ROOT = `assets/broll/stock/pexels/test2-v${VERSION}`;

const REQUEST = {
  orientation: "landscape",
  size: "medium",
  locale: "en-US",
  per_page: "15",
};

const slots = [
  {
    slot: 1,
    start: 1.5,
    keyword: "ai_video_editing_intro",
    beforeSpeech: "เริ่มคลิป พูดว่ากำลังตัดต่อด้วย AI และเพิ่งอัดคลิปเสร็จ",
    afterSpeech: "อธิบายว่า AI สามารถตัดต่อได้แล้ว",
    intent: "เปิดเรื่อง AI video editing",
    queries: ["video editing computer", "artificial intelligence technology", "content creator editing"],
  },
  {
    slot: 2,
    start: 8,
    keyword: "ai_editing_automation",
    beforeSpeech: "วันนี้ AI สามารถตัดต่อได้แล้ว",
    afterSpeech: "เป็นคลิปแนะนำว่าสามารถตัดต่อได้",
    intent: "AI automation ทำงานแทนคน",
    queries: ["automation technology computer", "artificial intelligence automation", "computer processing data"],
  },
  {
    slot: 3,
    start: 14.5,
    keyword: "two_video_sources",
    beforeSpeech: "มีฟุตอยู่สองตัว",
    afterSpeech: "ฟุตหน้าพี่แบงค์ กับฟุตหน้าจอ",
    intent: "สอง source video: face + screen",
    queries: ["video production monitor", "dual monitor workspace", "content creator computer"],
  },
  {
    slot: 4,
    start: 22,
    keyword: "workflow_to_ai",
    beforeSpeech: "โยนเข้าไปให้ AI ตัดต่อจริง",
    afterSpeech: "ทำ workflow เสร็จแล้วก็สั่งตัดต่อ",
    intent: "workflow automation ส่งงานให้ AI",
    queries: ["workflow automation laptop", "software workflow computer", "developer automation laptop"],
  },
  {
    slot: 5,
    start: 31,
    keyword: "ai_processing_job",
    beforeSpeech: "AI รับงานต่อ",
    afterSpeech: "รอ 7-10 นาที ปล่อยเขาทำ",
    intent: "AI processing / rendering / waiting",
    queries: ["computer processing data", "digital processing technology", "server data processing"],
  },
  {
    slot: 6,
    start: 39,
    keyword: "dead_air_cleanup",
    beforeSpeech: "เขาจะเช็คไฟล์",
    afterSpeech: "มาตัด Dead Air ตัดเสียงฟุ่มเฟือย",
    intent: "audio cleanup / silence cut",
    queries: ["audio waveform editing", "sound editing computer", "audio mixing waveform"],
  },
  {
    slot: 7,
    start: 47,
    keyword: "audio_polish_normalization",
    beforeSpeech: "ตัดเสียงฟุ่มเฟือยออก",
    afterSpeech: "ปรับเสียงให้ดังขึ้นเสมอกัน",
    intent: "audio polish / mixer / loudness",
    queries: ["audio mixer sound", "recording studio mixing", "sound engineer mixer"],
  },
  {
    slot: 8,
    start: 56,
    keyword: "broll_video_editing",
    beforeSpeech: "วาง layout ดูภาพรวม",
    afterSpeech: "ใส่ B-roll ใส่ส่วนต่างๆ",
    intent: "video editing timeline / b-roll insert",
    queries: ["video editing timeline", "video editor computer", "filmmaker editing computer"],
  },
  {
    slot: 9,
    start: 66,
    keyword: "caption_overlay_graphics",
    beforeSpeech: "ทำ caption ทำ overlay",
    afterSpeech: "ตัวเหลืองเด่น เช็ครายละเอียด",
    intent: "caption overlay / motion graphics",
    queries: ["motion graphics animation", "digital animation graphics", "video graphics editing"],
  },
  {
    slot: 10,
    start: 76,
    keyword: "intro_outro_thumbnail_export",
    beforeSpeech: "ใส่ intro ใส่ outro",
    afterSpeech: "ทำ thumbnail แล้วออกมาเป็นคลิป",
    intent: "final export / content production",
    queries: ["video editing export", "content creator editing", "video production computer"],
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

function usedPexelsIds(index) {
  const ids = new Set();
  for (const entries of Object.values(index.keywords || {})) {
    for (const entry of entries) {
      if (entry.provider === "pexels" && entry.pexelsVideoId) ids.add(entry.pexelsVideoId);
    }
  }
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
  const ratioPenalty = Math.abs(ratio - 16 / 9) * 1000;
  const hdBonus = width >= 1280 && height >= 720 ? 2000 : 0;
  const tooLargePenalty = width > 1920 ? 500 : 0;
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
const usedIds = usedPexelsIds(index);
const downloadedIds = new Set();
const manifest = {
  version: VERSION,
  setId: `test2-context-v${VERSION}-candidates`,
  createdAt: new Date().toISOString(),
  candidatesPerSlot: CANDIDATES_PER_SLOT,
  rule: "Fresh download candidates for every B-roll slot, selected by before/after speech context.",
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
