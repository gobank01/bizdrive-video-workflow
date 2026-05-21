const API_KEY = process.env.PEXELS_API_KEY;
const INDEX_PATH = "assets/broll/index.json";
const LIBRARY_VERSION = 26;

const DEFAULT_REQUEST = {
  orientation: "landscape",
  size: "medium",
  locale: "en-US",
  per_page: 8,
};

const BROLL_SEARCHES = [
  {
    keyword: "stock_market",
    title: "Stock market screens",
    query: "stock market trading screen",
    tags: ["stock", "market", "trading", "finance"],
  },
  {
    keyword: "investment_money",
    title: "Investment money",
    query: "investment money finance",
    tags: ["investment", "money", "dividend", "finance"],
  },
  {
    keyword: "business_dashboard",
    title: "Business dashboard",
    query: "business analytics dashboard",
    tags: ["business", "dashboard", "data", "analytics"],
  },
  {
    keyword: "coding_workflow",
    title: "Coding workflow",
    query: "coding laptop workflow",
    tags: ["coding", "workflow", "prompt", "app"],
  },
  {
    keyword: "wall_street",
    title: "Wall Street finance",
    query: "wall street finance",
    tags: ["wall-street", "usa", "stocks", "finance"],
  },
];

if (!API_KEY) {
  console.error("PEXELS_API_KEY is missing. Export it before running this script.");
  process.exit(1);
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

async function exists(path) {
  try {
    const fs = await import("node:fs/promises");
    await fs.access(path);
    return true;
  } catch {
    return false;
  }
}

function slug(input) {
  return input.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

async function searchVideos(search) {
  const params = new URLSearchParams({
    query: search.query,
    orientation: DEFAULT_REQUEST.orientation,
    size: DEFAULT_REQUEST.size,
    locale: DEFAULT_REQUEST.locale,
    per_page: String(DEFAULT_REQUEST.per_page),
  });

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
  if (!file.link || file.file_type !== "video/mp4") return -Infinity;
  const width = file.width || 0;
  const height = file.height || 0;
  const ratio = height ? width / height : 0;
  const ratioPenalty = Math.abs(ratio - 16 / 9) * 1000;
  const hdBonus = width >= 1280 && height >= 720 ? 2000 : 0;
  const tooLargePenalty = width > 1920 ? 500 : 0;
  return hdBonus + Math.min(width, 1920) - ratioPenalty - tooLargePenalty;
}

function pickBestVideo(search, videos, usedIds) {
  const candidates = videos
    .filter((video) => video.duration >= 3 && !usedIds.has(video.id))
    .map((video) => {
      const file = [...video.video_files].sort((a, b) => scoreFile(b) - scoreFile(a))[0];
      return { video, file, score: scoreFile(file) };
    })
    .filter((item) => item.file && item.score > 0)
    .sort((a, b) => b.score - a.score);

  if (candidates.length === 0) {
    throw new Error(`no usable Pexels video found for ${search.keyword}`);
  }

  return candidates[0];
}

async function download(url, output) {
  const fs = await import("node:fs/promises");
  await fs.mkdir(output.split("/").slice(0, -1).join("/"), { recursive: true });

  const response = await fetch(url);
  if (!response.ok) throw new Error(`download failed ${response.status} ${response.statusText}`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  await fs.writeFile(output, bytes);
}

function makeEntry(search, video, file, output) {
  return {
    id: `v${LIBRARY_VERSION}-pexels-${search.keyword}-${video.id}`,
    version: LIBRARY_VERSION,
    provider: "pexels",
    keyword: search.keyword,
    title: search.title,
    query: search.query,
    tags: search.tags,
    path: output,
    status: "downloaded",
    pexelsVideoId: video.id,
    sourceUrl: video.url,
    photographer: video.user?.name || null,
    photographerUrl: video.user?.url || null,
    previewImage: video.image,
    duration: video.duration,
    width: file.width,
    height: file.height,
    fileType: file.file_type,
    aspectRatio: "16:9 landscape",
    usableSeconds: 3,
    estimatedCostUsd: 0,
    attributionRequired: false,
    createdAt: new Date().toISOString(),
  };
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

function findReusableEntry(index, search) {
  const entries = index.keywords?.[search.keyword] || [];
  return entries.find((entry) => entry.provider === "pexels" && entry.path);
}

function upsertIndexEntry(index, entry) {
  index.version = LIBRARY_VERSION;
  index.updatedAt = new Date().toISOString();
  index.rules = {
    reuseBeforeGenerate: true,
    matchByKeywordAndTags: true,
    pexelsBeforeOpenRouter: true,
    maxInsertSeconds: 3,
    preferredAspectRatio: "16:9",
    preferredResolution: "720p",
    generateAudio: false,
  };
  index.providers = {
    pexels: {
      role: "primary-stock-search",
      cost: "free-with-api-limits",
      attributionRequired: false,
    },
    openrouter: {
      role: "fallback-text-to-video-generation",
    },
  };
  index.keywords ||= {};
  index.keywords[entry.keyword] ||= [];

  const entries = index.keywords[entry.keyword];
  const currentIndex = entries.findIndex((item) => item.id === entry.id);
  if (currentIndex >= 0) {
    entries[currentIndex] = { ...entries[currentIndex], ...entry };
  } else {
    entries.unshift(entry);
  }
}

const index = await readJson(INDEX_PATH, {
  version: LIBRARY_VERSION,
  updatedAt: null,
  rules: {},
  providers: {},
  keywords: {},
});

const usedIds = usedPexelsIds(index);

for (const search of BROLL_SEARCHES) {
  const reusable = findReusableEntry(index, search);
  if (process.env.FORCE_BROLL !== "1" && reusable && (await exists(reusable.path))) {
    console.log(`reuse ${search.keyword}: ${reusable.path}`);
    continue;
  }

  console.log(`search ${search.keyword}: ${search.query}`);
  const videos = await searchVideos(search);
  const { video, file } = pickBestVideo(search, videos, usedIds);
  usedIds.add(video.id);

  const output = `assets/broll/stock/pexels/${search.keyword}/${slug(search.keyword)}-${video.id}-${file.width}x${file.height}.mp4`;
  if (process.env.FORCE_BROLL !== "1" && (await exists(output))) {
    console.log(`exists ${output}`);
  } else {
    await download(file.link, output);
    console.log(`downloaded ${output}`);
  }

  upsertIndexEntry(index, makeEntry(search, video, file, output));
  await writeJson(INDEX_PATH, index);
}
