#!/usr/bin/env python3
"""Insert multi-mode B-roll <video> elements into index.html (Template 10).

Each insert carries a DISPLAY MODE that index.html positions/animates:
  - full        B-roll fills the whole frame (face hidden)
  - split-top   B-roll fills the top half; the face drops to the bottom rectangle

B-roll clips live at assets/intermediates/broll/broll-NN.mp4 (9:16 / 1080x1920).
object-fit cover crops each into its box, so the same source works for both modes.

Usage (run from the job workspace):
    python3 scripts/add-broll.py [--display MODE] <start1>[:mode] <start2>[:mode] ...

  --display MODE   default mode for starts that don't specify one
                   (full | split-top | mixed). Default: mixed.
  <start>[:mode]   start time in seconds, optional per-insert mode override.
                   mode aliases: full, split (=split-top).

Examples:
    python3 scripts/add-broll.py 12 32 52 70                 # mixed (auto-rotates modes)
    python3 scripts/add-broll.py --display full 12 32 52 70  # all full-screen
    python3 scripts/add-broll.py 12:split 32:full 52:split   # explicit per insert

Rules enforced (v88 B-roll):
- Each insert is 3 seconds long.
- Inserts must be >= 6s apart and within the composition duration.
- Re-running replaces any previously inserted B-roll block.
- broll-NN.mp4 (NN = 01, 02, ...) must exist for each start.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
BROLL_DURATION = 3
MIN_SPACING = 6

# "mixed" rotates through these so a clip naturally cuts between layouts.
MIXED_ROTATION = ["split-top", "full"]

MODE_ALIASES = {"full": "full", "split": "split-top", "split-top": "split-top"}

# Per-mode CSS class + a gentle pan that suits the box.
MODE_CLASS = {"full": "broll-full", "split-top": "broll-split"}
MODE_PAN = {
    "full": [("50% 51%", "50% 49%"), ("51% 50%", "49% 50%"), ("49% 50%", "51% 50%"), ("50% 49%", "50% 51%")],
    "split-top": [("50% 42%", "50% 48%")],
}


def broll_tag(index: int, start: float, mode: str) -> str:
    cls = MODE_CLASS[mode]
    pans = MODE_PAN[mode]
    pan_from, pan_to = pans[index % len(pans)]
    nn = f"{index + 1:02d}"
    overflow = ' data-layout-allow-overflow="true"' if mode == "full" else ""
    return (
        f'      <video id="broll{nn}" class="clip broll-frame {cls}"{overflow} '
        f'src="assets/intermediates/broll/broll-{nn}.mp4" '
        f'data-start="{start:.3f}" data-duration="{BROLL_DURATION}" data-media-start="0" '
        f'data-display-mode="{mode}" '
        f'data-transition-mode="soft" data-transition-in="0.22" data-transition-out="0.22" '
        f'data-pan-from="{pan_from}" data-pan-to="{pan_to}" '
        f'data-motion-kind="slow-fullscreen-inner-zoom" data-motion-duration="{BROLL_DURATION}" '
        f'data-track-index="{4 + index}" data-volume="0" muted playsinline></video>'
    )


def parse_args(argv):
    default = "mixed"
    starts = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--display", "-d"):
            default = argv[i + 1]
            i += 2
            continue
        starts.append(a)
        i += 1
    if default not in ("mixed", "full", "split-top"):
        if default in MODE_ALIASES:
            default = MODE_ALIASES[default]
        else:
            print(f"Error: bad --display '{default}' (full | split-top | mixed)", file=sys.stderr)
            sys.exit(1)
    return default, starts


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/add-broll.py [--display MODE] <start1>[:mode] ...", file=sys.stderr)
        print("Example: python3 scripts/add-broll.py 12:split 32:full 52:split", file=sys.stderr)
        sys.exit(1)

    default, tokens = parse_args(sys.argv[1:])

    parsed = []
    for tok in tokens:
        if ":" in tok:
            t_str, m_str = tok.split(":", 1)
            m = MODE_ALIASES.get(m_str.strip())
            if not m:
                print(f"Error: bad mode in '{tok}' (full | split)", file=sys.stderr)
                sys.exit(1)
        else:
            t_str, m = tok, None
        try:
            parsed.append((float(t_str), m))
        except ValueError:
            print(f"Error: start '{t_str}' is not a number", file=sys.stderr)
            sys.exit(1)

    parsed.sort(key=lambda p: p[0])

    # Fill unspecified modes: rotate the mixed list, or use the fixed default.
    resolved = []
    for i, (t, m) in enumerate(parsed):
        if m is None:
            m = MIXED_ROTATION[i % len(MIXED_ROTATION)] if default == "mixed" else default
        resolved.append((t, m))

    positions = [t for t, _ in resolved]
    for a, b in zip(positions, positions[1:]):
        if b - a < MIN_SPACING:
            print(f"Error: B-roll starts {a} and {b} are < {MIN_SPACING}s apart", file=sys.stderr)
            sys.exit(1)

    html = INDEX.read_text(encoding="utf-8")

    m = re.search(r'id="root"[^>]*data-duration="(\d+\.?\d*)"', html)
    comp_dur = float(m.group(1)) if m else None
    if comp_dur:
        for p in positions:
            if p + BROLL_DURATION > comp_dur:
                print(f"Error: B-roll at {p}s + {BROLL_DURATION}s exceeds composition {comp_dur}s",
                      file=sys.stderr)
                sys.exit(1)

    # Remove any existing broll elements, then insert the new block after #bottomVideo.
    html = re.sub(r'\s*<video\s+id="broll\d+"[\s\S]*?</video>\s*\n', '\n', html)
    tags = "\n\n".join(broll_tag(i, t, mode) for i, (t, mode) in enumerate(resolved))
    block = f"\n\n{tags}\n\n"

    m_bottom = re.search(r'(<video id="bottomVideo"[\s\S]*?</video>)', html)
    if not m_bottom:
        print("Error: could not find #bottomVideo in index.html", file=sys.stderr)
        sys.exit(1)
    insert_at = m_bottom.end()
    html = html[:insert_at] + block + html[insert_at:]

    INDEX.write_text(html, encoding="utf-8")
    clips = ", ".join(f"broll-{i + 1:02d} @ {t}s [{mode}]" for i, (t, mode) in enumerate(resolved))
    print(f"  Inserted {len(resolved)} B-roll element(s): {clips}")
    print(f"  Each {BROLL_DURATION}s, soft 0.22s transitions, tracks 4-{3 + len(resolved)}")


if __name__ == "__main__":
    main()
