#!/usr/bin/env node
// Generate 4 B-roll clips for the why-ai-editing job via OpenRouter.
// Default model: bytedance/seedance-1-5-pro (~10x cheaper than seedance-2.0-fast).

const API_KEY = process.env.OPENROUTER_API_KEY;
const models = ["bytedance/seedance-1-5-pro", "bytedance/seedance-2.0-fast", "google/veo-3.1-lite"];

const OUT_DIR = "../intermediates/broll";

const brolls = [
  {
    output: `${OUT_DIR}/broll-01.mp4`,
    slot: "12s — solar panels overview",
    prompt:
      "cinematic aerial b-roll of a large solar panel farm under blue sky, rows of photovoltaic panels glinting in sunlight, clean renewable energy, no text, no logos, no people, 16:9",
  },
  {
    output: `${OUT_DIR}/broll-02.mp4`,
    slot: "32s — On Grid (connected to power grid)",
    prompt:
      "cinematic b-roll of rooftop solar panels connected to power lines and an electricity grid, modern house, sunny day, clean energy infrastructure, no text, no logos, no people, 16:9",
  },
  {
    output: `${OUT_DIR}/broll-03.mp4`,
    slot: "52s — Off Grid (remote + battery)",
    prompt:
      "cinematic b-roll of an off-grid solar setup in a remote rural area with a large battery storage unit beside solar panels, isolated landscape, golden light, no text, no logos, no people, 16:9",
  },
  {
    output: `${OUT_DIR}/broll-04.mp4`,
    slot: "70s — Hybrid system",
    prompt:
      "cinematic b-roll of a hybrid solar energy system, solar panels with both grid connection and battery backup, glowing energy flow diagram feel, modern clean technology, blue and gold light, no text, no logos, no people, 16:9",
  },
];

if (!API_KEY) {
  console.error("OPENROUTER_API_KEY missing — add it to .env");
  process.exit(1);
}

async function submit(model, prompt) {
  const response = await fetch("https://openrouter.ai/api/v1/videos", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://bizdrive.local",
      "X-Title": "Bizdrive HyperFrames B-roll (why-ai-editing)",
    },
    body: JSON.stringify({
      model,
      prompt,
      aspect_ratio: "16:9",
      duration: 5,
      resolution: "720p",
      generate_audio: false,
    }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`${response.status}: ${JSON.stringify(body)}`);
  return body;
}

async function poll(pollingUrl) {
  for (let attempt = 1; attempt <= 80; attempt += 1) {
    await new Promise((r) => setTimeout(r, 15000));
    const response = await fetch(pollingUrl, { headers: { Authorization: `Bearer ${API_KEY}` } });
    const body = await response.json();
    console.log(`  poll ${attempt}: ${body.status}`);
    if (body.status === "completed") return body;
    if (["failed", "cancelled", "expired"].includes(body.status)) {
      throw new Error(`${body.status}: ${JSON.stringify(body.error || body)}`);
    }
  }
  throw new Error("timed out");
}

async function download(url, output) {
  const response = await fetch(url, {
    headers: url.includes("openrouter.ai") ? { Authorization: `Bearer ${API_KEY}` } : {},
  });
  if (!response.ok) throw new Error(`download failed ${response.status}`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  await import("node:fs/promises").then((fs) => fs.writeFile(output, bytes));
}

async function exists(path) {
  try {
    await import("node:fs/promises").then((fs) => fs.access(path));
    return true;
  } catch {
    return false;
  }
}

for (const [index, broll] of brolls.entries()) {
  console.log(`\n=== Slot ${index + 1}: ${broll.slot} ===`);
  if (process.env.FORCE_BROLL !== "1" && (await exists(broll.output))) {
    console.log(`  exists, skipping`);
    continue;
  }
  let done = false;
  for (const model of models) {
    try {
      console.log(`  model: ${model}`);
      const submitted = await submit(model, broll.prompt);
      const completed = await poll(submitted.polling_url);
      const url =
        completed.unsigned_urls?.[0] ||
        `https://openrouter.ai/api/v1/videos/${completed.id}/content?index=0`;
      await download(url, broll.output);
      console.log(`  ✓ saved ${broll.output}`);
      done = true;
      break;
    } catch (error) {
      console.error(`  ✗ ${model}: ${error.message}`);
    }
  }
  if (!done) process.exitCode = 1;
}
