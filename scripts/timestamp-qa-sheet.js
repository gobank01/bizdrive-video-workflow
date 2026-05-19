import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

function parseArgs(argv) {
  const args = {
    cols: 5,
    width: 360,
    prefix: "timestamp-qa",
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--input") args.input = argv[++index];
    else if (arg === "--output-dir") args.outputDir = argv[++index];
    else if (arg === "--prefix") args.prefix = argv[++index];
    else if (arg === "--cols") args.cols = Number(argv[++index]);
    else if (arg === "--width") args.width = Number(argv[++index]);
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }

  return args;
}

function usage() {
  return `Usage:
  npm run qa:timestamps -- --input <video.mp4> --output-dir <dir> [--prefix final] [--cols 5] [--width 360]

Creates:
  <dir>/frames/<prefix>-%04d.jpg  one labeled frame per second
  <dir>/<prefix>-sheet.jpg        tiled contact sheet
  <dir>/<prefix>-manifest.json    metadata for QA report
`;
}

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { encoding: "utf8", stdio: options.stdio ?? "pipe" });
  if (result.status !== 0) {
    const stderr = result.stderr ? `\n${result.stderr}` : "";
    const stdout = result.stdout ? `\n${result.stdout}` : "";
    throw new Error(`${command} failed${stderr}${stdout}`);
  }
  return result.stdout ?? "";
}

function ffprobeDuration(input) {
  const stdout = run("ffprobe", [
    "-v",
    "error",
    "-show_entries",
    "format=duration",
    "-of",
    "default=noprint_wrappers=1:nokey=1",
    input,
  ]);
  const duration = Number(stdout.trim());
  if (!Number.isFinite(duration) || duration <= 0) throw new Error(`Unable to read duration from ${input}`);
  return duration;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    process.stdout.write(usage());
    return;
  }
  if (!args.input || !args.outputDir) throw new Error(`Missing required arguments.\n${usage()}`);
  if (!fs.existsSync(args.input)) throw new Error(`Input not found: ${args.input}`);
  if (!Number.isInteger(args.cols) || args.cols < 1) throw new Error("--cols must be a positive integer");
  if (!Number.isInteger(args.width) || args.width < 120) throw new Error("--width must be an integer >= 120");

  const duration = ffprobeDuration(args.input);
  const frameCount = Math.ceil(duration);
  const rows = Math.ceil(frameCount / args.cols);
  const outputDir = args.outputDir;
  const framesDir = path.join(outputDir, "frames");
  const sheetPath = path.join(outputDir, `${args.prefix}-sheet.jpg`);
  const manifestPath = path.join(outputDir, `${args.prefix}-manifest.json`);

  fs.mkdirSync(outputDir, { recursive: true });
  fs.rmSync(framesDir, { recursive: true, force: true });
  fs.mkdirSync(framesDir, { recursive: true });

  const framePattern = path.join(framesDir, `${args.prefix}-%04d.jpg`);
  const drawText = [
    "fps=1",
    `scale=${args.width}:-1`,
    "drawtext=text='%{pts\\:hms}':x=12:y=12:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=8",
  ].join(",");

  run(
    "ffmpeg",
    ["-hide_banner", "-loglevel", "error", "-y", "-i", args.input, "-vf", drawText, "-vsync", "0", "-q:v", "3", framePattern],
    { stdio: "pipe" }
  );

  run(
    "ffmpeg",
    [
      "-hide_banner",
      "-loglevel",
      "error",
      "-y",
      "-framerate",
      "1",
      "-i",
      framePattern,
      "-vf",
      `tile=${args.cols}x${rows}:margin=8:padding=4:color=black`,
      "-frames:v",
      "1",
      "-q:v",
      "3",
      sheetPath,
    ],
    { stdio: "pipe" }
  );

  const manifest = {
    input: path.resolve(args.input),
    outputDir: path.resolve(outputDir),
    framesDir: path.resolve(framesDir),
    sheetPath: path.resolve(sheetPath),
    durationSeconds: Number(duration.toFixed(3)),
    intervalSeconds: 1,
    expectedFrames: frameCount,
    cols: args.cols,
    rows,
    width: args.width,
    purpose: "Every-second timestamp QA sheet for checking lip sync, cuts, captions, B-roll, and timeline issues.",
  };
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify(manifest, null, 2)}\n`);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
