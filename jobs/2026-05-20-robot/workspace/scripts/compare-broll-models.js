#!/usr/bin/env node
// Compare cheaper OpenRouter video models against the current seedance-2.0-fast.
// Generates ONE clip per model with the same prompt → save side-by-side for comparison.

const API_KEY = process.env.OPENROUTER_API_KEY;

const PROMPT =
  "cinematic close-up of an industrial humanoid robot working in a modern automated factory, photorealistic detail, blue and gold rim lighting, slow motion, no people, no text, no logos, 16:9";

const OUT_DIR = "../intermediates/broll-compare";

// Models sorted from cheapest to most expensive (per 3-5s clip estimated cost)
const tests = [
  {
    id: "01-seedance-1-5-pro",
    model: "bytedance/seedance-1-5-pro",
    expectedCost: "~$0.02",
    body: {
      aspect_ratio: "16:9",
      duration: 4,
      resolution: "720p",
      generate_audio: false,
    },
  },
  {
    id: "02-veo-3-1-lite",
    model: "google/veo-3.1-lite",
    expectedCost: "~$0.12",
    body: {
      aspect_ratio: "16:9",
      duration: 4,
      resolution: "720p",
      generate_audio: false,
    },
  },
  {
    id: "03-wan-2-6-480p",
    model: "alibaba/wan-2.6",
    expectedCost: "~$0.20",
    body: {
      aspect_ratio: "16:9",
      duration: 5,
      resolution: "480p",
      generate_audio: false,
    },
  },
  {
    id: "04-grok-imagine-480p",
    model: "x-ai/grok-imagine-video",
    expectedCost: "~$0.25",
    body: {
      aspect_ratio: "16:9",
      duration: 5,
      resolution: "480p",
      generate_audio: false,
    },
  },
];

if (!API_KEY) {
  console.error("OPENROUTER_API_KEY missing");
  process.exit(1);
}

async function submit(model, body) {
  const response = await fetch("https://openrouter.ai/api/v1/videos", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://bizdrive.local",
      "X-Title": "Bizdrive HyperFrames B-roll (Model Compare)",
    },
    body: JSON.stringify({ model, prompt: PROMPT, ...body }),
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}: ${JSON.stringify(result)}`);
  }
  return result;
}

async function poll(pollingUrl) {
  for (let attempt = 1; attempt <= 60; attempt += 1) {
    await new Promise((r) => setTimeout(r, 15000));
    const response = await fetch(pollingUrl, { headers: { Authorization: `Bearer ${API_KEY}` } });
    const body = await response.json();
    process.stdout.write(`.${body.status[0]}`);
    if (body.status === "completed") {
      process.stdout.write(" done\n");
      return body;
    }
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
  if (!response.ok) throw new Error(`download ${response.status}`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  await import("node:fs/promises").then((fs) => fs.writeFile(output, bytes));
}

console.log(`Comparing ${tests.length} models with same prompt:`);
console.log(`Prompt: "${PROMPT.slice(0, 80)}..."`);
console.log("");

const results = [];
for (const test of tests) {
  const output = `${OUT_DIR}/${test.id}.mp4`;
  console.log(`\n[${test.id}] ${test.model} (expected: ${test.expectedCost})`);
  const t0 = Date.now();
  try {
    const submitted = await submit(test.model, test.body);
    process.stdout.write("  polling: ");
    const completed = await poll(submitted.polling_url);
    const url =
      completed.unsigned_urls?.[0] ||
      `https://openrouter.ai/api/v1/videos/${completed.id}/content?index=0`;
    await download(url, output);
    const t1 = Date.now();
    console.log(`  ✓ saved ${output} (${((t1 - t0) / 1000).toFixed(1)}s)`);
    results.push({
      id: test.id,
      model: test.model,
      output,
      timeSec: ((t1 - t0) / 1000).toFixed(1),
      expectedCost: test.expectedCost,
      status: "ok",
    });
  } catch (error) {
    console.error(`  ✗ failed: ${error.message}`);
    results.push({ id: test.id, model: test.model, status: "fail", error: error.message });
  }
}

console.log("\n=== SUMMARY ===");
console.log(JSON.stringify(results, null, 2));
