#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const DEFAULT_TERMS = [
  "B-roll",
  "b roll",
  "บีโรล",
  "caption",
  "prompt",
  "Dead Air",
  "audio polish",
  "intro",
  "outro",
  "thumbnail",
  "export",
  "AI"
];

function parseArgs(argv) {
  const args = {
    mode: "warn",
    terms: DEFAULT_TERMS,
    required: [],
    transcript: null,
    context: null,
    output: null
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--transcript") {
      args.transcript = next;
      i += 1;
    } else if (arg === "--context") {
      args.context = next;
      i += 1;
    } else if (arg === "--terms") {
      args.terms = splitList(next);
      i += 1;
    } else if (arg === "--required") {
      args.required = splitList(next);
      i += 1;
    } else if (arg === "--mode") {
      args.mode = next || "warn";
      i += 1;
    } else if (arg === "--output") {
      args.output = next;
      i += 1;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }

  if (!args.transcript && !args.context) {
    throw new Error("Provide --transcript and/or --context");
  }
  if (args.required.length === 0) {
    args.required = args.terms;
  }
  return args;
}

function splitList(value = "") {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function transcriptText(file) {
  if (!file) return "";
  const json = readJson(file);
  if (typeof json === "string") return json;
  if (Array.isArray(json)) {
    return json.map((item) => item.text || item.speech || JSON.stringify(item)).join("\n");
  }
  if (Array.isArray(json.transcription)) {
    return json.transcription.map((item) => item.text || "").join("\n");
  }
  if (Array.isArray(json.segments)) {
    return json.segments.map((item) => item.text || item.speech || "").join("\n");
  }
  if (typeof json.text === "string") return json.text;
  return JSON.stringify(json);
}

function contextText(file) {
  if (!file) return "";
  const json = readJson(file);
  const parts = [];
  for (const key of ["keptSegments", "droppedSegments"]) {
    if (Array.isArray(json[key])) {
      for (const item of json[key]) {
        parts.push(item.speech || item.text || "");
        if (Array.isArray(item.captionKeywords)) parts.push(item.captionKeywords.join(" "));
        if (Array.isArray(item.keyTermsIncluded)) parts.push(item.keyTermsIncluded.join(" "));
      }
    }
  }
  if (Array.isArray(json.brollSlots)) {
    for (const slot of json.brollSlots) {
      parts.push(slot.keyword || "", slot.query || "", slot.beforeSpeech || "", slot.afterSpeech || "");
    }
  }
  return parts.join("\n");
}

function normalize(text) {
  return String(text || "")
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[-_]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function termVariants(term) {
  const normalized = normalize(term);
  const variants = new Set([normalized]);
  if (normalized.includes("b roll")) {
    variants.add("broll");
    variants.add("บีโรล");
  }
  if (normalized === "ai") {
    variants.add("เอไอ");
  }
  if (normalized === "prompt") {
    variants.add("พร้อม");
  }
  return [...variants].filter(Boolean);
}

function findTerms(text, terms) {
  const haystack = normalize(text);
  const result = {};
  for (const term of terms) {
    result[term] = termVariants(term).some((variant) => haystack.includes(variant));
  }
  return result;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const transcript = transcriptText(args.transcript);
  const context = contextText(args.context);
  const transcriptFound = findTerms(transcript, args.terms);
  const contextFound = findTerms(context, args.terms);
  const missingRequired = args.required.filter((term) => !transcriptFound[term] && !contextFound[term]);
  const status = missingRequired.length === 0 ? "pass" : args.mode === "strict" ? "fail" : "warn";

  const report = {
    status,
    mode: args.mode,
    transcript: args.transcript,
    context: args.context,
    termsChecked: args.terms,
    requiredTerms: args.required,
    foundInTranscript: transcriptFound,
    foundInContext: contextFound,
    missingRequired
  };

  const output = JSON.stringify(report, null, 2);
  console.log(output);
  if (args.output) {
    fs.mkdirSync(path.dirname(args.output), { recursive: true });
    fs.writeFileSync(args.output, `${output}\n`);
  }
  if (status === "fail") process.exit(1);
}

function printHelp() {
  console.log(`Usage:
  node scripts/check-keyterms.js --transcript path.json --context path.json
  node scripts/check-keyterms.js --context path.json --required B-roll,prompt --mode strict

Options:
  --transcript <path>  Whisper or segment transcript JSON
  --context <path>     Context index JSON
  --terms <csv>        Terms to scan
  --required <csv>     Terms that must appear in transcript or context
  --mode warn|strict   Warn by default, strict exits non-zero on missing terms
  --output <path>      Write JSON report
`);
}

try {
  main();
} catch (error) {
  console.error(`check-keyterms: ${error.message}`);
  process.exit(2);
}
