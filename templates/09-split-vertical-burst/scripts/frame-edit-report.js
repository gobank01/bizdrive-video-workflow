import fs from "node:fs";
import { execFileSync } from "node:child_process";

function parseArgs(argv) {
  const args = {
    context: "assets/context/test2-v35-full-context-index.json",
    brollManifest: "assets/broll/optimized/test2-v35/manifest.json",
    html: "index.html",
    fps: 30,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--context") args.context = argv[++i];
    else if (arg === "--broll-manifest") args.brollManifest = argv[++i];
    else if (arg === "--final") args.final = argv[++i];
    else if (arg === "--html") args.html = argv[++i];
    else if (arg === "--fps") args.fps = Number(argv[++i]);
    else if (arg === "--json") args.json = argv[++i];
  }

  if (!Number.isFinite(args.fps) || args.fps <= 0) {
    throw new Error("--fps must be a positive number");
  }

  return args;
}

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, "utf8"));
}

function secondsToFrames(seconds, fps) {
  return Math.round(seconds * fps);
}

function sumDuration(items = []) {
  return items.reduce((sum, item) => sum + Number(item.duration || 0), 0);
}

function ffprobeDuration(path) {
  if (!path) return null;
  const output = execFileSync(
    "ffprobe",
    [
      "-v",
      "error",
      "-show_entries",
      "format=duration",
      "-of",
      "default=nw=1:nk=1",
      path,
    ],
    { encoding: "utf8" },
  ).trim();
  const duration = Number(output);
  return Number.isFinite(duration) ? duration : null;
}

function attr(tag, name) {
  const match = tag.match(new RegExp(`${name}="([^"]*)"`));
  return match ? match[1] : null;
}

function motionSummary(htmlPath, finalDuration, fps) {
  if (!htmlPath || !fs.existsSync(htmlPath)) {
    return {
      html: htmlPath || null,
      visibleMotion: { seconds: 0, frames: 0 },
      topInnerMotion: { seconds: 0, frames: 0 },
      brollInnerMotion: { seconds: 0, frames: 0 },
      note: "No HTML supplied or file missing.",
    };
  }
  const html = fs.readFileSync(htmlPath, "utf8");
  const tags = [...html.matchAll(/<video\b[^>]*data-motion-kind="[^"]+"[^>]*>/g)].map((match) => match[0]);
  const topSeconds = tags
    .filter((tag) => attr(tag, "data-motion-kind") === "slow-top-inner-zoom")
    .reduce((sum, tag) => sum + Number(attr(tag, "data-motion-duration") || attr(tag, "data-duration") || 0), 0);
  const brollSeconds = tags
    .filter((tag) => attr(tag, "data-motion-kind") === "slow-broll-inner-zoom")
    .reduce((sum, tag) => sum + Number(attr(tag, "data-motion-duration") || attr(tag, "data-duration") || 0), 0);
  const visibleSeconds = Math.min(Number(finalDuration || 0), Math.max(topSeconds, brollSeconds));
  return {
    html: htmlPath,
    visibleMotion: {
      seconds: Number(visibleSeconds.toFixed(3)),
      frames: secondsToFrames(visibleSeconds, fps),
      note: "Visible top-frame area has slow inner-media movement; frame/border remains fixed.",
    },
    topInnerMotion: {
      seconds: Number(topSeconds.toFixed(3)),
      frames: secondsToFrames(topSeconds, fps),
    },
    brollInnerMotion: {
      seconds: Number(brollSeconds.toFixed(3)),
      frames: secondsToFrames(brollSeconds, fps),
    },
  };
}

function buildReport(args) {
  const context = readJson(args.context);
  const manifest = readJson(args.brollManifest);
  const fps = args.fps;

  const keptSeconds = sumDuration(context.keptSegments);
  const droppedSeconds = sumDuration(context.droppedSegments);
  const finalDuration = ffprobeDuration(args.final) ?? context.outputDuration;
  const originalDuration = Number(context.originalDuration || keptSeconds + droppedSeconds);
  const brollSeconds = sumDuration(manifest.slots);
  const transitionSeconds = (manifest.slots || []).reduce((sum, slot) => {
    const mix = slot.transitionMix || {};
    return sum + Number(mix.inDuration || 0) + Number(mix.outDuration || 0);
  }, 0);
  const softSlots = (manifest.slots || []).filter((slot) => slot.transitionMix?.mode === "soft");
  const bridgeSlots = (manifest.slots || []).filter((slot) => slot.transitionMix?.mode === "bridge");
  const softCutOverlapSeconds = Math.max(0, keptSeconds - Number(finalDuration || 0));
  const netRemovedSeconds = Math.max(0, originalDuration - Number(finalDuration || 0));

  return {
    fps,
    context: args.context,
    brollManifest: args.brollManifest,
    final: args.final || null,
    original: {
      seconds: Number(originalDuration.toFixed(3)),
      frames: secondsToFrames(originalDuration, fps),
    },
    finalOutput: {
      seconds: Number(Number(finalDuration || 0).toFixed(3)),
      frames: secondsToFrames(Number(finalDuration || 0), fps),
    },
    contentKept: {
      seconds: Number(keptSeconds.toFixed(3)),
      frames: secondsToFrames(keptSeconds, fps),
    },
    contentDropped: {
      seconds: Number(droppedSeconds.toFixed(3)),
      frames: secondsToFrames(droppedSeconds, fps),
      note: "Semantic dropped segments from context index.",
    },
    softCutOverlapRemoved: {
      seconds: Number(softCutOverlapSeconds.toFixed(3)),
      frames: secondsToFrames(softCutOverlapSeconds, fps),
      note: "Extra timeline reduction from overlapping adjacent kept segments with soft cuts.",
    },
    totalNetRemoved: {
      seconds: Number(netRemovedSeconds.toFixed(3)),
      frames: secondsToFrames(netRemovedSeconds, fps),
      note: "Original duration minus final output duration.",
    },
    visualEdits: {
      brollSlots: (manifest.slots || []).length,
      brollTopReplacement: {
        seconds: Number(brollSeconds.toFixed(3)),
        frames: secondsToFrames(brollSeconds, fps),
        note: "Frames where B-roll replaces the top frame.",
      },
      transitionMix: {
        seconds: Number(transitionSeconds.toFixed(3)),
        frames: secondsToFrames(transitionSeconds, fps),
        softSlots: softSlots.length,
        bridgeSlots: bridgeSlots.length,
        note: "Entry/exit transition frames inside B-roll slots.",
      },
      motion: motionSummary(args.html, finalDuration, fps),
    },
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const report = buildReport(args);

  if (args.json) {
    fs.writeFileSync(args.json, `${JSON.stringify(report, null, 2)}\n`);
  }

  console.log(JSON.stringify(report, null, 2));
}

main();
