#!/usr/bin/env python3
"""
inbox-sync.py — สแกนโฟลเดอร์ inbox "ออกจาก Studio" บนเครื่อง แล้วดันสถานะ (auto)
ขึ้น dashboard ออนไลน์ (Vercel) เพื่อเช็คจากมือถือได้

สถานะ auto อ่านจากไฟล์ + prefix ชื่อโฟลเดอร์ (กฎ inbox-rename-on-done-posted):
  - มี bottom.mp4/top.mp4            → rawPresent
  - มี Bottom02.mp4                  → bottom02Present (ทำหน้าใสแล้ว)
  - prefix "ตัดแล้ว" หรือ "โพสแล้ว"   → cutDone
  - prefix "โพสแล้ว"                  → autopostDone (โพส auto 2 กลุ่มแล้ว)

flag มือ (โพส FB ส่วนตัว) อยู่ในฐานข้อมูลออนไลน์ — สคริปต์นี้ "ไม่แตะ"

จับคู่ไอเดีย → ไฟล์ (สาย "อัดแล้ว → เตรียมตัดต่อ"):
  ไอเดียที่กด "อัดแล้ว" บนกระดาน (editStatus='recorded') ถ้าหาโฟลเดอร์ที่ชื่อตรงกัน
  และมี Bottom02.mp4 ครบ → เลื่อนเป็น "พร้อมตัด" (editStatus='ready') ให้อัตโนมัติ
  รออนุมัติบนกระดานก่อนตัดจริง (semi-auto)

ใช้:
  python3 tools/inbox-sync.py          # สแกน + ดันขึ้นออนไลน์ + จับคู่ไอเดีย
  python3 tools/inbox-sync.py --dry    # ดูผลเฉย ๆ ไม่ส่ง
"""
import os, sys, json, subprocess, base64, datetime, urllib.request

INBOX = "/Users/gobank01/Desktop/BizDrive/Class เรียน/VDO/ออกจาก Studio"
ENDPOINT = "https://bizdrive-social-poster.vercel.app/api/inbox"
IDEAS_ENDPOINT = "https://bizdrive-social-poster.vercel.app/api/ideas"
BLOTATO_ENV = "/Users/gobank01/Documents/Post Social - Blotato/.env"
VIDEO_EXTS = (".mp4", ".mov", ".m4v")

def secret():
    try:
        for line in open(BLOTATO_ENV, encoding="utf-8"):
            if line.strip().startswith("INBOX_SECRET="):
                return line.split("=", 1)[1].strip().strip('"\'')
    except OSError:
        pass
    return ""

def clean_title(name):
    for p in ("โพสแล้ว", "ตัดแล้ว"):
        while name.startswith(p):
            name = name[len(p):].lstrip()
    return name

def ffprobe_dur(path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True, timeout=30).stdout.strip()
        return float(out) if out else None
    except Exception:
        return None

def fmt_dur(s):
    if not s:
        return "—"
    m, sec = divmod(int(round(s)), 60)
    return f"{m}:{sec:02d}"

def human_size(b):
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.0f}{u}" if u == "B" else f"{b:.1f}{u}"
        b /= 1024
    return f"{b:.1f}TB"

def thumb_b64(video):
    try:
        p = subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "error", "-ss", "2", "-i", video,
             "-vframes", "1", "-vf", "scale=320:-1", "-q:v", "6",
             "-f", "image2pipe", "-vcodec", "mjpeg", "pipe:1"],
            capture_output=True, timeout=40)
        if p.returncode == 0 and p.stdout:
            return "data:image/jpeg;base64," + base64.b64encode(p.stdout).decode()
    except Exception:
        pass
    return ""

def scan():
    clips = []
    if not os.path.isdir(INBOX):
        print(f"✗ ไม่พบโฟลเดอร์ inbox: {INBOX}", file=sys.stderr)
        return clips
    for name in sorted(os.listdir(INBOX)):
        full = os.path.join(INBOX, name)
        if name.startswith(".") or not os.path.isdir(full):
            continue
        vids = [f for f in os.listdir(full) if f.lower().endswith(VIDEO_EXTS)]
        has = lambda f: f in vids
        posted = name.startswith("โพสแล้ว")
        cut = posted or name.startswith("ตัดแล้ว")
        # thumbnail: top.mp4 (จอ = เห็นเนื้อหา) ก่อน, ไม่งั้น face cam
        thumb_src = None
        for pref in ("top.mp4", "Bottom02.mp4", "bottom.mp4"):
            if has(pref):
                thumb_src = os.path.join(full, pref); break
        if not thumb_src and vids:
            thumb_src = os.path.join(full, vids[0])
        dur_src = None
        for pref in ("Bottom02.mp4", "bottom.mp4", "top.mp4"):
            if has(pref):
                dur_src = os.path.join(full, pref); break
        total = 0
        for f in vids:
            try: total += os.path.getsize(os.path.join(full, f))
            except OSError: pass
        clips.append({
            "id": clean_title(name) or name,
            "folder": name,
            "title": clean_title(name) or name,
            "rawPresent": has("bottom.mp4") or has("top.mp4"),
            "bottom02Present": has("Bottom02.mp4"),
            "cutDone": cut,
            "autopostDone": posted,
            "dur": fmt_dur(ffprobe_dur(dur_src)) if dur_src else "—",
            "size": human_size(total) if total else "—",
            "videos": sorted(vids),
            "thumb": thumb_b64(thumb_src) if thumb_src else "",
            "modified": datetime.datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y-%m-%d %H:%M"),
        })
    return clips

def post(payload, endpoint=ENDPOINT):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read().decode()

def get_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

def norm(s):
    """เหลือเฉพาะตัวอักษร/ตัวเลข (ไทยด้วย) — ใช้เทียบชื่อหัวข้อกับชื่อโฟลเดอร์"""
    return "".join(ch for ch in (s or "").lower() if ch.isalnum())

def match_ideas(clips):
    """
    จับคู่ไอเดียที่ 'อัดแล้ว' (recorded) กับโฟลเดอร์ที่มี Bottom02.mp4 ครบ
    → เลื่อนเป็น 'ready' (พร้อมตัด) บนกระดานออนไลน์ รออนุมัติ
    ปลอดภัย: เลื่อนขึ้นอย่างเดียว ไม่ถอยสถานะ, จับคู่แบบ normalized contains (กันชนกัน)
    """
    try:
        ideas = (get_json(IDEAS_ENDPOINT) or {}).get("ideas", [])
    except Exception as e:
        print(f"  (ข้ามจับคู่ไอเดีย: ดึง /api/ideas ไม่ได้ — {e})", file=sys.stderr)
        return
    # 'recorded' รวมไอเดียเก่าที่กด "อัดแล้ว" ก่อนมีฟีเจอร์นี้ (editStatus ว่าง + done=true)
    recorded = [i for i in ideas
                if (i.get("editStatus") or "") == "recorded"
                or (i.get("done") and not i.get("editStatus"))]
    ready_clips = [c for c in clips if c.get("bottom02Present")]
    if not recorded or not ready_clips:
        return
    used = set()
    promoted = 0
    for idea in recorded:
        a = norm(idea.get("topic"))
        if len(a) < 6:
            continue
        for c in ready_clips:
            if c["folder"] in used:
                continue
            b = norm(c.get("title"))
            if len(b) < 6:
                continue
            if a in b or b in a:
                try:
                    post({"action": "editstatus", "id": idea["id"],
                          "status": "ready", "clipFolder": c["folder"]}, IDEAS_ENDPOINT)
                    used.add(c["folder"]); promoted += 1
                    print(f"  ✅ พร้อมตัด: “{idea.get('topic')}” ↔ 📂 {c['folder']}")
                except Exception as e:
                    print(f"  (เลื่อนสถานะไม่สำเร็จ: {idea.get('topic')} — {e})", file=sys.stderr)
                break
    if promoted:
        print(f"  → เลื่อนเป็น “พร้อมตัด” {promoted} ไอเดีย — รออนุมัติบนกระดาน /ideas.html")

def main():
    clips = scan()
    summary = {}
    for c in clips:
        st = ("posted" if c["autopostDone"] else "cut" if c["cutDone"]
              else "ready" if c["bottom02Present"] else "raw")
        summary[st] = summary.get(st, 0) + 1
    print(f"สแกนเจอ {len(clips)} คลิป — "
          f"🔴ดิบ {summary.get('raw',0)} · 🟠พร้อมตัด {summary.get('ready',0)} · "
          f"🟡ตัดแล้ว {summary.get('cut',0)} · 🔵โพสauto {summary.get('posted',0)}")
    for c in clips:
        flags = "".join([
            "B" if c["bottom02Present"] else "-",
            "C" if c["cutDone"] else "-",
            "P" if c["autopostDone"] else "-"])
        print(f"   [{flags}] {c['title']}")
    if "--dry" in sys.argv:
        print("(dry-run — ไม่ส่ง)")
        return
    payload = {"action": "sync", "clips": clips}
    sec = secret()
    if sec:
        payload["secret"] = sec
    try:
        status, body = post(payload)
        print(f"✓ ส่งขึ้นออนไลน์: HTTP {status} — {body[:200]}")
        print(f"  ดูได้ที่: https://bizdrive-social-poster.vercel.app/inbox.html")
    except Exception as e:
        print(f"✗ ส่งไม่สำเร็จ: {e}", file=sys.stderr)
        sys.exit(1)
    # จับคู่ไอเดีย 'อัดแล้ว' กับไฟล์ที่ครบ → เลื่อนเป็น 'พร้อมตัด'
    match_ideas(clips)

if __name__ == "__main__":
    main()
