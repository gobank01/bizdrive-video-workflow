#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const DEFAULTS = {
  index: "bgm-library/mixkit-stock-v50.json",
  styleKeywords: "bgm-library/style-keywords-v53.json",
  gainPercent: 5,
  top: 3
};

function parseArgs(argv) {
  const args = {
    title: "",
    transcript: null,
    context: null,
    index: DEFAULTS.index,
    styleKeywords: DEFAULTS.styleKeywords,
    output: null,
    gainPercent: DEFAULTS.gainPercent,
    top: DEFAULTS.top
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--title") {
      args.title = next || "";
      i += 1;
    } else if (arg === "--transcript") {
      args.transcript = next;
      i += 1;
    } else if (arg === "--context") {
      args.context = next;
      i += 1;
    } else if (arg === "--index") {
      args.index = next;
      i += 1;
    } else if (arg === "--style-keywords") {
      args.styleKeywords = next;
      i += 1;
    } else if (arg === "--output") {
      args.output = next;
      i += 1;
    } else if (arg === "--gain-percent") {
      args.gainPercent = Number(next);
      i += 1;
    } else if (arg === "--top") {
      args.top = Number(next);
      i += 1;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }

  if (!args.title && !args.transcript && !args.context) {
    throw new Error("Provide --title, --transcript, and/or --context");
  }
  if (!Number.isFinite(args.gainPercent) || args.gainPercent <= 0 || args.gainPercent > 100) {
    throw new Error("Invalid --gain-percent; use > 0 and <= 100");
  }
  if (!Number.isFinite(args.top) || args.top < 1) {
    throw new Error("Invalid --top");
  }
  return args;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function transcriptText(file) {
  if (!file) return "";
  const json = readJson(file);
  if (typeof json === "string") return json;
  if (Array.isArray(json)) return json.map(itemText).join("\n");
  if (Array.isArray(json.transcription)) return json.transcription.map(itemText).join("\n");
  if (Array.isArray(json.segments)) return json.segments.map(itemText).join("\n");
  if (typeof json.text === "string") return json.text;
  return JSON.stringify(json);
}

function contextText(file) {
  if (!file) return "";
  const json = readJson(file);
  const parts = [
    json.goal,
    json.strategy,
    json.screenSampling?.summary
  ];

  for (const key of ["keptSegments", "droppedSegments"]) {
    if (!Array.isArray(json[key])) continue;
    for (const item of json[key]) {
      parts.push(
        item.id,
        item.speech,
        item.text,
        item.topic,
        item.intent,
        item.screenContext,
        item.brollKeyword,
        item.brollQuery,
        item.keepReason,
        item.dropReason
      );
      for (const listKey of ["captionKeywords", "keyTermsIncluded"]) {
        if (Array.isArray(item[listKey])) parts.push(item[listKey].join(" "));
      }
    }
  }

  if (Array.isArray(json.brollSlots)) {
    for (const slot of json.brollSlots) {
      parts.push(slot.keyword, slot.query, slot.beforeSpeech, slot.afterSpeech, slot.reason);
    }
  }

  return parts.filter(Boolean).join("\n");
}

function itemText(item) {
  if (typeof item === "string") return item;
  return item?.text || item?.speech || "";
}

function normalize(text) {
  return String(text || "")
    .normalize("NFKC")
    .toLowerCase()
    .replace(/&amp;/g, "&")
    .replace(/[-_/]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function countMatches(text, keywords) {
  const haystack = normalize(text);
  const hits = [];
  let score = 0;
  for (const keyword of keywords) {
    const needle = normalize(keyword);
    if (!needle) continue;
    if (haystack.includes(needle)) {
      hits.push(keyword);
      score += needle.includes(" ") ? 2 : 1;
    }
  }
  return { score, hits };
}

function detectStyles({ title, transcript, context }, keywordConfig) {
  const styles = keywordConfig.styles || {};
  const result = {};

  for (const [style, config] of Object.entries(styles)) {
    const keywords = config.keywords || [];
    const titleMatch = countMatches(title, keywords);
    const contextMatch = countMatches(context, keywords);
    const transcriptMatch = countMatches(transcript, keywords);
    const score = titleMatch.score * 4 + contextMatch.score * 2 + transcriptMatch.score;
    result[style] = {
      style,
      score,
      intent: config.intent,
      hits: {
        title: titleMatch.hits,
        context: contextMatch.hits,
        transcript: transcriptMatch.hits.slice(0, 12)
      }
    };
  }

  return Object.values(result).sort((a, b) => b.score - a.score || a.style.localeCompare(b.style));
}

function trackScore(track, selectedStyle, styleScores, allText) {
  let score = 0;
  const reasons = [];

  if (track.bestFor?.includes(selectedStyle)) {
    score += 100;
    reasons.push(`bestFor includes ${selectedStyle}`);
  }

  for (const style of styleScores.slice(0, 3)) {
    if (style.score <= 0) continue;
    if (track.bestFor?.includes(style.style)) {
      const add = Math.min(45, style.score * 4);
      score += add;
      reasons.push(`matches detected style ${style.style} (+${add})`);
    }
  }

  const text = [
    track.title,
    track.artist,
    ...(track.tags || []),
    ...(track.mood || []),
    ...(track.bestFor || []),
    track.energy,
    track.notes
  ].join(" ");
  const metadataMatch = countMatches(allText, [
    ...(track.tags || []),
    ...(track.mood || []),
    ...(track.bestFor || [])
  ]);
  if (metadataMatch.score > 0) {
    const add = Math.min(20, metadataMatch.score * 2);
    score += add;
    reasons.push(`metadata/context overlap: ${metadataMatch.hits.slice(0, 5).join(", ")}`);
  }

  if (selectedStyle === "default_fallback" && track.id) {
    score -= energyPenalty(track.energy);
    reasons.push("unclear style: prefer lower-energy fallback");
  } else if (["tutorial_screen", "calm_learning", "finance_business"].includes(selectedStyle)) {
    score -= energyPenalty(track.energy);
    if (energyPenalty(track.energy) > 0) reasons.push("speech-heavy style: penalize higher energy");
  } else if (selectedStyle === "high_energy_recap") {
    score += highEnergyBonus(track.energy);
    if (highEnergyBonus(track.energy) > 0) reasons.push("recap style: higher energy is acceptable");
  }

  if (normalize(text).includes("vocal") || normalize(text).includes("sexy")) {
    score -= 20;
    reasons.push("possible distraction tag penalty");
  }

  return { score, reasons };
}

function energyPenalty(energy = "") {
  const normalized = normalize(energy);
  if (normalized.includes("very low")) return 0;
  if (normalized.includes("low medium")) return 0;
  if (normalized === "low") return 0;
  if (normalized === "medium") return 4;
  if (normalized.includes("medium high")) return 16;
  if (normalized.includes("high")) return 24;
  return 6;
}

function highEnergyBonus(energy = "") {
  const normalized = normalize(energy);
  if (normalized.includes("medium high")) return 10;
  if (normalized === "medium") return 6;
  if (normalized.includes("very low")) return -8;
  if (normalized === "low") return -4;
  return 0;
}

function pickFallback(library, style) {
  const fallbackId = style === "tech_explainer"
    ? library.techFallbackTrackId
    : style === "calm_learning" || style === "tutorial_screen"
      ? library.calmFallbackTrackId
      : library.defaultFallbackTrackId;
  return library.tracks.find((track) => track.id === fallbackId) || library.tracks.find((track) => track.id === library.defaultFallbackTrackId);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const library = readJson(args.index);
  const keywordConfig = readJson(args.styleKeywords);
  const transcript = transcriptText(args.transcript);
  const context = contextText(args.context);
  const title = args.title;
  const allText = [title, context, transcript].filter(Boolean).join("\n");
  const styleScores = detectStyles({ title, transcript, context }, keywordConfig);
  const minimumStyleScore = Number(keywordConfig.minimumStyleScore || 1);
  const bestStyle = styleScores[0]?.score >= minimumStyleScore ? styleScores[0].style : "default_fallback";
  const fallback = pickFallback(library, bestStyle);

  const rankedTracks = library.tracks
    .map((track) => {
      const scored = trackScore(track, bestStyle, styleScores, allText);
      if (track.id === fallback?.id) {
        scored.score += bestStyle === "default_fallback" ? 80 : 8;
        scored.reasons.push(`fallback fit: ${track.id}`);
      }
      return { ...track, score: Number(scored.score.toFixed(2)), reasons: scored.reasons };
    })
    .sort((a, b) => b.score - a.score || a.energy.localeCompare(b.energy) || a.id.localeCompare(b.id));

  const selected = rankedTracks[0] || fallback;
  const report = {
    version: 53,
    title,
    transcript: args.transcript,
    context: args.context,
    index: args.index,
    styleKeywords: args.styleKeywords,
    minimumStyleScore,
    selectedStyle: bestStyle,
    styleScores,
    selectedTrack: selected ? trackReport(selected) : null,
    alternatives: rankedTracks.slice(1, args.top).map(trackReport),
    mixDefaults: {
      gainPercent: args.gainPercent,
      audibilityIntent: "barely audible ambient bed, felt more than heard",
      sourcePolicy: library.licensePolicy,
      licenseUrl: library.licenseUrl
    },
    suggestedMixCommand: selected
      ? `npm run mix:bgm -- --voice <final-or-bottom-source.mp4> --bgm ${selected.localPath} --output <output-with-bgm.mp4> --report reports/bgm-mix-v53.json --gain-percent ${args.gainPercent}`
      : null
  };

  const output = `${JSON.stringify(report, null, 2)}\n`;
  console.log(output);
  if (args.output) {
    fs.mkdirSync(path.dirname(args.output), { recursive: true });
    fs.writeFileSync(args.output, output);
  }
}

function trackReport(track) {
  return {
    id: track.id,
    title: track.title,
    artist: track.artist,
    localPath: track.localPath,
    sourcePage: track.sourcePage,
    licenseUrl: "https://mixkit.co/license/",
    energy: track.energy,
    mood: track.mood,
    bestFor: track.bestFor,
    score: track.score,
    reasons: track.reasons,
    notes: track.notes
  };
}

function printHelp() {
  console.log(`Usage:
  npm run select:bgm -- --title "ใช้ AI ตัดต่อคลิป" --context assets/context/test2-v35-full-context-index.json
  npm run select:bgm -- --transcript assets/transcript_test2.large-v3.json --output reports/bgm-select-v53.json

Options:
  --title <text>           Clip title/topic
  --transcript <path>      Whisper/transcript JSON
  --context <path>         Context index JSON
  --index <path>           BGM stock index, default ${DEFAULTS.index}
  --style-keywords <path>  Editable style keyword map, default ${DEFAULTS.styleKeywords}
  --gain-percent <number>  Suggested mix level, default 5
  --top <number>           Number of choices to include, default 3
  --output <path>          Write JSON report
`);
}

try {
  main();
} catch (error) {
  console.error(`select-bgm: ${error.message}`);
  process.exit(2);
}
