#!/usr/bin/env node
// Re-generate the 4 robot B-roll clips using bytedance/seedance-1-5-pro (cheaper).
// Saves to ../intermediates/broll-seedance15/ for side-by-side compare with broll/ (seedance-2.0-fast).

const API_KEY = process.env.OPENROUTER_API_KEY;
const MODEL = "bytedance/seedance-1-5-pro";
const FALLBACK = ["bytedance/seedance-2.0-fast", "alibaba/wan-2.6"];

const OUT_DIR = "../intermediates/broll-seedance15";

const brolls = [
  {
    output: `${OUT_DIR}/robot-broll-01.mp4`,
    slot: "10s — hook reveal",
    prompt:
      "cinematic close-up of an industrial humanoid robot working in a modern automated factory, photorealistic detail, blue and gold rim lighting, slow motion, no people, no text, no logos, 16:9",
  },
  {
    output: `${OUT_DIR}/robot-broll-02.mp4`,
    slot: "25s — Frank robot introduction",
    prompt:
      "cinematic shot of a sleek humanoid robot assembling small parts on a conveyor belt, sparks flying, focused mechanical precision, modern industrial environment, cinematic 16:9, no humans, no text, no logos",
  },
  {
    output: `${OUT_DIR}/robot-broll-03.mp4`,
    slot: "42s — 24/7 stats",
    prompt:
      "time-lapse of multiple humanoid robots working in a vast warehouse, synchronized motion, 24/7 operation feel, blue LED lighting, photorealistic, cinematic 16:9, no text, no people, no logos",
  },
  {
    output: `${OUT_DIR}/robot-broll-04.mp4`,
    slot: "55s — CTA learn AI",
    prompt:
      "cinematic shot of a glowing AI neural network hologram with a robotic arm in soft focus background, modern lab setting, blue and gold lighting, photorealistic, 16:9, no text, no humans, no logos",
  },
];

if (!API_KEY) {
  console.error("OPENROUTER_API_KEY missing");
  process.exit(1);
}

async function submit(model, prompt) {
  const response = await fetch("https://openrouter.ai/api/v1/videos", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://bizdrive.local",
      "X-Title": "Bizdrive HyperFrames B-roll (Seedance 1.5 Pro)",
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
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}: ${JSON.stringify(body)}`);
  }
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
      throw new Error(`video job ${body.status}: ${JSON.stringify(body.error || body)}`);
    }
  }
  throw new Error("video job timed out");
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

const models = [MODEL, ...FALLBACK];

for (const [index, broll] of brolls.entries()) {
  console.log(`\n=== Slot ${index + 1}: ${broll.slot} ===`);
  if (process.env.FORCE_BROLL !== "1" && (await exists(broll.output))) {
    console.log(`  exists, skipping ${broll.output}`);
    continue;
  }
  let done = false;
  for (const model of models) {
    try {
      console.log(`  submitting model: ${model}`);
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
      console.error(`  ✗ ${model} failed: ${error.message}`);
    }
  }
  if (!done) process.exitCode = 1;
}
