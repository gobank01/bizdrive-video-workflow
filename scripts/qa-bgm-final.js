#!/usr/bin/env node
import { execFileSync, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const DEFAULTS = {
  gainPercent: 5,
  previewSeconds: 20,
  selectorReport: "reports/bgm-select-v54.json",
  mixReport: "reports/bgm-mix-v54.json",
  report: "reports/bgm-final-qa-v54.json"
};

function parseArgs(argv) {
  const args = {
    final: null,
    title: "",
    transcript: null,
    context: null,
    output: null,
    report: DEFAULTS.report,
    selectorReport: DEFAULTS.selectorReport,
    mixReport: DEFAULTS.mixReport,
    previewSeconds: DEFAULTS.previewSeconds,
    gainPercent: DEFAULTS.gainPercent,
    dryRun: false
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--final") {
      args.final = next;
      i += 1;
    } else if (arg === "--title") {
      args.title = next || "";
      i += 1;
    } else if (arg === "--transcript") {
      args.transcript = next;
      i += 1;
    } else if (arg === "--context") {
      args.context = next;
      i += 1;
    } else if (arg === "--output") {
      args.output = next;
      i += 1;
    } else if (arg === "--report") {
      args.report = next;
      i += 1;
    } else if (arg === "--selector-report") {
      args.selectorReport = next;
      i += 1;
    } else if (arg === "--mix-report") {
      args.mixReport = next;
      i += 1;
    } else if (arg === "--preview-seconds") {
      args.previewSeconds = Number(next);
      i += 1;
    } else if (arg === "--gain-percent") {
      args.gainPercent = Number(next);
      i += 1;
    } else if (arg === "--dry-run") {
      args.dryRun = true;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }

  if (!args.final) throw new Error("Missing --final");
  if (!fs.existsSync(args.final)) throw new Error(`Final MP4 not found: ${args.final}`);
  if (!args.title && !args.transcript && !args.context) {
    throw new Error("Provide --title, --transcript, and/or --context for BGM selection");
  }
  if (!Number.isFinite(args.gainPercent) || args.gainPercent <= 0 || args.gainPercent > 100) {
    throw new Error("Invalid --gain-percent; use > 0 and <= 100");
  }
  if (!Number.isFinite(args.previewSeconds) || args.previewSeconds <= 0) {
    throw new Error("Invalid --preview-seconds");
  }

  const parsed = path.parse(args.final);
  if (!args.output) {
    args.output = path.join(parsed.dir, `${parsed.name}-bgm-${args.gainPercent}pct${parsed.ext}`);
  }
  return args;
}

function runNodeScript(script, args, options = {}) {
  const result = spawnSync("node", [script, ...args], {
    cwd: process.cwd(),
    encoding: "utf8",
    stdio: options.inherit ? "inherit" : ["ignore", "pipe", "pipe"]
  });
  if (result.status !== 0) {
    const output = [result.stdout, result.stderr].filter(Boolean).join("\n");
    throw new Error(`${script} failed with exit ${result.status}\n${output}`);
  }
  return result.stdout || "";
}

function ffprobe(file) {
  return JSON.parse(execFileSync("ffprobe", [
    "-v",
    "error",
    "-show_entries",
    "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,sample_rate",
    "-of",
    "json",
    file
  ], { encoding: "utf8" }));
}

function loudnessFromStderr(file) {
  const result = spawnSync("ffmpeg", [
    "-hide_banner",
    "-nostats",
    "-i",
    file,
    "-filter_complex",
    "ebur128=peak=true",
    "-f",
    "null",
    "-"
  ], { encoding: "utf8" });
  if (result.status !== 0) throw new Error(`ffmpeg loudness failed for ${file}\n${result.stderr}`);
  return parseLoudness(result.stderr);
}

function parseLoudness(text) {
  const integrated = lastMatch(text, /I:\s*(-?\d+(?:\.\d+)?) LUFS/g);
  const lra = lastMatch(text, /LRA:\s*(-?\d+(?:\.\d+)?) LU/g);
  const peak = lastMatch(text, /Peak:\s*(-?\d+(?:\.\d+)?) dBFS/g);
  return {
    integratedLufs: integrated === null ? null : Number(integrated),
    loudnessRangeLu: lra === null ? null : Number(lra),
    truePeakDbfs: peak === null ? null : Number(peak)
  };
}

function lastMatch(text, pattern) {
  let result = null;
  for (const match of text.matchAll(pattern)) {
    result = match[1];
  }
  return result;
}

function makePreview(source, output, seconds) {
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const result = spawnSync("ffmpeg", [
    "-hide_banner",
    "-loglevel",
    "error",
    "-y",
    "-t",
    String(seconds),
    "-i",
    source,
    "-c",
    "copy",
    "-movflags",
    "+faststart",
    output
  ], { stdio: "inherit" });
  if (result.status !== 0) throw new Error(`ffmpeg preview failed with exit ${result.status}`);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function qaStatus(originalLoudness, mixedLoudness) {
  const lufsDelta = mixedLoudness.integratedLufs - originalLoudness.integratedLufs;
  const peakOk = mixedLoudness.truePeakDbfs <= -1.5;
  const lufsOk = Math.abs(lufsDelta) <= 1.0;
  return {
    status: peakOk && lufsOk ? "pass" : "review",
    lufsDelta: Number(lufsDelta.toFixed(2)),
    peakOk,
    lufsOk,
    notes: peakOk && lufsOk
      ? "BGM final QA is within speech-first defaults."
      : "Review by listening; adjust gain/track/limiter if BGM distracts or peak is too high."
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  fs.mkdirSync(path.dirname(args.selectorReport), { recursive: true });
  fs.mkdirSync(path.dirname(args.mixReport), { recursive: true });
  fs.mkdirSync(path.dirname(args.report), { recursive: true });

  const selectorArgs = [
    "--output", args.selectorReport,
    "--gain-percent", String(args.gainPercent)
  ];
  if (args.title) selectorArgs.push("--title", args.title);
  if (args.transcript) selectorArgs.push("--transcript", args.transcript);
  if (args.context) selectorArgs.push("--context", args.context);

  const selectCommand = `node scripts/select-bgm.js ${selectorArgs.map(quote).join(" ")}`;
  const selectorOutput = args.dryRun ? "" : runNodeScript("scripts/select-bgm.js", selectorArgs);
  const selectorReport = args.dryRun ? null : readJson(args.selectorReport);
  const selectedTrack = selectorReport?.selectedTrack;
  if (!args.dryRun && !selectedTrack?.localPath) throw new Error("BGM selector did not return a selectedTrack.localPath");

  const mixArgs = selectedTrack ? [
    "--voice", args.final,
    "--bgm", selectedTrack.localPath,
    "--output", args.output,
    "--report", args.mixReport,
    "--gain-percent", String(args.gainPercent)
  ] : [];
  const mixCommand = selectedTrack
    ? `node scripts/mix-bgm.js ${mixArgs.map(quote).join(" ")}`
    : "node scripts/mix-bgm.js <pending selector>";

  if (args.dryRun) {
    const report = {
      version: 54,
      dryRun: true,
      selectCommand,
      mixCommand,
      final: args.final,
      output: args.output,
      report: args.report
    };
    console.log(JSON.stringify(report, null, 2));
    return;
  }

  runNodeScript("scripts/mix-bgm.js", mixArgs, { inherit: true });

  const finalParsed = path.parse(args.final);
  const outputParsed = path.parse(args.output);
  const originalPreview = path.join(finalParsed.dir || ".", `${finalParsed.name}-preview${args.previewSeconds}s-original${finalParsed.ext}`);
  const mixedPreview = path.join(outputParsed.dir || ".", `${outputParsed.name}-preview${args.previewSeconds}s${outputParsed.ext}`);
  makePreview(args.final, originalPreview, args.previewSeconds);
  makePreview(args.output, mixedPreview, args.previewSeconds);

  const originalLoudness = loudnessFromStderr(args.final);
  const mixedLoudness = loudnessFromStderr(args.output);
  const report = {
    version: 54,
    finalInput: args.final,
    bgmOutput: args.output,
    title: args.title,
    transcript: args.transcript,
    context: args.context,
    selectorReport: args.selectorReport,
    mixReport: args.mixReport,
    selectedStyle: selectorReport.selectedStyle,
    selectedTrack,
    gainPercent: args.gainPercent,
    audibilityIntent: "barely audible ambient bed, felt more than heard",
    originalPreview,
    mixedPreview,
    originalMetadata: ffprobe(args.final),
    mixedMetadata: ffprobe(args.output),
    originalLoudness,
    mixedLoudness,
    qa: qaStatus(originalLoudness, mixedLoudness),
    commands: {
      select: selectCommand,
      mix: mixCommand
    }
  };

  fs.writeFileSync(args.report, `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify(report, null, 2));
}

function quote(value) {
  return /[\s"'$]/.test(value) ? JSON.stringify(value) : value;
}

function printHelp() {
  console.log(`Usage:
  npm run qa:bgm -- --final ../stacked-output.mp4 --title "ใช้ AI ตัดต่อคลิป" --context assets/context/test2-v35-full-context-index.json

Options:
  --final <path>            Required final rendered MP4 to QA with BGM
  --title <text>            Clip title/topic for BGM selector
  --transcript <path>       Transcript JSON for BGM selector
  --context <path>          Context index JSON for BGM selector
  --output <path>           Mixed final MP4 output
  --report <path>           Final BGM QA JSON, default ${DEFAULTS.report}
  --selector-report <path>  Selector JSON, default ${DEFAULTS.selectorReport}
  --mix-report <path>       Mix JSON, default ${DEFAULTS.mixReport}
  --preview-seconds <n>     Preview duration, default 20
  --gain-percent <n>        BGM level, default 5
  --dry-run                 Print planned commands
`);
}

try {
  main();
} catch (error) {
  console.error(`qa-bgm-final: ${error.message}`);
  process.exit(2);
}
