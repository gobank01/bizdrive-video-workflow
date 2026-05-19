#!/usr/bin/env node
import { execFileSync, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const DEFAULTS = {
  fadeIn: 0.5,
  fadeOut: 1.0,
  gainPercent: 5,
  gainDb: percentToDb(5),
  limiterLimit: 0.80,
  duck: false,
  duckThreshold: 0.02,
  duckRatio: 6,
  audioBitrate: "192k"
};

function parseArgs(argv) {
  const args = {
    voice: null,
    bgm: null,
    output: null,
    report: null,
    fadeIn: DEFAULTS.fadeIn,
    fadeOut: DEFAULTS.fadeOut,
    gainPercent: DEFAULTS.gainPercent,
    gainDb: DEFAULTS.gainDb,
    limiterLimit: DEFAULTS.limiterLimit,
    duck: DEFAULTS.duck,
    duckThreshold: DEFAULTS.duckThreshold,
    duckRatio: DEFAULTS.duckRatio,
    audioBitrate: DEFAULTS.audioBitrate,
    dryRun: false
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--voice") {
      args.voice = next;
      i += 1;
    } else if (arg === "--bgm") {
      args.bgm = next;
      i += 1;
    } else if (arg === "--output") {
      args.output = next;
      i += 1;
    } else if (arg === "--report") {
      args.report = next;
      i += 1;
    } else if (arg === "--fade-in") {
      args.fadeIn = Number(next);
      i += 1;
    } else if (arg === "--fade-out") {
      args.fadeOut = Number(next);
      i += 1;
    } else if (arg === "--gain-db") {
      args.gainDb = Number(next);
      args.gainPercent = null;
      i += 1;
    } else if (arg === "--gain-percent") {
      args.gainPercent = Number(next);
      args.gainDb = percentToDb(args.gainPercent);
      i += 1;
    } else if (arg === "--duck") {
      args.duck = next !== "false";
      if (next && !next.startsWith("--")) i += 1;
    } else if (arg === "--duck-threshold") {
      args.duckThreshold = Number(next);
      i += 1;
    } else if (arg === "--duck-ratio") {
      args.duckRatio = Number(next);
      i += 1;
    } else if (arg === "--limiter-limit") {
      args.limiterLimit = Number(next);
      i += 1;
    } else if (arg === "--audio-bitrate") {
      args.audioBitrate = next;
      i += 1;
    } else if (arg === "--dry-run") {
      args.dryRun = true;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }

  for (const key of ["voice", "bgm", "output"]) {
    if (!args[key]) throw new Error(`Missing --${key}`);
  }
  for (const key of ["fadeIn", "fadeOut", "gainDb", "limiterLimit", "duckThreshold", "duckRatio"]) {
    if (!Number.isFinite(args[key])) throw new Error(`Invalid ${key}`);
  }
  if (args.limiterLimit <= 0 || args.limiterLimit > 1) throw new Error("Invalid limiterLimit; use a value > 0 and <= 1");
  if (args.gainPercent !== null && (!Number.isFinite(args.gainPercent) || args.gainPercent <= 0 || args.gainPercent > 100)) {
    throw new Error("Invalid gainPercent; use a value > 0 and <= 100");
  }
  if (!fs.existsSync(args.voice)) throw new Error(`Voice file not found: ${args.voice}`);
  if (!fs.existsSync(args.bgm)) throw new Error(`BGM file not found: ${args.bgm}`);
  return args;
}

function ffprobeDuration(file) {
  const raw = execFileSync("ffprobe", [
    "-v",
    "error",
    "-show_entries",
    "format=duration",
    "-of",
    "default=nokey=1:noprint_wrappers=1",
    file
  ], { encoding: "utf8" }).trim();
  const duration = Number(raw);
  if (!Number.isFinite(duration) || duration <= 0) {
    throw new Error(`Could not read duration for ${file}`);
  }
  return duration;
}

function dbToLinear(db) {
  return Math.pow(10, db / 20);
}

function percentToDb(percent) {
  return 20 * Math.log10(percent / 100);
}

function dbToPercent(db) {
  return dbToLinear(db) * 100;
}

function buildFilter(args, duration) {
  const bgmVolume = dbToLinear(args.gainDb).toFixed(6);
  const fadeOutStart = Math.max(0, duration - args.fadeOut).toFixed(3);
  const fadeIn = Math.max(0, args.fadeIn).toFixed(3);
  const fadeOut = Math.max(0, args.fadeOut).toFixed(3);
  const bgmBase = `[1:a]volume=${bgmVolume},afade=t=in:st=0:d=${fadeIn},afade=t=out:st=${fadeOutStart}:d=${fadeOut}[bgm0]`;
  const audioTailLock = `,apad,atrim=0:${duration.toFixed(6)},asetpts=PTS-STARTPTS[a]`;

  if (args.duck) {
    return `${bgmBase};[bgm0][0:a]sidechaincompress=threshold=${args.duckThreshold}:ratio=${args.duckRatio}:attack=20:release=250[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=${args.limiterLimit}:level=false${audioTailLock}`;
  }
  return `${bgmBase};[0:a][bgm0]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=${args.limiterLimit}:level=false${audioTailLock}`;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const duration = ffprobeDuration(args.voice);
  const filter = buildFilter(args, duration);
  const ffmpegArgs = [
    "-y",
    "-i",
    args.voice,
    "-stream_loop",
    "-1",
    "-i",
    args.bgm,
    "-filter_complex",
    filter,
    "-map",
    "0:v?",
    "-map",
    "[a]",
    "-c:v",
    "copy",
    "-c:a",
    "aac",
    "-b:a",
    args.audioBitrate,
    "-movflags",
    "+faststart",
    args.output
  ];

  const report = {
    version: 54,
    voice: args.voice,
    bgm: args.bgm,
    output: args.output,
    duration,
    stockIndex: "bgm-library/mixkit-stock-v50.json",
    sourcePolicy: "licensed/royalty-free/generated-with-usage-rights only; do not assume arbitrary music is copyright-free",
    gainPercent: args.gainPercent,
    effectiveGainPercent: Number(dbToPercent(args.gainDb).toFixed(3)),
    gainDb: args.gainDb,
    fadeIn: args.fadeIn,
    fadeOut: args.fadeOut,
    limiterLimit: args.limiterLimit,
    duck: args.duck,
    duckThreshold: args.duckThreshold,
    duckRatio: args.duckRatio,
    audioBitrate: args.audioBitrate,
    command: `ffmpeg ${ffmpegArgs.map(quote).join(" ")}`
  };

  if (args.dryRun) {
    console.log(JSON.stringify(report, null, 2));
    return;
  }

  fs.mkdirSync(path.dirname(args.output), { recursive: true });
  const result = spawnSync("ffmpeg", ffmpegArgs, { stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`ffmpeg failed with exit code ${result.status}`);
  }

  if (args.report) {
    fs.mkdirSync(path.dirname(args.report), { recursive: true });
    fs.writeFileSync(args.report, `${JSON.stringify(report, null, 2)}\n`);
  }
  console.log(JSON.stringify(report, null, 2));
}

function quote(value) {
  return /[\s"'$]/.test(value) ? JSON.stringify(value) : value;
}

function printHelp() {
  console.log(`Usage:
  npm run mix:bgm -- --voice assets/bottom_audio_polished.mp4 --bgm assets/bgm/track.mp3 --output assets/bottom_with_bgm.mp4

Options:
  --voice <path>          Bottom polished video/audio source
  --bgm <path>            Licensed/royalty-free/generated-with-rights BGM file
  --output <path>         Output video/audio with BGM mixed in
  --report <path>         Optional JSON mix report
  --gain-percent <number> BGM level as percent of original, default 5
  --gain-db <number>      BGM gain in dB, overrides percent default
  --fade-in <seconds>     BGM fade in, default 0.5
  --fade-out <seconds>    BGM fade out, default 1.0
  --duck true|false       Sidechain duck BGM under voice, default false
  --duck-threshold <n>    Sidechain threshold, default 0.02
  --duck-ratio <n>        Sidechain ratio, default 6
  --limiter-limit <n>     Final limiter ceiling, default 0.80
  --dry-run               Print ffmpeg command without rendering
`);
}

try {
  main();
} catch (error) {
  console.error(`mix-bgm: ${error.message}`);
  process.exit(2);
}
