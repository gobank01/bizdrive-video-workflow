#!/usr/bin/env node
// A/B test — generate Template 02 (9:16) B-roll for slot 2 and slot 4 with the
// OLD prompt vs the NEW (transcript-grounded, shot-grammar) prompt.
// Outputs 4 clips to ../intermediates/broll-abtest/.
//
// Run from the job workspace:
//   set -a && source .env && set +a && node scripts/abtest-broll.js

import fs from "node:fs/promises";

const API_KEY = process.env.OPENROUTER_API_KEY;
const MODELS = ["bytedance/seedance-1-5-pro", "bytedance/seedance-2.0-fast", "google/veo-3.1-lite"];
const OUT_DIR = "../intermediates/broll-abtest";

// slot 2 ~27s — transcript: "ทำภาพ ทำวิดีโอ ทำสไลด์ ทำเว็บไซต์"
// slot 4 ~58s — transcript: "เข้ามาเรียนได้ทันทีหลังสมัคร แค่ 3,900 บาท"
const clips = [
  {
    id: "slot2-old",
    prompt:
      "cinematic vertical 9:16 b-roll of an autonomous AI agent visualized as glowing neural threads completing tasks across multiple floating panels, futuristic dark interface, blue and gold, photorealistic, no text, no logos, no people",
  },
  {
    id: "slot2-new",
    prompt:
      "Macro lateral dolly across a creator's desk with three angled monitors — one showing a video editing timeline, one a website layout grid, one a slide deck — all rendered as soft out-of-focus shapes, modern studio, slow lateral dolly, cool daylight with a warm gold rim light, cinematic photorealistic 9:16 vertical, shallow depth of field — no readable text, no UI text, no logos, no watermark",
  },
  {
    id: "slot4-old",
    prompt:
      "cinematic vertical 9:16 b-roll of creative digital output forming — abstract graphics, design elements and content pieces assembling into a polished result, blue and gold lighting, photorealistic, no text, no logos, no people",
  },
  {
    id: "slot4-new",
    prompt:
      "Close-up of hands picking up a smartphone on a clean desk, a soft welcoming light blooming from the screen, warm inviting morning light with gentle gold accent, slow push-in, cinematic photorealistic 9:16 vertical, shallow depth of field, face not visible — no on-screen text, no UI text, no logos, no watermark",
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
      "X-Title": "Bizdrive B-roll A/B test (slot 2 + 4)",
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

async function poll(pollingUrl, tag) {
  for (let attempt = 1; attempt <= 80; attempt += 1) {
    await new Promise((r) => setTimeout(r, 15000));
    const response = await fetch(pollingUrl, { headers: { Authorization: `Bearer ${API_KEY}` } });
    const body = await response.json();
    console.log(`  [${tag}] poll ${attempt}: ${body.status}`);
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
  await fs.writeFile(output, new Uint8Array(await response.arrayBuffer()));
}

async function generate(clip) {
  const output = `${OUT_DIR}/${clip.id}.mp4`;
  for (const model of MODELS) {
    try {
      console.log(`  [${clip.id}] submitting ${model}`);
      const submitted = await submit(model, clip.prompt);
      const completed = await poll(submitted.polling_url, clip.id);
      const url =
        completed.unsigned_urls?.[0] ||
        `https://openrouter.ai/api/v1/videos/${completed.id}/content?index=0`;
      await download(url, output);
      console.log(`  [${clip.id}] ✓ saved ${output} (model: ${model})`);
      return { ...clip, output, model };
    } catch (error) {
      console.error(`  [${clip.id}] ✗ ${model}: ${error.message}`);
    }
  }
  throw new Error(`all models failed for ${clip.id}`);
}

(async () => {
  await fs.mkdir(OUT_DIR, { recursive: true });
  const results = await Promise.allSettled(clips.map(generate));
  console.log("\n=== A/B test summary ===");
  let failed = 0;
  results.forEach((r, i) => {
    if (r.status === "fulfilled") console.log(`  ${clips[i].id}: OK  (${r.value.model})`);
    else { console.log(`  ${clips[i].id}: FAILED — ${r.reason.message}`); failed += 1; }
  });
  process.exitCode = failed ? 1 : 0;
})();
