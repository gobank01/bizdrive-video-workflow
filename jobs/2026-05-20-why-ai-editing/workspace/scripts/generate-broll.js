#!/usr/bin/env node
// Generate 4 B-roll clips for the why-ai-editing job via OpenRouter.
// Default model: bytedance/seedance-1-5-pro (~10x cheaper than seedance-2.0-fast).

const API_KEY = process.env.OPENROUTER_API_KEY;
const models = ["bytedance/seedance-1-5-pro", "bytedance/seedance-2.0-fast", "google/veo-3.1-lite"];

const OUT_DIR = "../intermediates/broll";

const brolls = [
  {
    output: `${OUT_DIR}/broll-01.mp4`,
    slot: "15s — hook: editing workflow",
    prompt:
      "cinematic abstract b-roll of glowing video clip thumbnails floating and arranging on a dark timeline, blue and gold light streaks, motion graphics feel, no text, no logos, no people, 16:9",
  },
  {
    output: `${OUT_DIR}/broll-02.mp4`,
    slot: "35s — problem: time pressure",
    prompt:
      "cinematic b-roll of a glowing clock with fast-spinning hands dissolving into light particles, sense of time passing and pressure, dark moody background with blue and gold accents, no text, no logos, no people, 16:9",
  },
  {
    output: `${OUT_DIR}/broll-03.mp4`,
    slot: "55s — solution: AI automation",
    prompt:
      "cinematic b-roll of an AI neural network processing video footage, raw clips flowing into a glowing automated pipeline and emerging polished, blue and gold lighting, futuristic, no text, no logos, no people, 16:9",
  },
  {
    output: `${OUT_DIR}/broll-04.mp4`,
    slot: "75s — CTA: ease and speed",
    prompt:
      "cinematic b-roll of a finished video glowing on a sleek monitor in a calm modern creator workspace, soft warm light, sense of effortless completion, blue and gold tones, no text, no logos, no people, 16:9",
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
