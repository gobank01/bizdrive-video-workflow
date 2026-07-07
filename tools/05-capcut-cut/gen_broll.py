#!/usr/bin/env python3
"""Gen AI B-roll ผ่าน OpenRouter (สูตรเดียวกับ generate-openrouter-broll.js ของ v88).

Usage: OPENROUTER_API_KEY=... python3 gen_broll.py --prompt "..." --output x.mp4
       [--model bytedance/seedance-1-5-pro] [--duration 5]
"""
import argparse, json, os, sys, time, urllib.request

API = "https://openrouter.ai/api/v1/videos"

def req(url, data=None, key=None):
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://bizdrive.local", "X-Title": "Bizdrive CapCut B-roll"})
    with urllib.request.urlopen(r, timeout=120) as resp:
        return json.loads(resp.read())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default="bytedance/seedance-1-5-pro")
    ap.add_argument("--duration", type=int, default=5)
    a = ap.parse_args()
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("no OPENROUTER_API_KEY")

    sub = req(API, {"model": a.model, "prompt": a.prompt, "aspect_ratio": "16:9",
                    "duration": a.duration, "resolution": "720p", "generate_audio": False}, key)
    print("submitted:", sub.get("id"), flush=True)
    for i in range(80):
        time.sleep(15)
        st = req(sub["polling_url"], key=key)
        print(f"poll {i+1}: {st.get('status')}", flush=True)
        if st.get("status") == "completed":
            url = (st.get("unsigned_urls") or [None])[0] or f"{API}/{st['id']}/content?index=0"
            rq = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"}
                                        if "openrouter.ai" in url else {})
            with urllib.request.urlopen(rq, timeout=300) as resp:
                open(a.output, "wb").write(resp.read())
            print("saved:", a.output)
            return
        if st.get("status") in ("failed", "cancelled", "expired"):
            sys.exit(f"job {st.get('status')}: {st.get('error')}")
    sys.exit("timed out")

if __name__ == "__main__":
    main()
