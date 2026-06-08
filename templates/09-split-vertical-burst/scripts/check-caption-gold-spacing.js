#!/usr/bin/env node
import fs from "node:fs";

function parseArgs(argv) {
  const args = {
    html: "index.html"
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--html") {
      args.html = next;
      i += 1;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }

  if (!fs.existsSync(args.html)) {
    throw new Error(`HTML file not found: ${args.html}`);
  }
  return args;
}

function hasLeftSpacingIssue(before) {
  if (!before) return false;
  return /\S$/.test(before);
}

function hasRightSpacingIssue(after) {
  if (!after) return false;
  return /^\S/.test(after);
}

function stripTags(value) {
  return value.replace(/<[^>]*>/g, "");
}

function checkCaptionBox(html) {
  const issues = [];
  const boxPattern = /<span\s+class="caption-box">([\s\S]*?)<\/span><\/div>/g;
  const goldPattern = /<span\s+class="gold">([\s\S]*?)<\/span>/g;
  let boxMatch;
  let index = 0;

  while ((boxMatch = boxPattern.exec(html))) {
    index += 1;
    const boxHtml = boxMatch[1];
    let goldMatch;
    while ((goldMatch = goldPattern.exec(boxHtml))) {
      const before = stripTags(boxHtml.slice(0, goldMatch.index));
      const after = stripTags(boxHtml.slice(goldMatch.index + goldMatch[0].length));
      if (hasLeftSpacingIssue(before)) {
        issues.push({
          caption: index,
          side: "left",
          goldText: stripTags(goldMatch[1]),
          before: before.slice(-12)
        });
      }
      if (hasRightSpacingIssue(after)) {
        issues.push({
          caption: index,
          side: "right",
          goldText: stripTags(goldMatch[1]),
          after: after.slice(0, 12)
        });
      }
    }
  }

  return { captionCount: index, issues };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const html = fs.readFileSync(args.html, "utf8");
  const result = checkCaptionBox(html);
  const report = {
    status: result.issues.length ? "fail" : "pass",
    html: args.html,
    captionCount: result.captionCount,
    rule: "Gold-highlight captions must have word-safe spacing from adjacent normal text. Examples: ABC with B highlighted becomes A B C; BCD becomes B C D.",
    issues: result.issues
  };

  console.log(JSON.stringify(report, null, 2));
  if (result.issues.length) process.exit(1);
}

function printHelp() {
  console.log(`Usage:
  node scripts/check-caption-gold-spacing.js --html index.html
`);
}

try {
  main();
} catch (error) {
  console.error(`check-caption-gold-spacing: ${error.message}`);
  process.exit(2);
}
