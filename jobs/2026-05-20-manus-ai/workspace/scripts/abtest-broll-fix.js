#!/usr/bin/env node
// Re-generate slot2-old on seedance-2.0-fast so the whole A/B test uses one model.

import fs from "node:fs/promises";

const API_KEY = process.env.OPENROUTER_API_KEY;
const MODEL = "bytedance/seedance-2.0-fast";
const OUT = "../intermediates/broll-abtest/slot2-old.mp4";
const PROMPT =
  "cinematic vertical 9:16 b-roll of an autonomous AI agent visualized as glowing neural threads completing tasks across multiple floating panels, futuristic dark interface, blue and gold, photorealistic, no text, no logos, no people";

if (!API_KEY) {
  console.error("OPENROUTER_API_KEY missing");
  process.exit(1);
}

async function submit() {
  for (let tries = 1; tries <= 4; tries += 1) {
    const response = await fetch("https://openrouter.ai/api/v1/videos", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${API_KEY}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://bizdrive.local",
        "X-Title": "Bizdrive B-roll A/B test (slot2-old refresh)",
      },
      body: JSON.stringify({
        model: MODEL,
        prompt: PROMPT,
        aspect_ratio: "9:16",
        duration: 5,
        resolution: "720p",
        generate_audio: false,
      }),
    });
    const body = await response.json().catch(() => ({}));
    if (response.ok) return body;
    console.error(`  submit try ${tries}: ${response.status} ${JSON.stringify(body)}`);
    await new Promise((r) => setTimeout(r, 5000));
  }
  throw new Error("submit failed after retries");
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

const submitted = await submit();
const completed = await poll(submitted.polling_url);
const url =
  completed.unsigned_urls?.[0] ||
  `https://openrouter.ai/api/v1/videos/${completed.id}/content?index=0`;
const response = await fetch(url, {
  headers: url.includes("openrouter.ai") ? { Authorization: `Bearer ${API_KEY}` } : {},
});
if (!response.ok) throw new Error(`download failed ${response.status}`);
await fs.writeFile(OUT, new Uint8Array(await response.arrayBuffer()));
console.log(`✓ saved ${OUT} (model: ${MODEL})`);
