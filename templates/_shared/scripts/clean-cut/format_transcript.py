#!/usr/bin/env python3
"""Format an AssemblyAI transcript JSON into a readable timestamped script.

Outputs a text format designed for LLM review, grouping words into lines
with timestamps so the editor can scan through and decide what to keep/cut.

Output format:
  [00:08.16 - 00:12.34] Okay, so we have a lot of Cloud Code updates to go over—
  [00:12.50 - 00:18.90] Okay, so we have a whole bunch of Cloud Code updates to go...
  ...

Lines are broken at natural boundaries: pauses >500ms, sentence endings, or every ~15 words.
"""

import argparse
import json
import sys


def format_timestamp(ms: int) -> str:
    """Convert milliseconds to MM:SS.mm format."""
    total_s = ms / 1000.0
    minutes = int(total_s // 60)
    seconds = total_s % 60
    return f"{minutes:02d}:{seconds:05.2f}"


def format_transcript(words, pause_threshold_ms=500, max_words_per_line=18):
    """Group words into timestamped lines."""
    if not words:
        return ""

    lines = []
    current_line_words = []
    line_start_ms = words[0]["start"]

    for i, w in enumerate(words):
        current_line_words.append(w["text"])

        # Decide whether to break the line
        should_break = False

        # End of transcript
        if i == len(words) - 1:
            should_break = True
        else:
            next_w = words[i + 1]
            gap_ms = next_w["start"] - w["end"]

            # Break on pause
            if gap_ms >= pause_threshold_ms:
                should_break = True
            # Break on sentence-ending punctuation
            elif w["text"].rstrip().endswith((".", "!", "?", "—")):
                should_break = True
            # Break on max length
            elif len(current_line_words) >= max_words_per_line:
                should_break = True

        if should_break and current_line_words:
            line_end_ms = w["end"]
            ts = f"[{format_timestamp(line_start_ms)} - {format_timestamp(line_end_ms)}]"
            text = " ".join(current_line_words)
            lines.append(f"{ts} {text}")

            current_line_words = []
            if i < len(words) - 1:
                line_start_ms = words[i + 1]["start"]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Format transcript for LLM review")
    parser.add_argument("transcript", help="Path to AssemblyAI transcript JSON")
    parser.add_argument("-o", "--output", help="Path for output text file (default: stdout)")
    parser.add_argument("--pause", type=int, default=500, help="Pause threshold for line breaks (ms, default: 500)")
    args = parser.parse_args()

    with open(args.transcript) as f:
        data = json.load(f)

    words = data.get("words", [])
    if not words:
        print("No words found in transcript.", file=sys.stderr)
        sys.exit(1)

    formatted = format_transcript(words, args.pause)

    total_duration = words[-1]["end"] - words[0]["start"]
    header = f"# Transcript: {len(words)} words, {total_duration / 1000:.1f}s ({total_duration / 60000:.1f}min)\n\n"

    output = header + formatted

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Formatted transcript saved to {args.output} ({len(output.splitlines())} lines)", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
