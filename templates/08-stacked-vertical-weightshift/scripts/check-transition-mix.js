#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const DEFAULTS = {
  html: "index.html",
  context: "assets/context/test2-v35-full-context-index.json",
  output: null,
  minStartGap: 6,
  minTopGap: 3
};

function parseArgs(argv) {
  const args = { ...DEFAULTS };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--html") {
      args.html = next;
      i += 1;
    } else if (arg === "--context") {
      args.context = next;
      i += 1;
    } else if (arg === "--output") {
      args.output = next;
      i += 1;
    } else if (arg === "--min-start-gap") {
      args.minStartGap = Number(next);
      i += 1;
    } else if (arg === "--min-top-gap") {
      args.minTopGap = Number(next);
      i += 1;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }
  if (!fs.existsSync(args.html)) throw new Error(`HTML not found: ${args.html}`);
  if (!Number.isFinite(args.minStartGap) || args.minStartGap <= 0) {
    throw new Error("--min-start-gap must be a positive number");
  }
  if (!Number.isFinite(args.minTopGap) || args.minTopGap < 0) {
    throw new Error("--min-top-gap must be zero or a positive number");
  }
  return args;
}

function readOptionalJson(file) {
  if (!file || !fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function parseBrollTags(html) {
  const tags = [];
  const pattern = /<video\b[^>]*>/g;
  for (const match of html.matchAll(pattern)) {
    const tag = match[0];
    const klass = attr(tag, "class") || "";
    if (!klass.split(/\s+/).includes("broll-frame")) continue;
    tags.push({
      id: attr(tag, "id"),
      start: numberAttr(tag, "data-start"),
      duration: numberAttr(tag, "data-duration"),
      mode: attr(tag, "data-transition-mode"),
      inDuration: numberAttr(tag, "data-transition-in"),
      outDuration: numberAttr(tag, "data-transition-out"),
      panFrom: attr(tag, "data-pan-from"),
      panTo: attr(tag, "data-pan-to"),
      trackIndex: numberAttr(tag, "data-track-index")
    });
  }
  return tags;
}

function attr(tag, name) {
  const match = tag.match(new RegExp(`${name}="([^"]*)"`));
  return match ? match[1] : null;
}

function numberAttr(tag, name) {
  const value = attr(tag, name);
  if (value === null) return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function validate(tags, context, args) {
  const issues = [];
  const contextSlots = new Map((context?.brollSlots || []).map((slot) => [slot.id, slot]));
  const seenTrackIndexes = new Set();

  for (const tag of tags) {
    const label = tag.id || "unknown";
    if (!tag.id) issues.push("B-roll tag missing id");
    if (!Number.isFinite(tag.start)) issues.push(`${label}: missing/invalid data-start`);
    if (!Number.isFinite(tag.duration) || tag.duration <= 0) issues.push(`${label}: missing/invalid data-duration`);
    if (!["soft", "bridge"].includes(tag.mode)) issues.push(`${label}: transition mode must be soft or bridge`);
    if (!Number.isFinite(tag.inDuration) || tag.inDuration <= 0) issues.push(`${label}: missing/invalid transition-in`);
    if (!Number.isFinite(tag.outDuration) || tag.outDuration <= 0) issues.push(`${label}: missing/invalid transition-out`);
    if (Number.isFinite(tag.duration)) {
      if (tag.inDuration > tag.duration / 3) issues.push(`${label}: transition-in too long for clip duration`);
      if (tag.outDuration > tag.duration / 3) issues.push(`${label}: transition-out too long for clip duration`);
    }
    if (!tag.panFrom || !tag.panTo) issues.push(`${label}: missing pan metadata`);
    if (tag.panFrom === tag.panTo) issues.push(`${label}: pan metadata should move subtly, not stay identical`);
    if (seenTrackIndexes.has(tag.trackIndex)) issues.push(`${label}: duplicate data-track-index ${tag.trackIndex}`);
    seenTrackIndexes.add(tag.trackIndex);

    const contextSlot = contextSlots.get(tag.id);
    if (contextSlot?.coverCut && tag.mode !== "bridge") {
      issues.push(`${label}: coverCut slot should use bridge transition`);
    }
  }

  const sortedTags = tags
    .filter((tag) => Number.isFinite(tag.start) && Number.isFinite(tag.duration))
    .slice()
    .sort((a, b) => a.start - b.start);
  for (let index = 1; index < sortedTags.length; index += 1) {
    const previous = sortedTags[index - 1];
    const current = sortedTags[index];
    const startGap = current.start - previous.start;
    const topGap = current.start - (previous.start + previous.duration);
    if (startGap < args.minStartGap - 0.001) {
      issues.push(
        `${previous.id}->${current.id}: B-roll starts are too close (${startGap.toFixed(2)}s < ${args.minStartGap}s)`,
      );
    }
    if (topGap < args.minTopGap - 0.001) {
      issues.push(
        `${previous.id}->${current.id}: real top footage gap is too short (${topGap.toFixed(2)}s < ${args.minTopGap}s)`,
      );
    }
  }

  return issues;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const html = fs.readFileSync(args.html, "utf8");
  const context = readOptionalJson(args.context);
  const tags = parseBrollTags(html);
  const issues = validate(tags, context, args);
  const bridgeCount = tags.filter((tag) => tag.mode === "bridge").length;
  const softCount = tags.filter((tag) => tag.mode === "soft").length;
  const report = {
    version: 61,
    status: issues.length ? "fail" : "pass",
    html: args.html,
    context: context ? args.context : null,
    brollCount: tags.length,
    softCount,
    bridgeCount,
    defaults: {
      softTransitionSeconds: 0.22,
      bridgeTransitionSeconds: 0.26,
      minBrollStartGapSeconds: args.minStartGap,
      minRealTopFootageGapSeconds: args.minTopGap,
      borderStable: true,
      bottomUnaffected: true
    },
    slots: tags,
    issues
  };
  const output = JSON.stringify(report, null, 2);
  console.log(output);
  if (args.output) {
    fs.mkdirSync(path.dirname(args.output), { recursive: true });
    fs.writeFileSync(args.output, `${output}\n`);
  }
  if (issues.length) process.exit(1);
}

function printHelp() {
  console.log(`Usage:
  npm run check:transition -- --html index.html --context assets/context/test2-v35-full-context-index.json

Options:
  --html <path>     Composition HTML, default ${DEFAULTS.html}
  --context <path>  Optional context index used to validate bridge slots
  --output <path>   Optional JSON report path
  --min-start-gap <seconds>  Hard minimum between B-roll starts, default ${DEFAULTS.minStartGap}
  --min-top-gap <seconds>    Hard minimum real top footage between B-rolls, default ${DEFAULTS.minTopGap}
`);
}

try {
  main();
} catch (error) {
  console.error(`check-transition-mix: ${error.message}`);
  process.exit(2);
}
