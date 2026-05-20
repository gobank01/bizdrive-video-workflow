#!/usr/bin/env python3
"""Build the v88 particle-burst captions sub-composition from caption-groups.json.

Input:  assets/v88-video-div/transcript/caption-groups.json
        (produced by the post-process subagent — text-fixed Thai groups with
         per-token gold annotations and timing taken from the real ElevenLabs
         word boundaries on the v88 edited timeline.)

Output:
  - compositions/captions-burst.html   (HyperFrames sub-composition)
  - index.html                         (29 inline captions replaced with one
                                        sub-composition mount on track 3)

Visual behavior per group:
  - Group container fades+scales in at group.start
  - Tokens reveal sequentially, distributed proportionally to character length
    within the group's [start, end] window
  - White token = #ffffff at active moment, dimmed to rgba(255,255,255,.45)
    before and after
  - Gold token = #FFD700 + particle burst (10 dots) at active moment
  - Group fades out 0.20s before group.end
"""

import json
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SUB_DIR = ROOT / "compositions"
SUB = SUB_DIR / "captions-burst.html"
GROUPS_JSON = ROOT / "assets/v88-video-div/transcript/caption-groups.json"


def distribute_token_times(tokens, group_start, group_end):
    """Spread tokens linearly across the group window by character weight.
    Each token gets {"start": ..., "end": ...} on the edited timeline."""
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
    <title>v88 Burst Captions</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@700;900&family=Inter:wght@900&display=swap" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      *, *::before, *::after { box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; margin: 0; overflow: hidden; background: transparent; }
      #burst-root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: transparent; }
      #bs-container { position: absolute; inset: 0; pointer-events: none; }
      .bs-group {
        position: absolute;
        left: 0;
        bottom: 360px;
        width: 100%;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        column-gap: 18px;
        row-gap: 8px;
        padding: 0 60px;
        opacity: 0;
        visibility: hidden;
      }
      .bs-word {
        font-family: "IBM Plex Sans Thai", "Inter", sans-serif;
        font-weight: 900;
        font-size: 64px;
        color: rgba(255, 255, 255, 0.45);
        text-shadow: 0 4px 16px rgba(0,0,0,.85), 0 0 28px rgba(0,0,0,.7);
        letter-spacing: 0.01em;
        line-height: 1.1;
        display: inline-block;
        white-space: nowrap;
      }
      .bs-particle {
        position: absolute;
        width: 10px; height: 10px;
        border-radius: 50%;
        opacity: 0;
        pointer-events: none;
        z-index: 20;
        left: 540px; bottom: 420px;
      }
    </style>
  </head>
  <body>
    <div id="burst-root" data-composition-id="captions-burst" data-start="0" data-duration="__DURATION__" data-width="1080" data-height="1920">
      <div id="bs-container"></div>
    </div>
    <script>
      (function () {
        window.__timelines = window.__timelines || {};

        function mulberry32(seed) {
          return function () {
            seed |= 0;
            seed = (seed + 0x6d2b79f5) | 0;
            var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
            t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
          };
        }

        var CUES = __CUES_JSON__;
        var YELLOW = "#FFD700";
        var WHITE = "#ffffff";
        var DIM = "rgba(255,255,255,0.45)";

        var PARTICLE_COLORS = [
          "#FFD700", "#FFC233", "#FFD86A", "#FFE48E", "#ffffff",
          "#FFD700", "#FFC233", "#FFD86A"
        ];
        var NUM_PARTICLES = 10;

        var container = document.getElementById("bs-container");
        var tl = gsap.timeline({ paused: true });

        CUES.forEach(function (cue, ci) {
          var grp = document.createElement("div");
          grp.className = "bs-group";
          grp.id = "bs-grp-" + ci;
          container.appendChild(grp);

          cue.tokens.forEach(function (tok, ti) {
            var span = document.createElement("span");
            span.className = "bs-word";
            span.id = "bs-w-" + ci + "-" + ti;
            span.textContent = tok.text;
            grp.appendChild(span);
          });

          // Group enter / hold / exit
          tl.set(grp, { visibility: "visible" }, cue.start);
          tl.fromTo(
            grp,
            { opacity: 0, scale: 0.92, y: 20 },
            { opacity: 1, scale: 1, y: 0, duration: 0.22, ease: "back.out(1.6)" },
            cue.start
          );

          cue.tokens.forEach(function (tok, ti) {
            var wid = "#bs-w-" + ci + "-" + ti;
            var isGold = !!tok.gold;
            // Active reveal at token.start
            tl.to(wid, { color: isGold ? YELLOW : WHITE, scale: isGold ? 1.10 : 1.03, duration: 0.10, ease: "power2.out" }, tok.start);
            // After a brief held window, ease the scale back so multiple tokens read together
            tl.to(wid, { scale: 1.0, duration: 0.20, ease: "power1.inOut" }, tok.start + Math.max(0.15, (tok.end - tok.start) * 0.35));

            if (isGold) {
              var rng = mulberry32((ci * 31 + ti * 7 + 11) | 0);
              for (var p = 0; p < NUM_PARTICLES; p++) {
                var angle = (p / NUM_PARTICLES) * Math.PI * 2 + rng() * 0.6;
                var dist = 90 + rng() * 160;
                var sz = 4 + rng() * 8;
                var dx = Math.cos(angle) * dist;
                var dy = -Math.sin(angle) * dist;
                var dot = document.createElement("div");
                dot.className = "bs-particle";
                dot.id = "bs-p-" + ci + "-" + ti + "-" + p;
                dot.style.backgroundColor = PARTICLE_COLORS[p % PARTICLE_COLORS.length];
                dot.style.width = sz.toFixed(1) + "px";
                dot.style.height = sz.toFixed(1) + "px";
                container.appendChild(dot);
                tl.set("#" + dot.id, { x: 0, y: 0, opacity: 0 }, tok.start);
                tl.to("#" + dot.id, { x: dx, y: dy, opacity: 1, duration: 0.14, ease: "power3.out" }, tok.start + p * 0.018);
                tl.to("#" + dot.id, { opacity: 0, duration: 0.5, ease: "power1.in" }, tok.start + 0.14 + p * 0.018);
                tl.set("#" + dot.id, { opacity: 0, x: 0, y: 0 }, Math.min(tok.start + 0.85, cue.end));
              }
            }
          });

          // Exit
          var exitStart = Math.max(cue.start + 0.1, cue.end - 0.22);
          tl.to(grp, { opacity: 0, duration: 0.20, ease: "power2.in" }, exitStart);
          tl.set(grp, { opacity: 0, visibility: "hidden" }, cue.end);
        });

        tl.seek(0);
        window.__timelines["captions-burst"] = tl;
      })();
    </script>
  </body>
</html>
'''


def emit_sub(cues, composition_duration):
    return (
        SUB_TEMPLATE
        .replace("__DURATION__", f"{composition_duration:.6f}")
        .replace("__CUES_JSON__", json.dumps(cues, ensure_ascii=False))
    )


def ensure_mount(html: str, composition_duration: float) -> str:
    """Make sure index.html has exactly one captions sub-composition mount on track 3."""
    mount = (
        '      <div id="captions-mount" class="clip" style="z-index: 10;" '
        'data-composition-id="captions-burst" '
        'data-composition-src="compositions/captions-burst.html" '
        f'data-start="0" data-duration="{composition_duration:.6f}" '
        'data-track-index="3" data-width="1080" data-height="1920"></div>'
    )
    # Replace any inline subtitle-XX lines on track 3 with the mount
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
        # No existing caption found — inject just before </div> that closes the root composition
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
    data = json.loads(GROUPS_JSON.read_text(encoding="utf-8"))
    composition_duration = float(data.get("duration", 103.561333))
    cues = build_cues(data)

    SUB_DIR.mkdir(parents=True, exist_ok=True)
    SUB.write_text(emit_sub(cues, composition_duration), encoding="utf-8")

    html = INDEX.read_text(encoding="utf-8")
    new_html = ensure_mount(html, composition_duration)
    INDEX.write_text(new_html, encoding="utf-8")

    gold_count = sum(1 for c in cues for t in c["tokens"] if t["gold"])
    white_count = sum(1 for c in cues for t in c["tokens"] if not t["gold"])
    print(f"  Wrote {SUB.relative_to(ROOT)}")
    print(f"  Composition duration: {composition_duration}s")
    print(f"  Groups: {len(cues)} | tokens: {gold_count + white_count} (gold {gold_count} / white {white_count})")
    print(f"  Generated at: {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
