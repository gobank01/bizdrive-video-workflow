// gen-shots.js — serial-drama shot generator.
// Clone of templates/01-stacked-vertical-burst/scripts/generate-openrouter-broll.js
// (submit/poll/download semantics kept verbatim) with three changes:
//   1. shots come from a JSON file given on the CLI, not a hard-coded array
//   2. [BLOCK] placeholders are injected from bible/characters.json — character/set/style
//      text is never hand-typed in a shots file (continuity rule)
//   3. vertical 9:16 default + per-shot take suffixes (s4-take2.mp4)
//
// Usage: node gen-shots.js <shots.json> [--force]
//
// shots.json:
// {
//   "outputDir": "takes",            // relative to the shots.json file
//   "aspect_ratio": "9:16",          // optional, default 9:16
//   "shots": [
//     { "id": "s1", "prompt": "[PHONE], [STYLE]", "duration": 5, "takes": 1 }
//   ]
// }

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const API_KEY = process.env.OPENROUTER_API_KEY;

// Model order: cheapest viable first (see original script for the 2026-05-20 test notes).
const models = ["bytedance/seedance-1-5-pro", "bytedance/seedance-2.0-fast", "google/veo-3.1-lite"];

const here = path.dirname(fileURLToPath(import.meta.url));
const shotsPath = process.argv[2];
const FORCE = process.argv.includes("--force") || process.env.FORCE_BROLL === "1";

if (!API_KEY) {
  console.error("OPENROUTER_API_KEY is missing. Source templates/_shared/env/.env first.");
  process.exit(1);
}
if (!shotsPath) {
  console.error("usage: node gen-shots.js <shots.json> [--force]");
  process.exit(1);
}

const spec = JSON.parse(await fs.readFile(shotsPath, "utf8"));
const bible = JSON.parse(await fs.readFile(path.join(here, "bible", "characters.json"), "utf8"));
const state = JSON.parse(await fs.readFile(path.join(here, "bible", "season-state.json"), "utf8"));

function resolvePrompt(raw) {
  return raw.replace(/\[([A-Z0-9-]+)\]/g, (_, key) => {
    let block = bible.blocks[key];
    if (!block) {
      throw new Error(`unknown bible block [${key}] — add it to bible/characters.json; never inline character text`);
    }
    if (key === "SET" && state.setExtra) block += state.setExtra;
    return block;
  });
}

async function submit(model, prompt) {
  const response = await fetch("https://openrouter.ai/api/v1/videos", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://bizdrive.local",
      "X-Title": "Bizdrive Serial Drama",
    },
    body: JSON.stringify({
      model,
      prompt,
      aspect_ratio: spec.aspect_ratio || "9:16",
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
    await new Promise((resolve) => setTimeout(resolve, 15000));
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
  const response = await fetch(url, {
    headers: url.includes("openrouter.ai") ? { Authorization: `Bearer ${API_KEY}` } : {},
  });
  if (!response.ok) throw new Error(`download failed ${response.status} ${response.statusText}`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  await fs.writeFile(output, bytes);
}

async function exists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

const outDir = path.resolve(path.dirname(shotsPath), spec.outputDir || "takes");
await fs.mkdir(outDir, { recursive: true });

let failures = 0;
for (const shot of spec.shots) {
  if (shot.html || shot.file) {
    console.log(`${shot.id}: ${shot.html ? "html" : "anchor file"} shot, nothing to generate`);
    continue;
  }
  const prompt = resolvePrompt(shot.prompt);
  const takes = shot.takes || 1;
  for (let t = 1; t <= takes; t += 1) {
    const output = path.join(outDir, `${shot.id}-take${t}.mp4`);
    if (!FORCE && (await exists(output))) {
      console.log(`${shot.id} take ${t}: exists, skipping`);
      continue;
    }
    let done = false;
    for (const model of models) {
      try {
        console.log(`${shot.id} take ${t}: submitting ${model}`);
        console.log(`  prompt: ${prompt}`);
        const submitted = await submit(model, prompt);
        const completed = await poll(submitted.polling_url);
        const url = completed.unsigned_urls?.[0] || `https://openrouter.ai/api/v1/videos/${completed.id}/content?index=0`;
        await download(url, output);
        console.log(`${shot.id} take ${t}: saved ${output}`);
        done = true;
        break;
      } catch (error) {
        console.error(`${shot.id} take ${t}: ${model} failed: ${error.message}`);
      }
    }
    if (!done) failures += 1;
  }
}

if (failures > 0) {
  console.error(`${failures} take(s) failed on all models`);
  process.exitCode = 1;
}
