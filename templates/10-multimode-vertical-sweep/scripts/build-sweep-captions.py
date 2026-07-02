#!/usr/bin/env python3
"""Build the Template 10 BLUE WORD-SWEEP captions sub-composition.

Input:  assets/intermediates/transcript/caption-groups.json
        (text-fixed Thai groups + per-token gold flag + timing on the v88 edited
         timeline — the SAME schema as Template 04/09.)

Output:
  - compositions/captions-sweep.html   (HyperFrames sub-composition)
  - index.html                         (one sub-composition mount on track 3)

Visual behavior per group (matches the screenshots — clean, easy to read):
  - Every word is solid WHITE the moment the group appears (no dim, no box, no pill)
  - The currently-spoken word pops to BLUE (#2EA8FF) with a small scale bump,
    then settles back to white — so exactly one word is blue at a time
  - Bare bold text with a heavy shadow for legibility over busy video
  - Centered over the seam (bottom arg, default 910)
  - The 'gold' token flag only adds a slightly stronger pop; the active colour
    is always blue (white+blue spec).
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SUB_DIR = ROOT / "compositions"
SUB = SUB_DIR / "captions-sweep.html"
GROUPS_JSON = ROOT / "assets/intermediates/transcript/caption-groups.json"


def distribute_token_times(tokens, group_start, group_end):
    """Spread tokens linearly across the group window by character weight."""
    duration = max(0.001, group_end - group_start)
    total_chars = sum(max(1, len(t["text"])) for t in tokens)
    cursor = group_start
    out = []
    for tok in tokens:
        chars = max(1, len(tok["text"]))
        share = duration * (chars / total_chars)
        t_start = cursor
        t_end = min(group_end, cursor + share)
        cursor = t_end
        out.append({
            "text": tok["text"],
            "gold": bool(tok.get("gold")),
            "start": round(t_start, 3),
            "end": round(t_end, 3),
        })
    return out


def build_cues(groups_data):
    cues = []
    for g in groups_data["groups"]:
        cues.append({
            "start": float(g["start"]),
            "end": float(g["end"]),
            "duration": round(float(g["end"]) - float(g["start"]), 3),
            "tokens": distribute_token_times(g["tokens"], float(g["start"]), float(g["end"])),
        })
    return cues


SUB_TEMPLATE = '''<!doctype html>
<html lang="th">
  <head>
    <meta charset="UTF-8" />
    <title>Template 10 Blue Word-Sweep Captions</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@700;900&family=Inter:wght@900&display=swap" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      *, *::before, *::after { box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; margin: 0; overflow: hidden; background: transparent; }
      #sweep-root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: transparent; }
      #sw-container { position: absolute; inset: 0; pointer-events: none; }
      .sw-group {
        position: absolute;
        left: 0;
        bottom: __BOTTOM__px;
        width: 100%;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        column-gap: 20px;
        row-gap: 6px;
        padding: 0 70px;
        opacity: 0;
        visibility: hidden;
      }
      .sw-word {
        font-family: "IBM Plex Sans Thai", "Inter", sans-serif;
        font-weight: 900;
        font-size: 100px;
        color: #ffffff;
        text-shadow: 0 4px 18px rgba(0,0,0,.9), 0 0 32px rgba(0,0,0,.75), 0 2px 4px rgba(0,0,0,.95);
        letter-spacing: 0.01em;
        line-height: 1.12;
        display: inline-block;
        white-space: nowrap;
        transform-origin: center bottom;
      }
    </style>
  </head>
  <body>
    <div id="sweep-root" data-composition-id="captions-sweep" data-start="0" data-duration="__DURATION__" data-width="1080" data-height="1920">
      <div id="sw-container"></div>
    </div>
    <script>
      (function () {
        window.__timelines = window.__timelines || {};

        var CUES = __CUES_JSON__;
        var BLUE = "#2EA8FF";
        var WHITE = "#ffffff";

        var container = document.getElementById("sw-container");
        var tl = gsap.timeline({ paused: true });

        CUES.forEach(function (cue, ci) {
          var grp = document.createElement("div");
          grp.className = "sw-group";
          grp.id = "sw-grp-" + ci;
          container.appendChild(grp);

          cue.tokens.forEach(function (tok, ti) {
            var span = document.createElement("span");
            span.className = "sw-word";
            span.id = "sw-w-" + ci + "-" + ti;
            span.textContent = tok.text;
            grp.appendChild(span);
          });

          // Group enter — all words already white.
          tl.set(grp, { visibility: "visible" }, cue.start);
          tl.fromTo(
            grp,
            { opacity: 0, scale: 0.94, y: 18 },
            { opacity: 1, scale: 1, y: 0, duration: 0.22, ease: "back.out(1.5)" },
            cue.start
          );

          // Per word — blue pop on the spoken word, then settle back to white.
          cue.tokens.forEach(function (tok, ti) {
            var wid = "#sw-w-" + ci + "-" + ti;
            var pop = tok.gold ? 1.14 : 1.07;
            var settle = tok.start + Math.max(0.15, (tok.end - tok.start) * 0.5);
            tl.to(wid, { color: BLUE, scale: pop, duration: 0.10, ease: "power2.out" }, tok.start);
            tl.to(wid, { color: WHITE, scale: 1.0, duration: 0.22, ease: "power1.inOut" }, settle);
          });

          // Exit
          var exitStart = Math.max(cue.start + 0.1, cue.end - 0.22);
          tl.to(grp, { opacity: 0, duration: 0.20, ease: "power2.in" }, exitStart);
          tl.set(grp, { opacity: 0, visibility: "hidden" }, cue.end);
        });

        tl.seek(0);
        window.__timelines["captions-sweep"] = tl;
      })();
    </script>
  </body>
</html>
'''


def emit_sub(cues, composition_duration, bottom=910):
    return (
        SUB_TEMPLATE
        .replace("__DURATION__", f"{composition_duration:.6f}")
        .replace("__CUES_JSON__", json.dumps(cues, ensure_ascii=False))
        .replace("__BOTTOM__", str(bottom))
    )


def ensure_mount(html: str, composition_duration: float) -> str:
    """Ensure index.html has exactly one captions-sweep mount on track 3."""
    mount = (
        '      <div id="captions-mount" class="clip" style="z-index: 10;" '
        'data-composition-id="captions-sweep" '
        'data-composition-src="compositions/captions-sweep.html" '
        f'data-start="0" data-duration="{composition_duration:.6f}" '
        'data-track-index="3" data-width="1080" data-height="1920"></div>'
    )
    lines = html.split("\n")
    out = []
    inserted = False
    for line in lines:
        if re.search(r'id="subtitle-\d+"[^>]*data-track-index="3"', line):
            if not inserted:
                out.append(mount)
                inserted = True
            continue
        if re.search(r'id="captions-mount"[^>]*data-track-index="3"', line):
            if not inserted:
                out.append(mount)
                inserted = True
            continue
        out.append(line)
    if not inserted:
        new_lines = []
        injected = False
        for line in out:
            if not injected and re.search(r'^\s*</div>\s*$', line):
                new_lines.append(mount)
                injected = True
            new_lines.append(line)
        out = new_lines
    return "\n".join(out)


def main():
    # Step 11 contract: argv = <groups.json> <out.html> <duration> <bottom_px>.
    # argv[1] lets v88-clip.sh pass the OFFSET-SHIFTED groups file (-120ms).
    groups_path = Path(sys.argv[1]) if len(sys.argv) > 1 else GROUPS_JSON
    if not groups_path.is_absolute():
        groups_path = ROOT / groups_path
    bottom = int(float(sys.argv[4])) if len(sys.argv) > 4 else 910

    data = json.loads(groups_path.read_text(encoding="utf-8"))
    composition_duration = float(sys.argv[3]) if len(sys.argv) > 3 else float(data.get("duration", 103.561333))
    cues = build_cues(data)

    SUB_DIR.mkdir(parents=True, exist_ok=True)
    SUB.write_text(emit_sub(cues, composition_duration, bottom), encoding="utf-8")

    html = INDEX.read_text(encoding="utf-8")
    INDEX.write_text(ensure_mount(html, composition_duration), encoding="utf-8")

    blue_pops = sum(1 for c in cues for t in c["tokens"] if t["gold"])
    total = sum(len(c["tokens"]) for c in cues)
    print(f"  Wrote {SUB.relative_to(ROOT)}")
    print(f"  Composition duration: {composition_duration}s | bottom: {bottom}px")
    print(f"  Groups: {len(cues)} | words: {total} (stronger pop on {blue_pops} gold tokens)")
    print(f"  Generated at: {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
