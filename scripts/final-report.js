#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const DEFAULTS = {
  version: "v56",
  json: "reports/final-report-v56.json",
  markdown: "reports/final-report-v56.md"
};

function parseArgs(argv) {
  const args = {
    final: null,
    version: DEFAULTS.version,
    title: "",
    goal: "",
    topSource: null,
    bottomSource: null,
    background: null,
    context: null,
    brollManifest: null,
    bgmQa: null,
    bgmSelect: null,
    bgmMix: null,
    keytermReport: null,
    checkStatus: "",
    notes: "",
    json: DEFAULTS.json,
    markdown: DEFAULTS.markdown
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--final" || arg === "--output") {
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
    } else if (arg === "--top-source") {
      args.topSource = next;
      i += 1;
    } else if (arg === "--bottom-source") {
      args.bottomSource = next;
      i += 1;
    } else if (arg === "--background") {
      args.background = next;
      i += 1;
    } else if (arg === "--context") {
      args.context = next;
      i += 1;
    } else if (arg === "--broll-manifest") {
      args.brollManifest = next;
      i += 1;
    } else if (arg === "--bgm-qa") {
      args.bgmQa = next;
      i += 1;
    } else if (arg === "--bgm-select") {
      args.bgmSelect = next;
      i += 1;
    } else if (arg === "--bgm-mix") {
      args.bgmMix = next;
      i += 1;
    } else if (arg === "--keyterm-report") {
      args.keytermReport = next;
      i += 1;
    } else if (arg === "--check-status") {
      args.checkStatus = next || "";
      i += 1;
    } else if (arg === "--notes") {
      args.notes = next || "";
      i += 1;
    } else if (arg === "--json") {
      args.json = next || DEFAULTS.json;
      i += 1;
    } else if (arg === "--markdown" || arg === "--md") {
      args.markdown = next || DEFAULTS.markdown;
      i += 1;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }

  if (!args.final && args.bgmQa && fs.existsSync(args.bgmQa)) {
    const bgmQa = readJson(args.bgmQa);
    args.final = bgmQa.bgmOutput || bgmQa.finalInput || null;
  }
  if (!args.final) throw new Error("Missing --final");
  if (!fs.existsSync(args.final)) throw new Error(`Final MP4 not found: ${args.final}`);
  return args;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function readOptionalJson(file) {
  if (!file) return null;
  if (!fs.existsSync(file)) return { missing: true, path: file };
  return readJson(file);
}

function ffprobe(file) {
  return JSON.parse(execFileSync("ffprobe", [
    "-v",
    "error",
    "-show_entries",
    "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,sample_rate,channels,start_time,duration,nb_frames,r_frame_rate,avg_frame_rate",
    "-of",
    "json",
    file
  ], { encoding: "utf8" }));
}

function fileSizeMb(bytes) {
  const value = Number(bytes);
  if (!Number.isFinite(value)) return null;
  return Number((value / 1024 / 1024).toFixed(2));
}

function seconds(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return null;
  return Number(number.toFixed(2));
}

function summarizeMetadata(metadata) {
  const video = metadata.streams?.find((stream) => stream.codec_type === "video");
  const audio = metadata.streams?.find((stream) => stream.codec_type === "audio");
  return {
    durationSeconds: seconds(metadata.format?.duration),
    sizeBytes: metadata.format?.size ? Number(metadata.format.size) : null,
    sizeMb: fileSizeMb(metadata.format?.size),
    bitRate: metadata.format?.bit_rate ? Number(metadata.format.bit_rate) : null,
    video: video ? {
      codec: video.codec_name,
      width: video.width,
      height: video.height,
      frames: video.nb_frames ? Number(video.nb_frames) : null,
      duration: seconds(video.duration),
      startTime: seconds(video.start_time),
      frameRate: video.avg_frame_rate || video.r_frame_rate || null
    } : null,
    audio: audio ? {
      codec: audio.codec_name,
      sampleRate: audio.sample_rate ? Number(audio.sample_rate) : null,
      channels: audio.channels ?? null,
      duration: seconds(audio.duration),
      startTime: seconds(audio.start_time)
    } : null
  };
}

function summarizeContext(context, contextPath) {
  if (!context || context.missing) return null;
  const kept = Array.isArray(context.keptSegments) ? context.keptSegments : [];
  const dropped = Array.isArray(context.droppedSegments) ? context.droppedSegments : [];
  const brollSlots = Array.isArray(context.brollSlots) ? context.brollSlots : [];
  return {
    path: contextPath,
    version: context.version ?? null,
    setId: context.setId ?? null,
    goal: context.goal ?? null,
    strategy: context.strategy ?? null,
    originalDuration: seconds(context.originalDuration),
    outputDuration: seconds(context.outputDuration ?? context.compositionDuration),
    xfadeSeconds: context.xfadeSeconds ?? null,
    keptSegmentCount: kept.length,
    droppedSegmentCount: dropped.length,
    droppedSeconds: seconds(dropped.reduce((sum, item) => sum + Number(item.duration || 0), 0)),
    keptSegments: kept.map((item) => ({
      id: item.id,
      newStart: seconds(item.newStart),
      newEnd: seconds(item.newEnd),
      originalStart: seconds(item.originalStart ?? item.start),
      originalEnd: seconds(item.originalEnd ?? item.end),
      topic: item.topic,
      keepReason: item.keepReason,
      cutRisk: item.cutRisk
    })),
    brollSlotCount: brollSlots.length
  };
}

function summarizeBroll(manifest, context, manifestPath) {
  const contextSlots = Array.isArray(context?.brollSlots) ? context.brollSlots : [];
  if (!manifest || manifest.missing) {
    return {
      manifest: manifestPath || null,
      source: contextSlots.length ? "context-index" : "none",
      counts: {
        newStockDownloads: null,
        newAiGenerations: null,
        reusedSources: null,
        optimizedDerivatives: contextSlots.length || null,
        rejectedCandidates: null
      },
      qaStatus: contextSlots.length && contextSlots.every((slot) => slot.qaStatus === "pass") ? "pass" : "unknown",
      slots: contextSlots.map(normalizeBrollSlot)
    };
  }

  const summary = manifest.summary || {};
  const slots = Array.isArray(manifest.slots) ? manifest.slots : [];
  const rejected = Array.isArray(manifest.rejectedCandidates) ? manifest.rejectedCandidates : [];
  return {
    manifest: manifestPath,
    source: "manifest",
    version: manifest.version ?? null,
    setId: manifest.setId ?? null,
    counts: {
      newStockDownloads: summary.externalDownloadsNew ?? summary.newStockDownloads ?? null,
      newAiGenerations: summary.openRouterGenerationsNew ?? summary.newAiGenerations ?? 0,
      reusedSources: summary.reusedSourceCount ?? null,
      optimizedDerivatives: summary.optimizedDerivativeCount ?? slots.length,
      rejectedCandidates: summary.rejectedCandidateCount ?? rejected.length
    },
    qaRule: manifest.qaRule ?? null,
    qaStatus: slots.length && slots.every((slot) => isPassStatus(slot.qaStatus)) ? "pass" : "review",
    slots: slots.map(normalizeBrollSlot),
    rejectedCandidates: rejected.map((item) => ({
      slot: item.slot,
      candidate: item.candidate,
      keyword: item.keyword,
      path: item.path,
      qaReason: item.qaReason
    }))
  };
}

function normalizeBrollSlot(slot) {
  return {
    slot: slot.slot,
    start: seconds(slot.start),
    duration: seconds(slot.duration),
    keyword: slot.keyword,
    query: slot.query,
    provider: slot.provider,
    source: slot.source,
    output: slot.output,
    usage: slot.usage ?? null,
    coverCut: slot.coverCut ?? null,
    transitionMix: slot.transitionMix ?? null,
    contextSegment: slot.contextSegment,
    qaStatus: slot.qaStatus ?? "unknown",
    sourceUrl: slot.sourceUrl ?? null,
    photographer: slot.photographer ?? null
  };
}

function summarizeBgm(bgmQa, bgmSelect, bgmMix, paths) {
  const selectedTrack = bgmQa?.selectedTrack || bgmSelect?.selectedTrack || null;
  return {
    enabled: Boolean(bgmQa || bgmSelect || bgmMix),
    qaReport: paths.bgmQa || null,
    selectorReport: paths.bgmSelect || bgmQa?.selectorReport || null,
    mixReport: paths.bgmMix || bgmQa?.mixReport || null,
    selectedStyle: bgmQa?.selectedStyle || bgmSelect?.selectedStyle || null,
    selectedTrack: selectedTrack ? {
      id: selectedTrack.id,
      title: selectedTrack.title,
      artist: selectedTrack.artist,
      localPath: selectedTrack.localPath,
      licenseUrl: selectedTrack.licenseUrl,
      score: selectedTrack.score ?? null
    } : null,
    gainPercent: bgmQa?.gainPercent ?? bgmMix?.gainPercent ?? null,
    audibilityIntent: bgmQa?.audibilityIntent || "barely audible ambient bed, felt more than heard",
    originalLoudness: bgmQa?.originalLoudness || null,
    mixedLoudness: bgmQa?.mixedLoudness || null,
    frameLock: bgmQa?.frameLock || null,
    qa: bgmQa?.qa || null,
    previews: {
      original: bgmQa?.originalPreview || null,
      mixed: bgmQa?.mixedPreview || null
    },
    output: bgmQa?.bgmOutput || bgmMix?.output || null,
    mix: bgmMix ? {
      fadeIn: bgmMix.fadeIn,
      fadeOut: bgmMix.fadeOut,
      limiterLimit: bgmMix.limiterLimit,
      duck: bgmMix.duck,
      sourcePolicy: bgmMix.sourcePolicy
    } : null
  };
}

function summarizeKeyterms(report, reportPath) {
  if (!report || report.missing) return { report: reportPath || null, status: "unknown" };
  return {
    report: reportPath,
    status: report.status,
    mode: report.mode,
    requiredTerms: report.requiredTerms || [],
    missingRequired: report.missingRequired || []
  };
}

function isPassStatus(status) {
  if (!status) return false;
  return /(^|[_ -])pass(ed)?($|[_ -])/i.test(status) || /^pass$/i.test(status);
}

function buildQaSummary({ args, broll, bgm, keyterms }) {
  const issues = [];
  if (args.checkStatus && !/pass|ok|passed|ผ่าน/i.test(args.checkStatus)) {
    issues.push(`npm run check: ${args.checkStatus}`);
  }
  if (broll.qaStatus && broll.qaStatus !== "pass") issues.push(`B-roll QA: ${broll.qaStatus}`);
  if (bgm.enabled && bgm.qa?.status && bgm.qa.status !== "pass") issues.push(`BGM QA: ${bgm.qa.status}`);
  if (bgm.enabled && bgm.frameLock?.status && bgm.frameLock.status !== "pass") {
    issues.push(`BGM frame lock: ${bgm.frameLock.status}`);
  }
  if (keyterms.status && !["pass", "unknown"].includes(keyterms.status)) {
    issues.push(`Key term QA: ${keyterms.status}`);
  }
  return {
    status: issues.length ? "review" : "pass",
    issues,
    npmRunCheck: args.checkStatus || "not recorded",
    brollQa: broll.qaStatus || "unknown",
    bgmQa: bgm.qa?.status || (bgm.enabled ? "unknown" : "disabled"),
    keytermQa: keyterms.status || "unknown"
  };
}

function buildReport(args) {
  const metadata = summarizeMetadata(ffprobe(args.final));
  const context = readOptionalJson(args.context);
  const brollManifest = readOptionalJson(args.brollManifest);
  const bgmQa = readOptionalJson(args.bgmQa);
  const bgmSelect = readOptionalJson(args.bgmSelect || bgmQa?.selectorReport);
  const bgmMix = readOptionalJson(args.bgmMix || bgmQa?.mixReport);
  const keytermReport = readOptionalJson(args.keytermReport);

  const contextSummary = summarizeContext(context, args.context);
  const broll = summarizeBroll(brollManifest, context, args.brollManifest);
  const bgm = summarizeBgm(bgmQa, bgmSelect, bgmMix, {
    bgmQa: args.bgmQa,
    bgmSelect: args.bgmSelect,
    bgmMix: args.bgmMix
  });
  const keyterms = summarizeKeyterms(keytermReport, args.keytermReport);
  const qa = buildQaSummary({ args, broll, bgm, keyterms });

  return {
    version: args.version,
    createdAt: new Date().toISOString(),
    title: args.title || bgmQa?.title || "",
    goal: args.goal || context?.goal || "",
    output: args.final,
    status: qa.status,
    renderMetadata: metadata,
    sourceMedia: {
      topSource: args.topSource,
      bottomSource: args.bottomSource,
      background: args.background
    },
    context: contextSummary,
    audio: {
      master: "bottom audio",
      bgm
    },
    broll,
    captions: {
      transcript: bgmQa?.transcript || null,
      style: "Bizdrive caption spec v4.1",
      keyterms
    },
    qa,
    files: {
      context: args.context,
      brollManifest: args.brollManifest,
      bgmQa: args.bgmQa,
      bgmSelect: args.bgmSelect || bgmQa?.selectorReport || null,
      bgmMix: args.bgmMix || bgmQa?.mixReport || null,
      keytermReport: args.keytermReport,
      json: args.json,
      markdown: args.markdown
    },
    notes: args.notes
  };
}

function writeOutputs(report, args) {
  fs.mkdirSync(path.dirname(args.json), { recursive: true });
  fs.mkdirSync(path.dirname(args.markdown), { recursive: true });
  fs.writeFileSync(args.json, `${JSON.stringify(report, null, 2)}\n`);
  fs.writeFileSync(args.markdown, renderMarkdown(report));
}

function renderMarkdown(report) {
  const brollLines = report.broll.slots.map((slot) => (
    `| ${slot.slot} | ${slot.start ?? ""}s | ${slot.keyword || ""} | ${slot.provider || ""} | ${slot.transitionMix?.mode || ""} | ${slot.qaStatus || ""} | ${slot.output || ""} |`
  )).join("\n");

  return `# Final Video Report

## Summary

| Field | Value |
| --- | --- |
| Version | ${safe(report.version)} |
| Status | ${safe(report.status)} |
| Title | ${safe(report.title)} |
| Goal | ${safe(report.goal)} |
| Output | ${safe(report.output)} |
| Created At | ${safe(report.createdAt)} |

## Render Metadata

| Field | Value |
| --- | --- |
| Duration | ${safe(report.renderMetadata.durationSeconds)}s |
| Size | ${safe(report.renderMetadata.sizeMb)} MB |
| Video | ${safe(streamText(report.renderMetadata.video))} |
| Audio | ${safe(audioText(report.renderMetadata.audio))} |
| Video Frames | ${safe(report.renderMetadata.video?.frames)} |
| Video Start Time | ${safe(report.renderMetadata.video?.startTime)}s |
| Audio Start Time | ${safe(report.renderMetadata.audio?.startTime)}s |

## Context Cut

| Field | Value |
| --- | --- |
| Context | ${safe(report.files.context)} |
| Original Duration | ${safe(report.context?.originalDuration)}s |
| Output Duration | ${safe(report.context?.outputDuration)}s |
| Kept Segments | ${safe(report.context?.keptSegmentCount)} |
| Dropped Segments | ${safe(report.context?.droppedSegmentCount)} |
| Dropped Seconds | ${safe(report.context?.droppedSeconds)}s |
| Soft Cut | ${safe(report.context?.xfadeSeconds)}s crossfade |

## B-roll

| Field | Value |
| --- | --- |
| Manifest | ${safe(report.broll.manifest)} |
| New Stock Downloads | ${safe(report.broll.counts.newStockDownloads)} |
| New AI Generations | ${safe(report.broll.counts.newAiGenerations)} |
| Reused Sources | ${safe(report.broll.counts.reusedSources)} |
| Optimized Derivatives | ${safe(report.broll.counts.optimizedDerivatives)} |
| Rejected Candidates | ${safe(report.broll.counts.rejectedCandidates)} |
| QA | ${safe(report.broll.qaStatus)} |

| Slot | Start | Keyword | Provider | Transition | QA | Output |
| --- | ---: | --- | --- | --- | --- | --- |
${brollLines || "| - | - | - | - | - | - | - |"}

## Audio / BGM

| Field | Value |
| --- | --- |
| BGM Enabled | ${safe(report.audio.bgm.enabled)} |
| Selected Style | ${safe(report.audio.bgm.selectedStyle)} |
| Track | ${safe(trackText(report.audio.bgm.selectedTrack))} |
| Gain | ${safe(report.audio.bgm.gainPercent)}% |
| Intent | ${safe(report.audio.bgm.audibilityIntent)} |
| BGM QA | ${safe(report.audio.bgm.qa?.status)} |
| Original Loudness | ${safe(loudnessText(report.audio.bgm.originalLoudness))} |
| Mixed Loudness | ${safe(loudnessText(report.audio.bgm.mixedLoudness))} |
| Mixed Output | ${safe(report.audio.bgm.output)} |
| Frame Lock | ${safe(frameLockText(report.audio.bgm.frameLock))} |

## Captions / Key Terms

| Field | Value |
| --- | --- |
| Caption Style | ${safe(report.captions.style)} |
| Key Term QA | ${safe(report.captions.keyterms.status)} |
| Missing Required | ${safe((report.captions.keyterms.missingRequired || []).join(", "))} |

## QA

| Field | Value |
| --- | --- |
| Overall | ${safe(report.qa.status)} |
| npm run check | ${safe(report.qa.npmRunCheck)} |
| B-roll QA | ${safe(report.qa.brollQa)} |
| BGM QA | ${safe(report.qa.bgmQa)} |
| Key Term QA | ${safe(report.qa.keytermQa)} |

${report.qa.issues.length ? `Issues:\n\n${report.qa.issues.map((issue) => `- ${issue}`).join("\n")}\n` : "Issues: none recorded.\n"}
## Files

${Object.entries(report.files).map(([key, value]) => `- ${key}: ${value || ""}`).join("\n")}

## Notes

${report.notes || "-"}
`;
}

function safe(value) {
  if (value === null || value === undefined || value === "") return "";
  return String(value);
}

function streamText(video) {
  if (!video) return "";
  return `${video.codec} ${video.width}x${video.height} ${video.frameRate || ""}`.trim();
}

function audioText(audio) {
  if (!audio) return "";
  return `${audio.codec} ${audio.sampleRate || ""}Hz ${audio.channels || ""}ch`.trim();
}

function trackText(track) {
  if (!track) return "";
  return `${track.id || ""} ${track.title || ""}`.trim();
}

function loudnessText(value) {
  if (!value) return "";
  return `${value.integratedLufs} LUFS, true peak ${value.truePeakDbfs} dBFS`;
}

function frameLockText(value) {
  if (!value) return "";
  return `${value.status}, frames ${value.originalFrames} -> ${value.mixedFrames}, delta ${value.frameDelta}, start delta ${value.startDeltaMs}ms`;
}

function printHelp() {
  console.log(`Usage:
  npm run report:final -- --final ../final.mp4 --context assets/context/job.json --broll-manifest assets/broll/optimized/job/manifest.json

Options:
  --final <path>           Final MP4 to inspect
  --version <text>         Workflow version, default ${DEFAULTS.version}
  --title <text>           Clip title
  --goal <text>            User goal
  --top-source <path>      Source top/screen video
  --bottom-source <path>   Source bottom/face video
  --background <path>      Background PNG
  --context <path>         Full context index JSON
  --broll-manifest <path>  Selected/optimized B-roll manifest JSON
  --bgm-qa <path>          Final BGM QA JSON
  --bgm-select <path>      BGM selector JSON
  --bgm-mix <path>         BGM mix JSON
  --keyterm-report <path>  Key term QA JSON
  --check-status <text>    npm run check result summary
  --notes <text>           Extra delivery notes
  --json <path>            JSON output path, default ${DEFAULTS.json}
  --markdown <path>        Markdown output path, default ${DEFAULTS.markdown}
`);
}

try {
  const args = parseArgs(process.argv.slice(2));
  const report = buildReport(args);
  writeOutputs(report, args);
  console.log(JSON.stringify({
    status: report.status,
    output: report.output,
    json: args.json,
    markdown: args.markdown,
    brollQa: report.qa.brollQa,
    bgmQa: report.qa.bgmQa,
    keytermQa: report.qa.keytermQa
  }, null, 2));
} catch (error) {
  console.error(`final-report: ${error.message}`);
  process.exit(2);
}
