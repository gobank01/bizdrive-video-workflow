#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const DEFAULTS = {
  dir: "..",
  gainPercent: 5,
  previewSeconds: 20,
  reportsDir: "reports",
  suffix: "auto-bgm"
};

function parseArgs(argv) {
  const args = {
    dir: DEFAULTS.dir,
    final: null,
    title: "",
    transcript: null,
    context: null,
    output: null,
    report: null,
    selectorReport: null,
    mixReport: null,
    gainPercent: DEFAULTS.gainPercent,
    previewSeconds: DEFAULTS.previewSeconds,
    includeBgmOutputs: false,
    includePreviews: false,
    dryRun: false
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--dir") {
      args.dir = next || DEFAULTS.dir;
      i += 1;
    } else if (arg === "--final") {
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
    } else if (arg === "--gain-percent") {
      args.gainPercent = Number(next);
      i += 1;
    } else if (arg === "--preview-seconds") {
      args.previewSeconds = Number(next);
      i += 1;
    } else if (arg === "--include-bgm-outputs") {
      args.includeBgmOutputs = true;
    } else if (arg === "--include-previews") {
      args.includePreviews = true;
    } else if (arg === "--dry-run") {
      args.dryRun = true;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }

  if (!Number.isFinite(args.gainPercent) || args.gainPercent <= 0 || args.gainPercent > 100) {
    throw new Error("Invalid --gain-percent; use > 0 and <= 100");
  }
  if (!Number.isFinite(args.previewSeconds) || args.previewSeconds <= 0) {
    throw new Error("Invalid --preview-seconds");
  }
  if (!args.title && !args.transcript && !args.context) {
    throw new Error("Provide --title, --transcript, and/or --context for BGM selection");
  }

  args.final = args.final || findLatestFinal(args);
  if (!fs.existsSync(args.final)) throw new Error(`Final MP4 not found: ${args.final}`);
  fillDerivedPaths(args);
  return args;
}

function findLatestFinal(args) {
  const dir = path.resolve(args.dir);
  if (!fs.existsSync(dir)) throw new Error(`Directory not found: ${args.dir}`);
  const candidates = fs.readdirSync(dir)
    .filter((name) => /^stacked-output.*\.mp4$/i.test(name))
    .filter((name) => args.includePreviews || !/-preview\d*s|preview\d+|preview/i.test(name))
    .filter((name) => args.includeBgmOutputs || !/(auto-bgm|bgm-\d+pct|default-curiosity|with-bgm|v54-auto-bgm)/i.test(name))
    .map((name) => {
      const file = path.join(dir, name);
      const stat = fs.statSync(file);
      return { file, name, mtimeMs: stat.mtimeMs };
    })
    .sort((a, b) => b.mtimeMs - a.mtimeMs);

  if (!candidates.length) {
    throw new Error(`No eligible stacked-output*.mp4 found in ${args.dir}`);
  }
  return path.relative(process.cwd(), candidates[0].file);
}

function fillDerivedPaths(args) {
  const parsed = path.parse(args.final);
  const base = parsed.name;
  const reportBase = safeName(base);
  if (!args.output) {
    args.output = path.join(parsed.dir || ".", `${base}-${DEFAULTS.suffix}-${args.gainPercent}pct${parsed.ext}`);
  }
  if (!args.report) args.report = path.join(DEFAULTS.reportsDir, `${reportBase}-${DEFAULTS.suffix}-qa.json`);
  if (!args.selectorReport) args.selectorReport = path.join(DEFAULTS.reportsDir, `${reportBase}-${DEFAULTS.suffix}-select.json`);
  if (!args.mixReport) args.mixReport = path.join(DEFAULTS.reportsDir, `${reportBase}-${DEFAULTS.suffix}-mix.json`);
}

function safeName(value) {
  return String(value)
    .replace(/[^a-z0-9._-]+/gi, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 120);
}

function buildQaArgs(args) {
  const qaArgs = [
    "scripts/qa-bgm-final.js",
    "--final", args.final,
    "--output", args.output,
    "--report", args.report,
    "--selector-report", args.selectorReport,
    "--mix-report", args.mixReport,
    "--gain-percent", String(args.gainPercent),
    "--preview-seconds", String(args.previewSeconds)
  ];
  if (args.title) qaArgs.push("--title", args.title);
  if (args.transcript) qaArgs.push("--transcript", args.transcript);
  if (args.context) qaArgs.push("--context", args.context);
  if (args.dryRun) qaArgs.push("--dry-run");
  return qaArgs;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const qaArgs = buildQaArgs(args);
  const report = {
    version: 57,
    selectedFinal: args.final,
    output: args.output,
    report: args.report,
    selectorReport: args.selectorReport,
    mixReport: args.mixReport,
    gainPercent: args.gainPercent,
    previewSeconds: args.previewSeconds,
    dryRun: args.dryRun,
    command: `node ${qaArgs.map(quote).join(" ")}`
  };

  console.log(JSON.stringify(report, null, 2));
  if (args.dryRun) return;

  const result = spawnSync("node", qaArgs, {
    cwd: process.cwd(),
    stdio: "inherit"
  });
  if (result.status !== 0) {
    throw new Error(`qa-bgm-final failed with exit ${result.status}`);
  }
}

function quote(value) {
  return /[\s"'$]/.test(value) ? JSON.stringify(value) : value;
}

function printHelp() {
  console.log(`Usage:
  npm run auto:bgm -- --title "หัวข้อคลิป" --context assets/context/job.json --transcript assets/transcript.json

Options:
  --dir <path>              Directory to scan, default ${DEFAULTS.dir}
  --final <path>            Explicit final MP4; if omitted, picks newest eligible stacked-output*.mp4
  --title <text>            Clip title/topic for BGM selector
  --transcript <path>       Transcript JSON for BGM selector
  --context <path>          Context index JSON for BGM selector
  --output <path>           Mixed BGM output path
  --report <path>           Final BGM QA report
  --selector-report <path>  BGM selector report
  --mix-report <path>       BGM mix report
  --gain-percent <n>        BGM level, default ${DEFAULTS.gainPercent}
  --preview-seconds <n>     Preview duration, default ${DEFAULTS.previewSeconds}
  --include-bgm-outputs     Allow already-BGM mixed MP4s in auto-pick
  --include-previews        Allow preview MP4s in auto-pick
  --dry-run                 Print selected final and command without rendering
`);
}

try {
  main();
} catch (error) {
  console.error(`auto-final-bgm: ${error.message}`);
  process.exit(2);
}
