const API_KEY = process.env.OPENROUTER_API_KEY;

const models = ["bytedance/seedance-2.0-fast", "alibaba/wan-2.6", "alibaba/wan-2.7"];

const brolls = [
  {
    output: "assets/broll/v23-broll-01.mp4",
    prompt:
      "cinematic 16:9 b-roll of an AI stock analysis dashboard, glowing financial charts, modern blue and gold interface, no text, no people",
  },
  {
    output: "assets/broll/v23-broll-02.mp4",
    prompt:
      "cinematic 16:9 b-roll of passive dividend income and long-term investing, premium finance visuals, blue and gold lighting, no text, no people",
  },
  {
    output: "assets/broll/v23-broll-03.mp4",
    prompt:
      "cinematic 16:9 b-roll of a single AI prompt transforming into a clean financial web app, elegant interface, blue and gold lighting, no text, no people",
  },
  {
    output: "assets/broll/v23-broll-04.mp4",
    prompt:
      "cinematic 16:9 b-roll of investing in United States stocks, Wall Street market screens, premium blue and gold finance look, no text, no people",
  },
  {
    output: "assets/broll/v23-broll-05.mp4",
    prompt:
      "cinematic 16:9 b-roll of S&P 500 market chart and dividend investing concept, premium finance look, blue and gold lighting, no text, no people",
  },
];

if (!API_KEY) {
  console.error("OPENROUTER_API_KEY is missing. Export it before running this script.");
  process.exit(1);
}

async function submit(model, prompt) {
  const response = await fetch("https://openrouter.ai/api/v1/videos", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://bizdrive.local",
      "X-Title": "Bizdrive HyperFrames B-roll",
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
  if (process.env.FORCE_BROLL !== "1" && (await exists(broll.output))) {
    console.log(`slot ${index + 1}: exists, skipping ${broll.output}`);
    continue;
  }

  let done = false;
  for (const model of models) {
    try {
      console.log(`slot ${index + 1}: submitting ${model}`);
      const submitted = await submit(model, broll.prompt);
      const completed = await poll(submitted.polling_url);
      const url = completed.unsigned_urls?.[0] || `https://openrouter.ai/api/v1/videos/${completed.id}/content?index=0`;
      await download(url, broll.output);
      console.log(`slot ${index + 1}: saved ${broll.output}`);
      done = true;
      break;
    } catch (error) {
      console.error(`slot ${index + 1}: ${model} failed: ${error.message}`);
    }
  }
  if (!done) process.exitCode = 1;
}
