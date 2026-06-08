#!/usr/bin/env python3
"""BIZDRIVE Karaoke Caption — designed caption-highlight v2.
caption-groups.json -> vertical Thai karaoke captions with brand 2-colour system:
  normal word  -> red box
  gold token   -> gold box (numbers / brands, from token.gold)
Per-word timing interpolated inside each group (weighted by character count).
Usage: build-highlight-v2.py <caption-groups.json> <out.html> <duration> [bottom_px]
"""
import json, sys

src = sys.argv[1]
out = sys.argv[2]
duration = float(sys.argv[3])
bottom = sys.argv[4] if len(sys.argv) > 4 else "330"

data = json.load(open(src))
groups_in = data["groups"]

WORDS = []        # {text, start, end, gold}
RAW_GROUPS = []   # [firstWordIdx, lastWordIdx]

for g in groups_in:
    gs, ge = float(g["start"]), float(g["end"])
    toks = g["tokens"]
    weights = [max(len(t["text"]), 1) for t in toks]
    total = sum(weights)
    cursor = gs
    first = len(WORDS)
    for t, w in zip(toks, weights):
        span = (ge - gs) * (w / total)
        WORDS.append({"text": t["text"], "start": round(cursor, 3),
                       "end": round(cursor + span, 3), "gold": bool(t.get("gold"))})
        cursor += span
    RAW_GROUPS.append([first, len(WORDS) - 1])

words_js = json.dumps(WORDS, ensure_ascii=False)
groups_js = json.dumps(RAW_GROUPS)

html = f"""<!doctype html>
<html lang="th">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@700;800&display=swap" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      *, *::before, *::after {{ box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; margin: 0; overflow: hidden; background: transparent; }}
      #highlight {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: transparent; pointer-events: none; }}
      #hl-container {{ position: absolute; inset: 0; z-index: 10; pointer-events: none; }}
      .hl-group {{
        position: absolute; bottom: {bottom}px; left: 0; width: 100%;
        display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: center;
        gap: 16px 10px; padding: 0 56px; opacity: 0; visibility: hidden;
      }}
      .hl-word {{
        font-family: "IBM Plex Sans Thai", sans-serif; font-weight: 800;
        font-size: 84px; color: #ffffff; display: inline-block;
        letter-spacing: 0; line-height: 1.12; position: relative;
        padding: 10px 20px 16px;
        text-shadow: 0 4px 16px rgba(0,0,0,.55), 0 2px 5px rgba(0,0,0,.6);
        transform-origin: 50% 60%; will-change: transform;
      }}
      .hl-word-bg {{
        position: absolute; inset: 0; border-radius: 14px;
        background: linear-gradient(135deg, #ff2d55 0%, #d11138 100%);
        box-shadow: 0 10px 26px rgba(209,17,56,.40), inset 0 1px 0 rgba(255,255,255,.28);
        opacity: 0; transform: scaleX(0); transform-origin: 0% 50%; z-index: -1;
      }}
      .hl-word-bg.gold {{
        background: linear-gradient(135deg, #ffd93d 0%, #f4c20f 55%, #d99a06 100%);
        box-shadow: 0 10px 26px rgba(244,194,15,.42), inset 0 1px 0 rgba(255,255,255,.4);
      }}
      .hl-word-text {{ position: relative; z-index: 1; }}
    </style>
  </head>
  <body>
    <div id="highlight" data-composition-id="captions-highlight" data-timeline-locked
         data-start="0" data-duration="{duration}" data-fps="30" data-width="1080" data-height="1920">
      <div id="hl-container"></div>
    </div>
    <script>
      (function () {{
        window.__timelines = window.__timelines || {{}};
        var _fitCanvas = document.createElement("canvas");
        var _fitCtx = _fitCanvas.getContext("2d");
        function fitFontSize(text, baseFontSize, fontWeight, fontFamily, maxWidth) {{
          var size = baseFontSize;
          var minSize = Math.floor(baseFontSize * 0.6);
          while (size > minSize) {{
            _fitCtx.font = fontWeight + " " + size + "px " + fontFamily;
            if (_fitCtx.measureText(text).width <= maxWidth) return size;
            size -= 2;
          }}
          return minSize;
        }}

        var WORDS = {words_js};
        var RAW_GROUPS = {groups_js};
        var COMP_DURATION = {duration};

        var GROUPS = RAW_GROUPS.map(function (pair, gi) {{
          var ws = pair[0], we = pair[1];
          var nextStart = gi + 1 < RAW_GROUPS.length ? WORDS[RAW_GROUPS[gi + 1][0]].start : COMP_DURATION;
          var gEnd = Math.min(WORDS[we].end + 0.35, nextStart - 0.04);
          return {{ wordStart: ws, wordEnd: we, start: WORDS[ws].start, end: gEnd }};
        }});

        var container = document.getElementById("hl-container");
        var tl = gsap.timeline({{ paused: true }});

        GROUPS.forEach(function (g, gi) {{
          var groupWords = WORDS.slice(g.wordStart, g.wordEnd + 1);
          var grp = document.createElement("div");
          grp.className = "hl-group";
          grp.id = "hl-grp-" + gi;

          var groupText = groupWords.map(function (w) {{ return w.text; }}).join(" ");
          var computedSize = fitFontSize(groupText, 84, "800", "IBM Plex Sans Thai", 1820);

          groupWords.forEach(function (w, i) {{
            var wi = g.wordStart + i;
            var wordEl = document.createElement("span");
            wordEl.className = "hl-word";
            wordEl.id = "hl-w-" + wi;
            wordEl.style.fontSize = computedSize + "px";
            var bgEl = document.createElement("span");
            bgEl.className = "hl-word-bg" + (w.gold ? " gold" : "");
            bgEl.id = "hl-bg-" + wi;
            var textEl = document.createElement("span");
            textEl.className = "hl-word-text";
            textEl.textContent = w.text;
            wordEl.appendChild(bgEl);
            wordEl.appendChild(textEl);
            grp.appendChild(wordEl);
          }});
          container.appendChild(grp);

          // group enter: fade-up lift
          tl.set(grp, {{ visibility: "visible" }}, g.start);
          tl.fromTo(grp, {{ opacity: 0, y: 24 }},
            {{ opacity: 1, y: 0, duration: 0.18, ease: "power3.out" }}, g.start);

          groupWords.forEach(function (w, i) {{
            var wi = g.wordStart + i;
            var bgEl = document.getElementById("hl-bg-" + wi);
            var wordEl = document.getElementById("hl-w-" + wi);
            var textEl = wordEl.querySelector(".hl-word-text");
            var isGold = bgEl.classList.contains("gold");
            // box sweeps in from the left as the word is spoken
            tl.to(bgEl, {{ opacity: 1, scaleX: 1, duration: 0.16, ease: "power3.out" }}, w.start);
            // word pops, then settles
            tl.to(wordEl, {{ scale: 1.07, duration: 0.14, ease: "back.out(2.4)" }}, w.start);
            tl.to(wordEl, {{ scale: 1.0, duration: 0.18, ease: "power2.out" }}, w.start + 0.14);
            // gold box needs dark text for contrast — flip text colour with the box
            if (isGold) {{
              tl.to(textEl, {{ color: "#1c1206", duration: 0.1, ease: "power2.out" }}, w.start);
              tl.to(textEl, {{ color: "#ffffff", duration: 0.1, ease: "power2.in" }}, w.end);
            }}
            // box exits with a slight overshoot
            tl.to(bgEl, {{ opacity: 0, scaleX: 1.03, duration: 0.12, ease: "power2.in" }}, w.end);
            tl.set(bgEl, {{ scaleX: 0 }}, w.end + 0.12);
          }});

          tl.to(grp, {{ opacity: 0, duration: 0.14, ease: "power2.in" }}, g.end - 0.14);
          tl.set(grp, {{ opacity: 0, visibility: "hidden" }}, g.end);
        }});

        tl.seek(0);
        window.__timelines["captions-highlight"] = tl;
      }})();
    </script>
  </body>
</html>
"""

open(out, "w").write(html)
gold_n = sum(1 for w in WORDS if w["gold"])
print(f"  wrote {out}")
print(f"  {len(WORDS)} words / {len(RAW_GROUPS)} groups / {gold_n} gold tokens")
