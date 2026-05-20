#!/usr/bin/env node
// Generate 16:9 B-roll clips for a Template 03 job via OpenRouter.
// Template 03 B-roll plays inside a floating 16:9 top-insert card (it does not
// cover the whole frame), so clips are generated landscape (16:9) — like
// Template 01's top-frame inserts, unlike Template 02's full-screen 9:16.
//
// Default model: bytedance/seedance-1-5-pro (~10x cheaper than seedance-2.0-fast).
//
// EDIT the `brolls` array below per job — set slot prompts that match the clip.
// Then run from the job workspace:
//   set -a && source .env && set +a && node scripts/generate-broll.js

const API_KEY = process.env.OPENROUTER_API_KEY;
const models = ["bytedance/seedance-1-5-pro", "bytedance/seedance-2.0-fast", "google/veo-3.1-lite"];

const OUT_DIR = "../intermediates/broll";

// --- EDIT THESE PER JOB ---
// Template 02: B-roll is FULL-SCREEN — generate vertical 9:16 clips.
const brolls = [
  {
    output: `${OUT_DIR}/broll-01.mp4`,
    slot: "social feed",
    prompt:
      "vertical 9:16 cinematic b-roll, close-up of a smartphone on a desk showing a fast-scrolling generic social media feed, glowing screen in a dim cozy room, photorealistic, shallow depth of field, no readable text, no logos, no people",
  },
  {
    output: `${OUT_DIR}/broll-02.mp4`,
    slot: "korat noodles",
    prompt:
      "vertical 9:16 cinematic food b-roll, a steaming bowl of Thai khanom-jeen rice noodles with spicy curry sauce and fresh herbs, extreme close-up, warm Thai street-market lighting, photorealistic, appetizing, no text, no logos, no people",
  },
  {
    output: `${OUT_DIR}/broll-03.mp4`,
    slot: "snowy us city",
    prompt:
      "vertical 9:16 cinematic b-roll, a snowy North American city skyline at blue-hour dusk, cold winter light, quiet empty streets, photorealistic, cinematic depth, no text, no logos, no people",
  },
  {
    output: `${OUT_DIR}/broll-04.mp4`,
    slot: "thailand map",
    prompt:
      "vertical 9:16 cinematic b-roll, a printed paper map of Thailand lying on a wooden table, soft warm desk-lamp light, slow push-in toward the northeastern region, photorealistic, no readable text, no logos, no people",
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
      "X-Title": "Bizdrive HyperFrames B-roll (Template 03 top-insert)",
    },
    body: JSON.stringify({
      model,
      prompt,
      aspect_ratio: "9:16",
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
