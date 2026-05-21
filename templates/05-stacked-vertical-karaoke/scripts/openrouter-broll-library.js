const API_KEY = process.env.OPENROUTER_API_KEY;

const MODEL_CONFIGS = [
  {
    model: "google/veo-3.1-lite",
    label: "google-veo-3-1-lite",
    pricePerSecondUsd: 0.05,
  },
  {
    model: "kwaivgi/kling-v3.0-std",
    label: "kwaivgi-kling-v3-0-std",
    pricePerSecondUsd: 0.126,
  },
];

const TEST_CLIPS = [
  {
    keyword: "ai_stock_dashboard",
    title: "AI stock dashboard",
    tags: ["ai", "stock", "dashboard", "finance", "blue-gold"],
    prompt:
      "cinematic 16:9 stock b-roll of an AI stock analysis dashboard, glowing financial charts, premium blue and gold finance lighting, smooth camera movement, no text, no logos, no people",
  },
];

const REQUEST_DEFAULTS = {
  aspect_ratio: "16:9",
  duration: 4,
  resolution: "720p",
  generate_audio: false,
};

const INDEX_PATH = "assets/broll/index.json";

if (!API_KEY) {
  console.error("OPENROUTER_API_KEY is missing. Export it before running this script.");
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

async function submit(model, prompt) {
  const response = await fetch("https://openrouter.ai/api/v1/videos", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://bizdrive.local",
      "X-Title": "Bizdrive B-roll Library",
    },
    body: JSON.stringify({
      model,
      prompt,
      ...REQUEST_DEFAULTS,
    }),
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}: ${JSON.stringify(body)}`);
  }
  return body;
}

async function poll(pollingUrl) {
  for (let attempt = 1; attempt <= 90; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 10000));
    const response = await fetch(pollingUrl, {
      headers: { Authorization: `Bearer ${API_KEY}` },
    });
    const body = await response.json();
    console.log(`poll ${attempt}: ${body.status}`);

    if (body.status === "completed") return body;
    if (["failed", "cancelled", "expired"].includes(body.status)) {
      throw new Error(`video job ${body.status}: ${JSON.stringify(body.error || body)}`);
    }
  }
  throw new Error("video job timed out");
}

async function download(url, output) {
  const fs = await import("node:fs/promises");
  await fs.mkdir(output.split("/").slice(0, -1).join("/"), { recursive: true });

  const response = await fetch(url, {
    headers: url.includes("openrouter.ai") ? { Authorization: `Bearer ${API_KEY}` } : {},
  });
  if (!response.ok) throw new Error(`download failed ${response.status} ${response.statusText}`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  await fs.writeFile(output, bytes);
}

function makeOutputPath(modelConfig, clip) {
  return `assets/broll/model-tests/v24-${modelConfig.label}-${clip.keyword}.mp4`;
}

function makeIndexEntry(modelConfig, clip, output, jobId) {
  const requestedSeconds = REQUEST_DEFAULTS.duration;
  return {
    id: `v24-${modelConfig.label}-${clip.keyword}`,
    version: 24,
    keyword: clip.keyword,
    title: clip.title,
    tags: clip.tags,
    model: modelConfig.model,
    path: output,
    prompt: clip.prompt,
    status: "generated",
    aspectRatio: REQUEST_DEFAULTS.aspect_ratio,
    resolution: REQUEST_DEFAULTS.resolution,
    requestedSeconds,
    usableSeconds: 3,
    generateAudio: REQUEST_DEFAULTS.generate_audio,
    estimatedCostUsd: Number((requestedSeconds * modelConfig.pricePerSecondUsd).toFixed(3)),
    pricePerSecondUsd: modelConfig.pricePerSecondUsd,
    openRouterJobId: jobId,
    createdAt: new Date().toISOString(),
  };
}

function upsertIndexEntry(index, entry) {
  index.version = 24;
  index.updatedAt = new Date().toISOString();
  index.rules = {
    reuseBeforeGenerate: true,
    matchByKeywordAndTags: true,
    maxInsertSeconds: 3,
    preferredAspectRatio: "16:9",
    preferredResolution: "720p",
    generateAudio: false,
  };
  index.keywords ||= {};
  index.keywords[entry.keyword] ||= [];

  const entries = index.keywords[entry.keyword];
  const currentIndex = entries.findIndex((item) => item.id === entry.id);
  if (currentIndex >= 0) {
    entries[currentIndex] = { ...entries[currentIndex], ...entry };
  } else {
    entries.push(entry);
  }
}

for (const clip of TEST_CLIPS) {
  for (const modelConfig of MODEL_CONFIGS) {
    const output = makeOutputPath(modelConfig, clip);
    const index = await readJson(INDEX_PATH, {
      version: 24,
      updatedAt: null,
      rules: {},
      keywords: {},
    });

    if (process.env.FORCE_BROLL !== "1" && (await exists(output))) {
      console.log(`exists, skipping ${output}`);
      upsertIndexEntry(index, makeIndexEntry(modelConfig, clip, output, null));
      await writeJson(INDEX_PATH, index);
      continue;
    }

    console.log(`submitting ${modelConfig.model} -> ${output}`);
    const submitted = await submit(modelConfig.model, clip.prompt);
    const completed = await poll(submitted.polling_url);
    const url = completed.unsigned_urls?.[0] || `https://openrouter.ai/api/v1/videos/${completed.id}/content?index=0`;
    await download(url, output);

    upsertIndexEntry(index, makeIndexEntry(modelConfig, clip, output, completed.id));
    await writeJson(INDEX_PATH, index);
    console.log(`saved ${output}`);
  }
}
