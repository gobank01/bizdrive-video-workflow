#!/usr/bin/env python3
"""BIZDRIVE Weight-Shift Caption — adapted from HyperFrames caption-weight-shift.
caption-groups.json -> vertical Thai captions where font-weight travels word-by-word:
  the currently-spoken word shifts to BOLD (700) + slight scale, the rest stay
  LIGHT (300). gold tokens keep a persistent gold colour so keywords always pop.
Per-word timing interpolated inside each group (weighted by character count) —
same interpolation as build-highlight-captions.py.
Usage: build-weightshift-captions.py <caption-groups.json> <out.html> <duration> [bottom_px]
"""
import json, sys

src = sys.argv[1]
out = sys.argv[2]
duration = float(sys.argv[3])
bottom = sys.argv[4] if len(sys.argv) > 4 else "360"

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
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@300;500;700&display=swap" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      *, *::before, *::after {{ box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; margin: 0; overflow: hidden; background: transparent; }}
      #weightshift {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: transparent; pointer-events: none; }}
      #ws-container {{ position: absolute; inset: 0; z-index: 10; pointer-events: none; }}
      .ws-group {{
        position: absolute; bottom: {bottom}px; left: 0; width: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 0 56px; opacity: 0; visibility: hidden;
      }}
      .ws-panel {{
        display: inline-flex; flex-wrap: wrap; align-items: center; justify-content: center;
        gap: 8px 18px; max-width: 100%; padding: 20px 44px; border-radius: 28px;
        background: linear-gradient(180deg, rgba(6,14,38,.84), rgba(4,10,30,.90));
        border: 1px solid rgba(255,255,255,.10);
        box-shadow: 0 14px 40px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.06);
        backdrop-filter: blur(10px);
      }}
      .ws-word {{
        font-family: "IBM Plex Sans Thai", sans-serif; font-weight: 300;
        font-size: 78px; color: #ffffff; display: inline-block;
        letter-spacing: -0.01em; line-height: 1.16;
        text-shadow: 0 3px 14px rgba(0,0,0,.55), 0 1px 4px rgba(0,0,0,.6);
        transform-origin: 50% 60%; will-change: transform, font-weight;
      }}
      .ws-word.gold {{
        color: #f4c20f;
        text-shadow: 0 3px 16px rgba(0,0,0,.6), 0 0 22px rgba(244,194,15,.25);
      }}
    </style>
  </head>
  <body>
    <div id="weightshift" data-composition-id="captions-weightshift" data-timeline-locked
         data-start="0" data-duration="{duration}" data-fps="30" data-width="1080" data-height="1920">
      <div id="ws-container"></div>
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

        var container = document.getElementById("ws-container");
        var tl = gsap.timeline({{ paused: true }});

        GROUPS.forEach(function (g, gi) {{
          var groupWords = WORDS.slice(g.wordStart, g.wordEnd + 1);
          var grp = document.createElement("div");
          grp.className = "ws-group";
          grp.id = "ws-grp-" + gi;
          var panel = document.createElement("div");
          panel.className = "ws-panel";

          var groupText = groupWords.map(function (w) {{ return w.text; }}).join(" ");
          var computedSize = fitFontSize(groupText, 78, "700", "IBM Plex Sans Thai", 1760);

          groupWords.forEach(function (w, i) {{
            var wi = g.wordStart + i;
            var wordEl = document.createElement("span");
            wordEl.className = "ws-word" + (w.gold ? " gold" : "");
            wordEl.id = "ws-w-" + wi;
            wordEl.style.fontSize = computedSize + "px";
            wordEl.textContent = w.text;
            panel.appendChild(wordEl);
          }});
          grp.appendChild(panel);
          container.appendChild(grp);

          // group enter: gentle fade-up
          tl.set(grp, {{ visibility: "visible" }}, g.start);
          tl.fromTo(grp, {{ opacity: 0, y: 22 }},
            {{ opacity: 1, y: 0, duration: 0.22, ease: "power3.out" }}, g.start);

          // weight travels word-by-word: active word -> bold + scale, then settles back to light
          groupWords.forEach(function (w, i) {{
            var wi = g.wordStart + i;
            var wordEl = document.getElementById("ws-w-" + wi);
            tl.to(wordEl, {{ fontWeight: 700, scale: 1.08, duration: 0.16, ease: "power2.out" }}, w.start);
            tl.to(wordEl, {{ fontWeight: 300, scale: 1.0, duration: 0.26, ease: "power2.inOut" }}, w.end);
          }});

          tl.to(grp, {{ opacity: 0, duration: 0.16, ease: "power2.in" }}, g.end - 0.16);
          tl.set(grp, {{ opacity: 0, visibility: "hidden" }}, g.end);
        }});

        tl.seek(0);
        window.__timelines["captions-weightshift"] = tl;
      }})();
    </script>
  </body>
</html>
"""

open(out, "w").write(html)
gold_n = sum(1 for w in WORDS if w["gold"])
print(f"  wrote {out}")
print(f"  {len(WORDS)} words / {len(RAW_GROUPS)} groups / {gold_n} gold tokens")
