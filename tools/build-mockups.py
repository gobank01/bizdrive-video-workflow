#!/usr/bin/env python3
"""Generate templates/NN-*/mockup.svg — the reference thumbnail with labelled
layout callouts (which zone is the screen recording / face cam / B-roll card /
captions, and which caption style).

Run for every template, or just one:
    python3 tools/build-mockups.py
    python3 tools/build-mockups.py templates/05-stacked-vertical-karaoke

The thumbnail.jpg is embedded as a base64 data-URI so the .svg is fully
self-contained — an <img>-loaded SVG cannot fetch external files, so the
catalog (and any markdown preview) renders it correctly.

Regenerated automatically by tools/build-catalog.sh after it extracts the
thumbnails. Add a template's callouts to SPECS below when you add a template.
"""
import base64
import glob
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Geometry ---------------------------------------------------------------
IMG_W, IMG_H = 340, 604           # thumbnail display size (9:16)
MARGIN = 300                      # side margin that holds the callout chips
PAD_TOP, PAD_BOT = 92, 64
CANVAS_W = IMG_W + 2 * MARGIN
CANVAS_H = IMG_H + PAD_TOP + PAD_BOT
IMG_X, IMG_Y = MARGIN, PAD_TOP
CHIP_W, CHIP_H = 264, 34

# --- Callouts per template --------------------------------------------------
# key = NN prefix; value = list of (label, side 'L'|'R', y-fraction, x-fraction)
# y/x fractions are positions inside the thumbnail the leader line points at.
SPECS = {
    "01": [("จอบันทึกหน้าจอ (top.mp4)", "R", 0.25, 0.50),
           ("หน้าคนพูด · วงกลม",        "L", 0.60, 0.50),
           ("แคปชั่น particle-burst",   "R", 0.80, 0.50)],
    "02": [("หน้าคนพูด · เต็มจอ",        "R", 0.40, 0.62),
           ("แคปชั่น particle-burst",   "L", 0.80, 0.50)],
    "03": [("การ์ด B-roll · มุมบน",      "L", 0.21, 0.50),
           ("หน้าคนพูด · เต็มจอ",        "R", 0.54, 0.62),
           ("แคปชั่น particle-burst",   "R", 0.80, 0.50)],
    "04": [("หน้าคนพูด · เต็มจอ",        "R", 0.40, 0.62),
           ("แคปชั่นคาราโอเกะ",         "L", 0.80, 0.50)],
    "05": [("จอบันทึกหน้าจอ (top.mp4)", "R", 0.25, 0.50),
           ("หน้าคนพูด · วงกลม",        "L", 0.60, 0.50),
           ("แคปชั่นคาราโอเกะ",         "R", 0.80, 0.50)],
    "06": [("จอบันทึกหน้าจอ · เต็มจอ",  "R", 0.30, 0.55),
           ("หน้าคนพูด · กล้องมุม",     "L", 0.16, 0.30),
           ("แคปชั่น particle-burst",   "R", 0.80, 0.50)],
    "07": [("หน้าคนพูด · เต็มจอ 16:9",  "R", 0.40, 0.50),
           ("ซับคาราโอเกะ · แดง/ทอง",   "L", 0.78, 0.50),
           ("B-roll · 1 ต่อ 2 นาที",     "R", 0.60, 0.50)],
}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_one(tdir):
    tdir = tdir.rstrip("/")
    tname = os.path.basename(tdir)
    num = tname.split("-")[0]
    thumb = os.path.join(tdir, "thumbnail.jpg")
    if not os.path.isfile(thumb):
        return None

    b64 = base64.b64encode(open(thumb, "rb").read()).decode()

    # Manifest fields for title + footer
    aspect, capsys = "9:16", ""
    mf = os.path.join(tdir, "manifest.json")
    if os.path.isfile(mf):
        try:
            m = json.load(open(mf))
            o = m.get("output", {})
            aspect = f"{o.get('aspect', '9:16')} · {o.get('width', '')}×{o.get('height', '')}"
            c = m.get("captions", {})
            capsys = c.get("style") or c.get("system") or ""
        except Exception:
            pass

    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
             f'font-family="\'IBM Plex Sans Thai\',\'Noto Sans Thai\',\'Inter\',sans-serif">')
    s.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="22" fill="#0b1330"/>')
    s.append(f'<rect x="1.5" y="1.5" width="{CANVAS_W - 3}" height="{CANVAS_H - 3}" rx="21" '
             f'fill="none" stroke="#1f2c55" stroke-width="2"/>')
    # Title
    s.append(f'<text x="{CANVAS_W / 2}" y="48" text-anchor="middle" font-size="31" '
             f'font-weight="800" fill="#f4c20f" letter-spacing="1">TEMPLATE {esc(num)}</text>')
    s.append(f'<text x="{CANVAS_W / 2}" y="73" text-anchor="middle" font-size="15" '
             f'font-weight="600" fill="#9fb0d8">{esc(tname)}</text>')
    # Thumbnail (rounded) + gold frame
    s.append(f'<clipPath id="clip{num}"><rect x="{IMG_X}" y="{IMG_Y}" width="{IMG_W}" '
             f'height="{IMG_H}" rx="16"/></clipPath>')
    s.append(f'<image x="{IMG_X}" y="{IMG_Y}" width="{IMG_W}" height="{IMG_H}" '
             f'clip-path="url(#clip{num})" preserveAspectRatio="xMidYMid slice" '
             f'href="data:image/jpeg;base64,{b64}"/>')
    s.append(f'<rect x="{IMG_X}" y="{IMG_Y}" width="{IMG_W}" height="{IMG_H}" rx="16" '
             f'fill="none" stroke="#f4c20f" stroke-width="2.5" opacity="0.9"/>')
    # Callouts
    for label, side, yf, xf in SPECS.get(num, []):
        cy = IMG_Y + yf * IMG_H
        tx = IMG_X + xf * IMG_W
        if side == "R":
            chip_x = IMG_X + IMG_W + 16
            edge = chip_x
        else:
            chip_x = IMG_X - 16 - CHIP_W
            edge = IMG_X - 16
        chy = cy - CHIP_H / 2
        s.append(f'<line x1="{edge:.1f}" y1="{cy:.1f}" x2="{tx:.1f}" y2="{cy:.1f}" '
                 f'stroke="#f4c20f" stroke-width="2"/>')
        s.append(f'<circle cx="{tx:.1f}" cy="{cy:.1f}" r="6.5" fill="#f4c20f"/>'
                 f'<circle cx="{tx:.1f}" cy="{cy:.1f}" r="2.6" fill="#0b1330"/>')
        s.append(f'<rect x="{chip_x:.1f}" y="{chy:.1f}" width="{CHIP_W}" height="{CHIP_H}" '
                 f'rx="17" fill="#16224a" stroke="#f4c20f" stroke-width="1.5"/>')
        s.append(f'<text x="{chip_x + CHIP_W / 2:.1f}" y="{cy + 5.5:.1f}" text-anchor="middle" '
                 f'font-size="15" font-weight="600" fill="#ffffff">{esc(label)}</text>')
    # Footer
    foot = f"{aspect}    ·    captions: {capsys}" if capsys else aspect
    s.append(f'<text x="{CANVAS_W / 2}" y="{CANVAS_H - 26}" text-anchor="middle" '
             f'font-size="15" font-weight="600" fill="#9fb0d8">{esc(foot)}</text>')
    s.append('</svg>')

    out = os.path.join(tdir, "mockup.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(s) + "\n")
    return out


def main():
    if len(sys.argv) > 1:
        dirs = [sys.argv[1]]
    else:
        dirs = sorted(glob.glob(os.path.join(REPO, "templates", "[0-9]*-*")))
    made = 0
    for d in dirs:
        out = build_one(d)
        if out:
            made += 1
            print(f"  ✓ {os.path.relpath(out, REPO)}")
        else:
            print(f"  ⚠ {os.path.basename(d.rstrip('/'))} — no thumbnail.jpg, skipped")
    print(f"✓ {made} mockup(s)")


if __name__ == "__main__":
    main()
