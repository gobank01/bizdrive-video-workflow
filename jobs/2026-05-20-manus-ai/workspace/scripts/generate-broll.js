#!/usr/bin/env node
// Generate full-screen (9:16) B-roll clips for a Template 02 job via OpenRouter.
// Template 02 B-roll fills the whole 1080x1920 frame, so clips are generated
// portrait (9:16) — unlike Template 01's 16:9 top-frame inserts.
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
const brolls = [
  {
    output: `${OUT_DIR}/broll-01.mp4`,
    slot: "10s — hook: upskill with AI",
    prompt:
      "cinematic vertical 9:16 b-roll of a person's hands on a laptop with glowing AI interface elements floating above the screen, modern workspace, blue and gold light, photorealistic, no text, no logos, no faces",
  },
  {
    output: `${OUT_DIR}/broll-02.mp4`,
    slot: "27s — Manus AI agent working autonomously",
    prompt:
      "cinematic vertical 9:16 b-roll of an autonomous AI agent visualized as glowing neural threads completing tasks across multiple floating panels, futuristic dark interface, blue and gold, photorealistic, no text, no logos, no people",
  },
  {
    output: `${OUT_DIR}/broll-03.mp4`,
    slot: "44s — course content, 50+ videos",
    prompt:
      "cinematic vertical 9:16 b-roll of a grid of glowing video lesson thumbnails stacking and flowing upward, online course library feel, dark background with blue and gold accents, photorealistic, no text, no logos, no people",
  },
  {
    output: `${OUT_DIR}/broll-04.mp4`,
    slot: "58s — results: content / graphics / creative output",
    prompt:
      "cinematic vertical 9:16 b-roll of creative digital output forming — abstract graphics, design elements and content pieces assembling into a polished result, blue and gold lighting, photorealistic, no text, no logos, no people",
  },
  {
    output: `${OUT_DIR}/broll-05.mp4`,
    slot: "71s — CTA: join the class",
    prompt:
      "cinematic vertical 9:16 b-roll of a glowing doorway of light opening toward a bright modern learning space, sense of invitation and starting a journey, blue and gold tones, photorealistic, no text, no logos, no people",
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
      "X-Title": "Bizdrive HyperFrames B-roll (Template 02 full-screen)",
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
