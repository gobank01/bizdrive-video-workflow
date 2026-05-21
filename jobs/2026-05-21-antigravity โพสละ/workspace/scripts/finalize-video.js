#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const DEFAULTS = {
  dir: "..",
  version: "v58",
  gainPercent: 5,
  previewSeconds: 20,
  reportsDir: "reports"
};

function parseArgs(argv) {
  const args = {
    dir: DEFAULTS.dir,
    final: null,
    version: DEFAULTS.version,
    title: "",
    goal: "",
    transcript: null,
    context: null,
    brollManifest: null,
    keytermReport: null,
    topSource: null,
    bottomSource: null,
    background: null,
    skipBgm: false,
    gainPercent: DEFAULTS.gainPercent,
    previewSeconds: DEFAULTS.previewSeconds,
    bgmOutput: null,
    bgmQaReport: null,
    bgmSelectorReport: null,
    bgmMixReport: null,
    finalReportJson: null,
    finalReportMarkdown: null,
    checkStatus: "",
    notes: "",
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
    } else if (arg === "--version") {
      args.version = next || DEFAULTS.version;
      i += 1;
    } else if (arg === "--title") {
      args.title = next || "";
      i += 1;
    } else if (arg === "--goal") {
      args.goal = next || "";
      i += 1;
    } else if (arg === "--transcript") {
      args.transcript = next;
      i += 1;
    } else if (arg === "--context") {
      args.context = next;
      i += 1;
    } else if (arg === "--broll-manifest") {
      args.brollManifest = next;
      i += 1;
    } else if (arg === "--keyterm-report") {
      args.keytermReport = next;
      i += 1;
    } else if (arg === "--top-source") {
      args.topSource = next;
      i += 1;
    } else if (arg === "--bottom-source") {
      args.bottomSource = next;
      i += 1;
    } else if (arg === "--background") {
      args.background = next;
      i += 1;
    } else if (arg === "--skip-bgm") {
      args.skipBgm = true;
    } else if (arg === "--gain-percent") {
      args.gainPercent = Number(next);
      i += 1;
    } else if (arg === "--preview-seconds") {
      args.previewSeconds = Number(next);
      i += 1;
    } else if (arg === "--bgm-output") {
      args.bgmOutput = next;
      i += 1;
    } else if (arg === "--bgm-qa-report") {
      args.bgmQaReport = next;
      i += 1;
    } else if (arg === "--bgm-selector-report") {
      args.bgmSelectorReport = next;
      i += 1;
    } else if (arg === "--bgm-mix-report") {
      args.bgmMixReport = next;
      i += 1;
    } else if (arg === "--final-report-json") {
      args.finalReportJson = next;
      i += 1;
    } else if (arg === "--final-report-markdown" || arg === "--final-report-md") {
      args.finalReportMarkdown = next;
      i += 1;
    } else if (arg === "--check-status") {
      args.checkStatus = next || "";
      i += 1;
    } else if (arg === "--notes") {
      args.notes = next || "";
      i += 1;
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
  if (!args.skipBgm && !args.title && !args.transcript && !args.context) {
    throw new Error("Provide --title, --transcript, and/or --context for BGM selection, or use --skip-bgm");
  }

  args.final = args.final || findLatestFinal(args.dir);
  if (!fs.existsSync(args.final)) throw new Error(`Final MP4 not found: ${args.final}`);
  fillDerivedPaths(args);
  return args;
}

function findLatestFinal(dirValue) {
  const dir = path.resolve(dirValue);
  if (!fs.existsSync(dir)) throw new Error(`Directory not found: ${dirValue}`);
  const candidates = fs.readdirSync(dir)
    .filter((name) => /^stacked-output.*\.mp4$/i.test(name))
    .filter((name) => !/-preview\d*s|preview\d+|preview/i.test(name))
    .filter((name) => !/(auto-bgm|bgm-\d+pct|default-curiosity|with-bgm|v54-auto-bgm)/i.test(name))
    .map((name) => {
      const file = path.join(dir, name);
      return { file, mtimeMs: fs.statSync(file).mtimeMs };
    })
    .sort((a, b) => b.mtimeMs - a.mtimeMs);
  if (!candidates.length) throw new Error(`No eligible stacked-output*.mp4 found in ${dirValue}`);
  return path.relative(process.cwd(), candidates[0].file);
}

function fillDerivedPaths(args) {
  const parsed = path.parse(args.final);
  const base = parsed.name;
  const reportBase = safeName(base);
  if (!args.bgmOutput) {
    args.bgmOutput = path.join(parsed.dir || ".", `${base}-auto-bgm-${args.gainPercent}pct${parsed.ext}`);
  }
  if (!args.bgmQaReport) args.bgmQaReport = path.join(DEFAULTS.reportsDir, `${reportBase}-auto-bgm-qa.json`);
  if (!args.bgmSelectorReport) args.bgmSelectorReport = path.join(DEFAULTS.reportsDir, `${reportBase}-auto-bgm-select.json`);
  if (!args.bgmMixReport) args.bgmMixReport = path.join(DEFAULTS.reportsDir, `${reportBase}-auto-bgm-mix.json`);
  if (!args.finalReportJson) args.finalReportJson = path.join(DEFAULTS.reportsDir, `${reportBase}-final-report.json`);
  if (!args.finalReportMarkdown) args.finalReportMarkdown = path.join(DEFAULTS.reportsDir, `${reportBase}-final-report.md`);
}

function safeName(value) {
  return String(value)
    .replace(/[^a-z0-9._-]+/gi, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 120);
}

function autoBgmArgs(args) {
  const command = [
    "scripts/auto-final-bgm.js",
    "--final", args.final,
    "--output", args.bgmOutput,
    "--report", args.bgmQaReport,
    "--selector-report", args.bgmSelectorReport,
    "--mix-report", args.bgmMixReport,
    "--gain-percent", String(args.gainPercent),
    "--preview-seconds", String(args.previewSeconds)
  ];
  if (args.title) command.push("--title", args.title);
  if (args.transcript) command.push("--transcript", args.transcript);
  if (args.context) command.push("--context", args.context);
  return command;
}

function reportArgs(args) {
  const finalForReport = args.skipBgm ? args.final : args.bgmOutput;
  const command = [
    "scripts/final-report.js",
    "--final", finalForReport,
    "--version", args.version,
    "--json", args.finalReportJson,
    "--markdown", args.finalReportMarkdown
  ];
  pushPair(command, "--title", args.title);
  pushPair(command, "--goal", args.goal);
  pushPair(command, "--top-source", args.topSource);
  pushPair(command, "--bottom-source", args.bottomSource);
  pushPair(command, "--background", args.background);
  pushPair(command, "--context", args.context);
  pushPair(command, "--broll-manifest", args.brollManifest);
  pushPair(command, "--keyterm-report", args.keytermReport);
  pushPair(command, "--check-status", args.checkStatus);
  pushPair(command, "--notes", args.notes);
  if (!args.skipBgm) {
    pushPair(command, "--bgm-qa", args.bgmQaReport);
    pushPair(command, "--bgm-select", args.bgmSelectorReport);
    pushPair(command, "--bgm-mix", args.bgmMixReport);
  }
  return command;
}

function pushPair(command, flag, value) {
  if (value) command.push(flag, value);
}

function runNode(command) {
  const result = spawnSync("node", command, {
    cwd: process.cwd(),
    stdio: "inherit"
  });
  if (result.status !== 0) throw new Error(`${command[0]} failed with exit ${result.status}`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const bgmCommand = args.skipBgm ? null : autoBgmArgs(args);
  const finalReportCommand = reportArgs(args);
  const plan = {
    version: 58,
    selectedFinal: args.final,
    bgmEnabled: !args.skipBgm,
    bgmOutput: args.skipBgm ? null : args.bgmOutput,
    bgmQaReport: args.skipBgm ? null : args.bgmQaReport,
    finalReportJson: args.finalReportJson,
    finalReportMarkdown: args.finalReportMarkdown,
    commands: {
      autoBgm: bgmCommand ? `node ${bgmCommand.map(quote).join(" ")}` : null,
      finalReport: `node ${finalReportCommand.map(quote).join(" ")}`
    },
    dryRun: args.dryRun
  };
  console.log(JSON.stringify(plan, null, 2));
  if (args.dryRun) return;

  if (bgmCommand) runNode(bgmCommand);
  runNode(finalReportCommand);
}

function quote(value) {
  return /[\s"'$]/.test(value) ? JSON.stringify(value) : value;
}

function printHelp() {
  console.log(`Usage:
  npm run finalize:video -- --title "หัวข้อคลิป" --context assets/context/job.json --transcript assets/transcript.json --broll-manifest assets/broll/optimized/job/manifest.json

Options:
  --dir <path>                    Directory to scan, default ${DEFAULTS.dir}
  --final <path>                  Explicit final MP4; if omitted, picks newest eligible stacked-output*.mp4
  --version <text>                Final report version, default ${DEFAULTS.version}
  --title <text>                  Clip title/topic
  --goal <text>                   User goal
  --transcript <path>             Transcript JSON for BGM selection
  --context <path>                Context index JSON
  --broll-manifest <path>         B-roll manifest JSON
  --keyterm-report <path>         Key term QA JSON
  --top-source <path>             Raw/clean top source
  --bottom-source <path>          Raw/clean bottom source
  --background <path>             Background PNG
  --skip-bgm                      Only write final report
  --gain-percent <n>              BGM level, default ${DEFAULTS.gainPercent}
  --preview-seconds <n>           Preview duration, default ${DEFAULTS.previewSeconds}
  --bgm-output <path>             BGM mixed output MP4
  --bgm-qa-report <path>          BGM QA JSON
  --bgm-selector-report <path>    BGM selector JSON
  --bgm-mix-report <path>         BGM mix JSON
  --final-report-json <path>      Final report JSON
  --final-report-markdown <path>  Final report Markdown
  --check-status <text>           npm run check result summary
  --notes <text>                  Extra report notes
  --dry-run                       Print plan without rendering/mixing/reporting
`);
}

try {
  main();
} catch (error) {
  console.error(`finalize-video: ${error.message}`);
  process.exit(2);
}
