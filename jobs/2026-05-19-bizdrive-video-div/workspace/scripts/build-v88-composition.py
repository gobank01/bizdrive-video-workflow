#!/usr/bin/env python3
"""Build v88 HyperFrames composition from v87 template.

Takes the existing v87 index.html, shifts caption timing by HEAD_PAD,
swaps video sources to v88 masters, and rebases composition duration.
B-roll slots get the same shift since underlying speech moved equally.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "index.html"
DST = ROOT / "index.html"  # in-place; we keep a backup

V87_DURATION = 103.466667
V88_DURATION = 103.561333
HEAD_PAD = 0.28  # v88 has 280ms head silence before first word (from VAD pad_ms=200 + editorial 200ms head_pad - actual speech start at 24.90)

V87_VIDEO_DIV = "assets/v87-video-div"
V88_VIDEO_DIV = "assets/v88-video-div"


def shift_attr(html: str, attr: str, delta: float, cap: float | None = None) -> str:
    """Add delta to every data-{attr}="X.YYY" value found."""
    pat = re.compile(rf'(data-{attr}=")(\d+\.?\d*)(")')

    def repl(m):
        val = float(m.group(2)) + delta
        if cap is not None:
            val = min(val, cap)
        return f'{m.group(1)}{val:.3f}{m.group(3)}'

    return pat.sub(repl, html)


def cap_duration_to_composition(html: str, composition_end: float) -> str:
    """For every clip with data-start + data-duration, ensure start+duration <= composition_end."""
    pat = re.compile(r'(data-start=")(\d+\.?\d*)(")[^>]*?(data-duration=")(\d+\.?\d*)(")')

    def repl(m):
        start = float(m.group(2))
        dur = float(m.group(5))
        end = start + dur
        if end > composition_end:
            dur = max(0.05, composition_end - start)
        return f'{m.group(1)}{start:.3f}{m.group(3)}{m.group(0)[m.end(3)-m.start():m.start(4)-m.start()]}{m.group(4)}{dur:.3f}{m.group(6)}'

    # Simpler: scan elements line by line via attribute order checks.
    # We'll do safer line-by-line transform.
    lines = html.split("\n")
    out_lines = []
    for line in lines:
        m_start = re.search(r'data-start="(\d+\.?\d*)"', line)
        m_dur = re.search(r'data-duration="(\d+\.?\d*)"', line)
        if m_start and m_dur:
            start = float(m_start.group(1))
            dur = float(m_dur.group(1))
            end = start + dur
            if end > composition_end + 0.001:
                new_dur = max(0.05, composition_end - start)
                line = re.sub(r'(data-duration=")(\d+\.?\d*)(")', rf'\g<1>{new_dur:.3f}\g<3>', line, count=1)
        out_lines.append(line)
    return "\n".join(out_lines)


def main():
    src_html = SRC.read_text(encoding="utf-8")

    # 1. Back up v87 index.html before in-place changes (keep diff history-friendly)
    backup = ROOT / "index.v87.html"
    if not backup.exists():
        backup.write_text(src_html, encoding="utf-8")
        print(f"  Backed up v87 composition to {backup.name}")

    # 2. Update root composition duration
    html = src_html.replace(f'data-duration="{V87_DURATION:.6f}"', f'data-duration="{V88_DURATION:.6f}"')
    html = html.replace(f'const compositionDuration = {V87_DURATION};', f'const compositionDuration = {V88_DURATION};')
    html = html.replace(f'data-motion-duration="{V87_DURATION:.6f}"', f'data-motion-duration="{V88_DURATION:.6f}"')

    # 3. Swap video sources
    html = html.replace(f'src="{V87_VIDEO_DIV}/top_phase5.mp4"', f'src="{V88_VIDEO_DIV}/top_v88_visual_master.mp4"')
    html = html.replace(f'src="{V87_VIDEO_DIV}/bottom_phase5.mp4"', f'src="{V88_VIDEO_DIV}/bottom_v88_visual_master.mp4"')
    html = html.replace(f'src="{V87_VIDEO_DIV}/bg.png"', f'src="{V87_VIDEO_DIV}/bg.png"')  # bg same

    # 4. Shift caption + B-roll starts by HEAD_PAD
    # subtitle-XX divs all have data-start that are caption timings (relative to composition)
    # broll videos also have data-start
    # We shift any clip with track-index >= 3 (captions) and broll-* (track-index 4-8)
    # Simpler: shift ALL data-start values for elements that are NOT the root, background, top, bottom (track 0-2)
    # Strategy: locate caption/broll lines specifically.
    lines = html.split("\n")
    out_lines = []
    for line in lines:
        # Skip if line has track-index="0" (bg), "1" (top), "2" (bottom)
        # Shift if line has 'subtitle-' or 'broll' identifier
        if 'subtitle-' in line or re.search(r'id="broll\d+"', line) or 'broll-frame' in line:
            m_start = re.search(r'data-start="(\d+\.?\d*)"', line)
            if m_start:
                new_start = float(m_start.group(1)) + HEAD_PAD
                # Cap so start < composition end
                new_start = min(new_start, V88_DURATION - 0.05)
                line = re.sub(r'(data-start=")(\d+\.?\d*)(")', rf'\g<1>{new_start:.3f}\g<3>', line, count=1)
        out_lines.append(line)
    html = "\n".join(out_lines)

    # 5. Cap durations so start+duration <= V88_DURATION for every clip
    html = cap_duration_to_composition(html, V88_DURATION)

    # 6. Write output
    DST.write_text(html, encoding="utf-8")
    print(f"  Wrote v88 composition to {DST.name}")
    print(f"  Composition duration: {V87_DURATION}s -> {V88_DURATION}s")
    print(f"  Caption/B-roll shifted by +{HEAD_PAD}s (head silence pad)")


if __name__ == "__main__":
    main()
