#!/usr/bin/env python3
"""Regenerate the embedded data inside tools/template-manager.html.

The Template Manager is a standalone HTML file — it carries its own copy of
every template's feature surface plus the UI label maps, so it works by
double-click with no server and no project dependency. This script keeps that
embedded copy in sync.

Sources of truth (the manager hard-codes none of this):
  - templates/NN-*/manifest.json        -> each template's features[] block
  - templates/_shared/manager-ui.json   -> section / layout / caption labels

It injects one JSON object between the
  /* TEMPLATES-DATA-START */ ... /* TEMPLATES-DATA-END */
markers in tools/template-manager.html.

Run it after adding or changing a template. You normally don't run it by hand:
  - tools/new-template.sh runs it automatically when scaffolding a template;
  - a PostToolUse hook (.claude/settings.json) runs it when a manifest changes.
Manual run:

    python3 tools/build-manager.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL_DIR = ROOT / "templates"
UI_FILE = TPL_DIR / "_shared" / "manager-ui.json"
HTML = ROOT / "tools" / "template-manager.html"
START = "/* TEMPLATES-DATA-START */"
END = "/* TEMPLATES-DATA-END */"


def layout_of(manifest: dict, tid: str) -> str:
    """Layout family — explicit manifest 'layoutType' wins, else inferred from id."""
    if manifest.get("layoutType"):
        return manifest["layoutType"]
    if "stacked" in tid:
        return "stacked"
    if "top-insert" in tid:
        return "top-insert"
    return "fullscreen"


def main() -> None:
    ui = {}
    if UI_FILE.exists():
        ui = json.loads(UI_FILE.read_text(encoding="utf-8"))
    else:
        print(f"  ⚠ {UI_FILE.name} missing — UI labels fall back to raw ids", file=sys.stderr)

    templates = []
    for d in sorted(TPL_DIR.glob("[0-9][0-9]-*")):
        mf = d / "manifest.json"
        if not mf.exists():
            print(f"  ⚠ {d.name}/manifest.json missing — skipped", file=sys.stderr)
            continue
        m = json.loads(mf.read_text(encoding="utf-8"))
        tid = m.get("id", d.name)
        if "features" not in m:
            print(f"  ⚠ {tid} has no 'features' block — skipped", file=sys.stderr)
            continue
        templates.append({
            "num": tid.split("-")[0],
            "id": tid,
            "name": m.get("name", tid),
            "desc": m.get("description", ""),
            "layout": layout_of(m, tid),
            "captionSystem": (m.get("captions") or {}).get("system", ""),
            "features": m["features"],
        })

    if not templates:
        print(f"✗ no usable templates found under {TPL_DIR}", file=sys.stderr)
        sys.exit(1)
    if not HTML.exists():
        print(f"✗ {HTML} not found — create the manager HTML first", file=sys.stderr)
        sys.exit(1)

    data = {"ui": ui, "templates": templates}
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    html = HTML.read_text(encoding="utf-8")
    pat = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pat.search(html):
        print(f"✗ data markers not found in {HTML}", file=sys.stderr)
        sys.exit(1)
    html = pat.sub(f"{START}\nwindow.HF_DATA = {payload};\n{END}", html)
    HTML.write_text(html, encoding="utf-8")

    print(f"✓ injected {len(templates)} templates into {HTML.relative_to(ROOT)}")
    for t in templates:
        print(f"  · {t['num']}  {t['id']}  ({len(t['features'])} features)")


if __name__ == "__main__":
    main()
