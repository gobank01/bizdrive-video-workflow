#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const DEFAULTS = {
  html: "index.html",
  output: null,
};

function parseArgs(argv) {
  const args = { ...DEFAULTS };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--html") {
      args.html = next;
      i += 1;
    } else if (arg === "--output") {
      args.output = next;
      i += 1;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }
  if (!fs.existsSync(args.html)) throw new Error(`HTML not found: ${args.html}`);
  return args;
}

function attr(tag, name) {
  const match = tag.match(new RegExp(`${name}="([^"]*)"`));
  return match ? match[1] : null;
}

function hasClass(tag, className) {
  return (attr(tag, "class") || "").split(/\s+/).includes(className);
}

function videoTags(html) {
  return [...html.matchAll(/<video\b[^>]*>/g)].map((match) => match[0]);
}

function scriptBlocks(html) {
  return [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)].map((match) => match[1]);
}

function validate(html) {
  const issues = [];
  const videos = videoTags(html);
  const topVideo = videos.find((tag) => attr(tag, "id") === "topVideo");
  const bottomVideo = videos.find((tag) => attr(tag, "id") === "bottomVideo");
  const brollVideos = videos.filter((tag) => hasClass(tag, "broll-frame"));
  const motionVideos = videos.filter((tag) => attr(tag, "data-motion-kind"));

  if (!html.includes('id="topFrameShell"')) {
    issues.push("Missing fixed topFrameShell wrapper for border-stable inner-media motion.");
  }
  if (!topVideo) issues.push("Missing topVideo.");
  if (!bottomVideo) issues.push("Missing bottomVideo.");
  if (topVideo && (hasClass(topVideo, "video-frame") || hasClass(topVideo, "top-frame"))) {
    issues.push("topVideo must be an inner media layer, not the border/frame element.");
  }
  for (const tag of brollVideos) {
    const id = attr(tag, "id") || "unknown-broll";
    if (!hasClass(tag, "top-media")) issues.push(`${id}: B-roll must animate as top-media inside the fixed shell.`);
    if (hasClass(tag, "video-frame") || hasClass(tag, "top-frame")) {
      issues.push(`${id}: B-roll must not carry frame/border classes.`);
    }
  }
  for (const tag of motionVideos) {
    const id = attr(tag, "id") || "unknown-motion";
    if (!hasClass(tag, "top-media")) {
      issues.push(`${id}: motion is only allowed on top-media inner layers.`);
    }
    if (id === "bottomVideo" || hasClass(tag, "bottom-frame")) {
      issues.push(`${id}: bottom frame/video must not have motion metadata.`);
    }
  }

  const scripts = scriptBlocks(html).join("\n");
  const forbiddenTargets = ["#topFrameShell", ".top-frame-shell", "#bottomVideo", ".bottom-frame"];
  const transformProps = /\b(scale|x|y|xPercent|yPercent|rotation|rotationX|rotationY|skewX|skewY|transform)\b/;
  for (const target of forbiddenTargets) {
    const targetIndex = scripts.indexOf(target);
    if (targetIndex === -1) continue;
    const snippet = scripts.slice(Math.max(0, targetIndex - 160), targetIndex + 320);
    if (transformProps.test(snippet)) {
      issues.push(`${target}: frame/bottom transform animation is forbidden.`);
    }
  }

  return {
    version: 62,
    status: issues.length ? "fail" : "pass",
    checked: {
      topFrameShell: html.includes('id="topFrameShell"'),
      brollCount: brollVideos.length,
      motionVideoCount: motionVideos.length,
      bottomMotionForbidden: true,
      frameTransformForbidden: true,
    },
    issues,
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const html = fs.readFileSync(args.html, "utf8");
  const report = validate(html);
  const output = JSON.stringify(report, null, 2);
  console.log(output);
  if (args.output) {
    fs.mkdirSync(path.dirname(args.output), { recursive: true });
    fs.writeFileSync(args.output, `${output}\n`);
  }
  if (report.issues.length) process.exit(1);
}

function printHelp() {
  console.log(`Usage:
  npm run check:motion -- --html index.html --output reports/motion-safety.json

Options:
  --html <path>    Composition HTML, default ${DEFAULTS.html}
  --output <path>  Optional JSON report path
`);
}

try {
  main();
} catch (error) {
  console.error(`check-motion-safety: ${error.message}`);
  process.exit(2);
}
