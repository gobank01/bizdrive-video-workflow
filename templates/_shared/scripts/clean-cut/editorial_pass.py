#!/usr/bin/env python3
"""Validate and refine an editorial EDL before rendering.

The editorial agent produces an EDL (which take ranges to keep). This script:
  1. Verifies no segment overlap
  2. Verifies end-pad doesn't bleed into the next dropped take
     (this is the bug that causes 'ขั้น ขั้น' double-hear — speaker said the
      word twice across two takes, and a too-generous end-pad on the earlier
      kept segment can include the start of the NEXT dropped take.)
  3. Adjusts end_ms to be just before the next dropped take starts

Usage:
  python3 editorial_pass.py <edl.json> <transcript.json> [-o <fixed-edl.json>]

Both inputs:
  edl.json:         {"segments": [{"start_ms", "end_ms"}, ...]}
  transcript.json:  {"words": [{"start", "end", "text"}, ...]}  (ElevenLabs shape)
"""

import argparse
import json
import sys


def validate_no_overlap(segments):
    """Check editorial segments are chronological and non-overlapping."""
    issues = []
    for i in range(1, len(segments)):
        if segments[i]["start_ms"] < segments[i-1]["end_ms"]:
            issues.append(
                f"seg {i} starts at {segments[i]['start_ms']}ms but seg {i-1} ends at "
                f"{segments[i-1]['end_ms']}ms — overlap of "
                f"{segments[i-1]['end_ms'] - segments[i]['start_ms']}ms"
            )
    return issues


def find_dropped_words(segments, words):
    """Return list of word dicts that fall ENTIRELY inside a dropped range."""
    kept_ranges = [(s["start_ms"]/1000, s["end_ms"]/1000) for s in segments]

    def in_kept(t_sec):
        for ks, ke in kept_ranges:
            if ks <= t_sec < ke:
                return True
        return False

    dropped = []
    for w in words:
        # word is dropped if its midpoint is not in any kept range
        mid = (w["start"] + w["end"]) / 2
        if not in_kept(mid):
            dropped.append(w)
    return dropped


def trim_end_pads(segments, dropped_words, min_gap_ms=20):
    """For each segment, if its end_ms reaches into a dropped word, trim it
    back to just before the dropped word starts (minus min_gap_ms safety)."""
    fixed = []
    fixes = []
    for i, seg in enumerate(segments):
        new_end = seg["end_ms"]
        # next dropped word that starts AFTER segment start and could be touched
        for w in dropped_words:
            w_start_ms = int(w["start"] * 1000)
            # only care about dropped words that START between seg.end and seg.end + 500ms
            # (i.e. ones we might have accidentally padded into)
            if seg["start_ms"] < w_start_ms < new_end + 500:
                # if our end is past this dropped word's start, trim
                if new_end > w_start_ms:
                    new_end = w_start_ms - min_gap_ms
                    fixes.append({
                        "seg_index": i,
                        "old_end_ms": seg["end_ms"],
                        "new_end_ms": new_end,
                        "trimmed_ms": seg["end_ms"] - new_end,
                        "dropped_word": w["text"],
                        "word_start_ms": w_start_ms,
                    })
        fixed.append({
            "start_ms": seg["start_ms"],
            "end_ms": new_end,
        })
    return fixed, fixes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edl", help="editorial EDL JSON (from subagent)")
    ap.add_argument("transcript", help="transcript JSON with word timings")
    ap.add_argument("-o", "--output", help="write fixed EDL (default: stdout)")
    ap.add_argument("--min-gap-ms", type=int, default=20,
                    help="minimum gap between seg end and next dropped word (default 20ms)")
    args = ap.parse_args()

    with open(args.edl, encoding="utf-8") as f:
        edl = json.load(f)
    with open(args.transcript, encoding="utf-8") as f:
        trans = json.load(f)

    segments = edl["segments"]
    words = trans["words"]

    # 1. Check overlap
    overlap_issues = validate_no_overlap(segments)
    if overlap_issues:
        print("WARNING: segment overlap issues:", file=sys.stderr)
        for issue in overlap_issues:
            print(f"  {issue}", file=sys.stderr)
        print("  (these will cause audio duplication when rendered)\n", file=sys.stderr)

    # 2. Find dropped words
    dropped = find_dropped_words(segments, words)
    print(f"editorial decision: keep {len(words) - len(dropped)} words, drop {len(dropped)}",
          file=sys.stderr)

    # 3. Trim end pads that bleed into dropped takes
    fixed_segs, fixes = trim_end_pads(segments, dropped, args.min_gap_ms)
    if fixes:
        print(f"\nFIXED {len(fixes)} end-pad bleed issue(s):", file=sys.stderr)
        for fix in fixes:
            print(f"  seg {fix['seg_index']}: end {fix['old_end_ms']} → {fix['new_end_ms']} "
                  f"(was bleeding into dropped word '{fix['dropped_word']}' "
                  f"at {fix['word_start_ms']}ms)", file=sys.stderr)
    else:
        print("\nNo end-pad bleed issues found.", file=sys.stderr)

    # Output fixed EDL
    out = {**edl, "segments": fixed_segs}
    out_json = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_json)
        print(f"\nwrote fixed EDL to {args.output}", file=sys.stderr)
    else:
        print(out_json)


if __name__ == "__main__":
    main()
