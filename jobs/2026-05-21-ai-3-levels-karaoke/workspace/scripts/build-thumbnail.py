#!/usr/bin/env python3
"""V88 — BIZDRIVE default thumbnail (BG + 3-line headline).

Shared across every template (01-05). Run from a job workspace:

    python3 scripts/build-thumbnail.py "<main>" "<hero>" "<sub>"

Example:
    python3 scripts/build-thumbnail.py "AI มี" "3 ระดับ" "คุณใช้อยู่ระดับไหน?"

What it does:
  - Reads the job background  assets/input/bg.png  (BIZDRIVE logo top +
    "ให้ AI ทำงานแทนคุณ" bottom are already baked into it).
  - Composites a 1080x1920 headline in the empty blue band — white MAIN
    line, gold-gradient HERO line, soft-blue SUB line, each auto-fitted to
    width so any length stays on one line.
  - Snapshots it to a PNG via `hyperframes snapshot`.

Output:
  thumbnail/                  small HyperFrames project (re-snapshottable)
  thumbnail/thumbnail.json    the 3 lines on record
  ../output/finals/thumbnail.png   ⭐ the deliverable

Notes:
  - "hero" is the big gold line — keep it short (a number, a brand, 2-3 words).
  - To re-style, edit TEMPLATE below; the layout is template-agnostic.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]            # job workspace
THUMB_DIR = ROOT / "thumbnail"
BG_DEFAULT = ROOT / "assets/input/bg.png"
OUT_DEFAULT = ROOT / "../output/finals/thumbnail.png"

HYPERFRAMES_JSON = {
    "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
    "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
    "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
}

TEMPLATE = """<!doctype html>
<html lang="th">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@700;800;900&display=swap" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; margin: 0; overflow: hidden; background: #0a1640; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
      .clip { position: absolute; }
      .background { inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0; }
      .title-wrap {
        left: 50px; right: 50px; top: 470px; height: 980px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        text-align: center; z-index: 2;
        font-family: "IBM Plex Sans Thai", sans-serif;
      }
      .t-main {
        font-weight: 900; font-size: 132px; line-height: 1.04; color: #ffffff;
        text-shadow: 0 8px 34px rgba(0,0,0,.75), 0 0 44px rgba(0,0,0,.55);
        white-space: nowrap;
      }
      .t-hero {
        font-weight: 900; font-size: 232px; line-height: 1.0;
        margin: 6px 0 4px;
        background: linear-gradient(180deg, #ffe87a 0%, #ffd93d 42%, #f4c20f 70%, #b8860b 100%);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent; color: transparent;
        filter: drop-shadow(0 10px 26px rgba(0,0,0,.6));
        white-space: nowrap;
      }
      .t-sub {
        font-weight: 800; font-size: 78px; line-height: 1.12; color: #cdd8f2;
        margin-top: 18px;
        text-shadow: 0 4px 18px rgba(0,0,0,.7);
        white-space: nowrap;
      }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="1" data-width="1080" data-height="1920">
      <img id="background" class="clip background" src="bg.png" alt="" data-start="0" data-duration="1" data-track-index="0" />
      <div id="title" class="clip title-wrap" data-start="0" data-duration="1" data-track-index="1">
        <div class="t-main">__MAIN__</div>
        <div class="t-hero">__HERO__</div>
        <div class="t-sub">__SUB__</div>
      </div>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = gsap.timeline({ paused: true });
      // auto-fit each headline line to the 980px content width
      function fitThumb() {
        var maxW = 980;
        [["t-main", 132], ["t-hero", 232], ["t-sub", 78]].forEach(function (p) {
          var el = document.querySelector("." + p[0]);
          if (!el) return;
          var fs = p[1];
          el.style.fontSize = fs + "px";
          while (el.scrollWidth > maxW && fs > 30) { fs -= 4; el.style.fontSize = fs + "px"; }
        });
      }
      if (document.fonts && document.fonts.ready) { document.fonts.ready.then(fitThumb); }
      else { window.addEventListener("load", fitThumb); }
    </script>
  </body>
</html>
"""


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("main", help="top line — white")
    ap.add_argument("hero", help="big gold line — keep short (number / brand / 2-3 words)")
    ap.add_argument("sub", help="bottom line — soft blue")
    ap.add_argument("--bg", default=str(BG_DEFAULT), help="background image (default: assets/input/bg.png)")
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="output PNG path")
    args = ap.parse_args()

    bg = Path(args.bg)
    if not bg.exists():
        print(f"✗ background not found: {bg}", file=sys.stderr)
        sys.exit(1)

    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(bg, THUMB_DIR / "bg.png")
    (THUMB_DIR / "hyperframes.json").write_text(json.dumps(HYPERFRAMES_JSON, indent=2))
    (THUMB_DIR / "meta.json").write_text(json.dumps(
        {"id": "thumbnail", "name": "thumbnail", "createdAt": "2026-05-21T00:00:00.000Z"}, indent=2))
    (THUMB_DIR / "thumbnail.json").write_text(json.dumps(
        {"main": args.main, "hero": args.hero, "sub": args.sub}, ensure_ascii=False, indent=2))
    (THUMB_DIR / "index.html").write_text(
        TEMPLATE.replace("__MAIN__", esc(args.main))
                .replace("__HERO__", esc(args.hero))
                .replace("__SUB__", esc(args.sub)),
        encoding="utf-8")

    print(f"  thumbnail headline: {args.main} / {args.hero} / {args.sub}")
    subprocess.run(
        ["npx", "--yes", "hyperframes@0.6.25", "snapshot", str(THUMB_DIR), "--at", "0"],
        check=True)

    snap = THUMB_DIR / "snapshots" / "frame-00-at-0.0s.png"
    if not snap.exists():
        print("✗ snapshot did not produce a PNG", file=sys.stderr)
        sys.exit(1)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(snap, out)
    print(f"  ✓ thumbnail → {out}")


if __name__ == "__main__":
    main()
