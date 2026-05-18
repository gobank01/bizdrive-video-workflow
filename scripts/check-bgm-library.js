#!/usr/bin/env node
import fs from "node:fs";

const indexPath = process.argv[2] || "bgm-library/mixkit-stock-v50.json";

function fail(message) {
  console.error(`check-bgm-library: ${message}`);
  process.exit(2);
}

if (!fs.existsSync(indexPath)) fail(`index not found: ${indexPath}`);

const library = JSON.parse(fs.readFileSync(indexPath, "utf8"));
const tracks = Array.isArray(library.tracks) ? library.tracks : [];

if (library.defaultMixLevelPercent !== 5) fail("defaultMixLevelPercent must be 5");
if (!library.licenseUrl) fail("missing library licenseUrl");
if (tracks.length < 10 || tracks.length > 20) fail(`expected 10-20 tracks, got ${tracks.length}`);
if (!library.defaultFallbackTrackId) fail("missing defaultFallbackTrackId");

const ids = new Set();
const required = [
  "id",
  "title",
  "artist",
  "localPath",
  "sourceUrl",
  "sourcePage",
  "durationSeconds",
  "tags",
  "energy",
  "mood",
  "bestFor",
  "notes"
];

for (const track of tracks) {
  for (const key of required) {
    if (track[key] === undefined || track[key] === null || track[key] === "") {
      fail(`${track.id || "unknown"} missing ${key}`);
    }
  }
  if (ids.has(track.id)) fail(`duplicate id: ${track.id}`);
  ids.add(track.id);
  if (!fs.existsSync(track.localPath)) fail(`${track.id} local file missing: ${track.localPath}`);
  if (!track.sourceUrl.startsWith("https://assets.mixkit.co/music/")) fail(`${track.id} sourceUrl is not Mixkit asset URL`);
  if (!Array.isArray(track.tags) || track.tags.length === 0) fail(`${track.id} tags must be non-empty`);
  if (!Array.isArray(track.bestFor) || track.bestFor.length === 0) fail(`${track.id} bestFor must be non-empty`);
  if (track.durationSeconds < 30) fail(`${track.id} duration is too short for loop stock`);
}

if (!ids.has(library.defaultFallbackTrackId)) {
  fail(`defaultFallbackTrackId not found in tracks: ${library.defaultFallbackTrackId}`);
}
if (library.techFallbackTrackId && !ids.has(library.techFallbackTrackId)) {
  fail(`techFallbackTrackId not found in tracks: ${library.techFallbackTrackId}`);
}
if (library.calmFallbackTrackId && !ids.has(library.calmFallbackTrackId)) {
  fail(`calmFallbackTrackId not found in tracks: ${library.calmFallbackTrackId}`);
}

console.log(JSON.stringify({
  ok: true,
  indexPath,
  version: library.version,
  trackCount: tracks.length,
  defaultMixLevelPercent: library.defaultMixLevelPercent,
  defaultFallbackTrackId: library.defaultFallbackTrackId,
  provider: library.provider,
  licenseUrl: library.licenseUrl
}, null, 2));
