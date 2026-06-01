#!/usr/bin/env python3
"""V88 T07 chunked workflow — query or update a chunk's status.

Reads/writes the master state at `<job>/chunks.json`.

Usage (run from the job workspace):

    # Print the whole status table (one line per chunk)
    python3 scripts/chunk-status.py

    # Mark a chunk as having reached a state
    python3 scripts/chunk-status.py 03 transcribed
    python3 scripts/chunk-status.py 03 polished       --note "manual EDL fix"
    python3 scripts/chunk-status.py 03 rendered
    python3 scripts/chunk-status.py 03 failed:render  --note "OOM at frame 4200"

Statuses (in pipeline order):
    sliced → transcribed → polished → captioned → composed → rendered

Anything else (e.g. `failed:render`) is also allowed — useful for debugging.

`merge-chunks.py` refuses to merge unless every chunk is `rendered`.
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
JOB_DIR = WS.parent
STATE = JOB_DIR / "chunks.json"

ORDER = ["sliced", "transcribed", "polished", "captioned", "composed", "rendered"]
SYMBOL = {
    "sliced":      "·",
    "transcribed": "T",
    "polished":    "P",
    "captioned":   "C",
    "composed":    "M",
    "rendered":    "✓",
}


def load() -> dict:
    if not STATE.exists():
        print(f"✗ no chunks.json — run split-chunks.py first", file=sys.stderr)
        sys.exit(1)
    return json.loads(STATE.read_text(encoding="utf-8"))


def save(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def show(state: dict) -> None:
    rows = state["chunks"]
    print(f"chunks.json — {state['totalChunks']} chunks "
          f"({state['chunkMinutes']:.1f} min each, source {state['sourceDuration']:.1f}s)")
    print()
    print(f"  {'id':>3}  {'start':>7}  {'end':>7}  {'dur':>6}  status")
    print("  " + "-" * 50)
    progress_marks = []
    for c in rows:
        sym = SYMBOL.get(c["status"], "?")
        progress_marks.append(sym)
        print(f"  {c['id']:>3}  {c['start']:>7.2f}  {c['end']:>7.2f}  "
              f"{c['duration']:>6.2f}  {c['status']}")
    print()
    print("  progress: [" + " ".join(progress_marks) + "]")
    ready = sum(1 for c in rows if c["status"] == "rendered")
    print(f"  → {ready}/{len(rows)} chunks rendered "
          f"({'READY to merge' if ready == len(rows) else 'not ready'})")


def update(state: dict, chunk_id: str, status: str, note: str | None) -> None:
    chunk = next((c for c in state["chunks"] if c["id"] == chunk_id), None)
    if not chunk:
        print(f"✗ chunk {chunk_id} not found in chunks.json", file=sys.stderr)
        sys.exit(1)
    chunk["status"] = status
    chunk.setdefault("logs", []).append({
        "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "step": status,
        "note": note,
        "ok": not status.startswith("failed"),
    })
    save(state)
    print(f"  ✓ chunk {chunk_id} → {status}{'  ('+note+')' if note else ''}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("chunk_id", nargs="?", help="e.g. 01, 02 (omit to show table)")
    ap.add_argument("status", nargs="?", help="new status (sliced/transcribed/.../rendered/failed:...)")
    ap.add_argument("--note", default=None, help="optional log note")
    args = ap.parse_args()

    state = load()
    if not args.chunk_id:
        show(state)
        return 0
    if not args.status:
        chunk = next((c for c in state["chunks"] if c["id"] == args.chunk_id), None)
        if not chunk:
            print(f"✗ chunk {args.chunk_id} not found", file=sys.stderr)
            return 1
        print(json.dumps(chunk, indent=2, ensure_ascii=False))
        return 0
    update(state, args.chunk_id, args.status, args.note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
