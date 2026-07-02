#!/usr/bin/env python3
"""
inbox-dashboard.py — สแกนโฟลเดอร์ inbox "ออกจาก Studio" แล้วสร้าง Dashboard HTML
แบบ self-contained (เปิดด้วยดับเบิลคลิกได้ ไม่ต้องรัน server).

สถานะอ่านจาก prefix ของชื่อโฟลเดอร์ (กฎ inbox-rename-on-done-posted):
  - ขึ้นต้น "โพสแล้ว"  → posted   (ตัด + โพสต์แล้ว)
  - ขึ้นต้น "ตัดแล้ว"  → cut      (ตัดแล้ว ยังไม่โพสต์)
  - อื่น ๆ            → uncut    (ยังไม่ตัด — งานค้างจริง)

รันซ้ำเมื่อต้องการ refresh:
  python3 tools/inbox-dashboard.py            # เปิดให้อัตโนมัติ
  python3 tools/inbox-dashboard.py --no-open  # สร้างไฟล์เฉย ๆ

Output: tools/inbox-dashboard.html
"""
import os, sys, json, subprocess, base64, datetime

INBOX = "/Users/gobank01/Desktop/BizDrive/Class เรียน/VDO/ออกจาก Studio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inbox-dashboard.html")
VIDEO_EXTS = (".mp4", ".mov", ".m4v")

def status_of(name):
    if name.startswith("โพสแล้ว"):
        return "posted"
    if name.startswith("ตัดแล้ว"):
        return "cut"
    return "uncut"

def clean_title(name):
    for p in ("โพสแล้ว", "ตัดแล้ว"):
        while name.startswith(p):
            name = name[len(p):].lstrip()
    return name or name

def ffprobe_dur(path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True, timeout=30).stdout.strip()
        return float(out) if out else None
    except Exception:
        return None

def thumb_b64(video):
    """ดึง 1 เฟรมที่ ~2s ย่อกว้าง 360 → base64 jpg (ฝังในไฟล์เลย)."""
    try:
        proc = subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "error", "-ss", "2", "-i", video,
             "-vframes", "1", "-vf", "scale=360:-1", "-q:v", "5",
             "-f", "image2pipe", "-vcodec", "mjpeg", "pipe:1"],
            capture_output=True, timeout=40)
        if proc.returncode == 0 and proc.stdout:
            return "data:image/jpeg;base64," + base64.b64encode(proc.stdout).decode()
    except Exception:
        pass
    return ""

def human_size(b):
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.0f}{u}" if u == "B" else f"{b:.1f}{u}"
        b /= 1024
    return f"{b:.1f}TB"

def fmt_dur(s):
    if not s:
        return "—"
    m, sec = divmod(int(round(s)), 60)
    return f"{m}:{sec:02d}"

def scan():
    items = []
    if not os.path.isdir(INBOX):
        return items
    for name in sorted(os.listdir(INBOX)):
        full = os.path.join(INBOX, name)
        if name.startswith(".") or not os.path.isdir(full):
            continue
        vids = [f for f in os.listdir(full) if f.lower().endswith(VIDEO_EXTS)]
        # เลือกไฟล์ทำ thumbnail: top.mp4 (จอ = เห็นเนื้อหา) ก่อน, ไม่งั้น face cam
        thumb_src = None
        for pref in ("top.mp4", "Bottom02.mp4", "bottom.mp4"):
            if pref in vids:
                thumb_src = os.path.join(full, pref); break
        if not thumb_src and vids:
            thumb_src = os.path.join(full, vids[0])
        # วัดความยาวจาก face cam (master audio)
        dur_src = None
        for pref in ("Bottom02.mp4", "bottom.mp4", "top.mp4"):
            if pref in vids:
                dur_src = os.path.join(full, pref); break
        total = 0
        for f in vids:
            try:
                total += os.path.getsize(os.path.join(full, f))
            except OSError:
                pass
        mtime = os.path.getmtime(full)
        items.append({
            "name": name,
            "title": clean_title(name),
            "status": status_of(name),
            "videos": sorted(vids),
            "dur": fmt_dur(ffprobe_dur(dur_src)) if dur_src else "—",
            "size": human_size(total) if total else "—",
            "modified": datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M"),
            "thumb": thumb_b64(thumb_src) if thumb_src else "",
            "path": full,
        })
    # เรียง: uncut ก่อน (งานค้าง) → cut → posted, ในกลุ่มเรียงตามแก้ไขล่าสุด
    order = {"uncut": 0, "cut": 1, "posted": 2}
    items.sort(key=lambda x: (order[x["status"]], x["modified"]), reverse=False)
    items.sort(key=lambda x: order[x["status"]])
    return items

def render(items):
    counts = {"uncut": 0, "cut": 0, "posted": 0}
    for it in items:
        counts[it["status"]] += 1
    data = json.dumps(items, ensure_ascii=False)
    gen_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return TEMPLATE.replace("__DATA__", data)\
                   .replace("__UNCUT__", str(counts["uncut"]))\
                   .replace("__CUT__", str(counts["cut"]))\
                   .replace("__POSTED__", str(counts["posted"]))\
                   .replace("__TOTAL__", str(len(items)))\
                   .replace("__GENAT__", gen_at)\
                   .replace("__INBOX__", INBOX)

TEMPLATE = r"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BizDrive — Inbox Dashboard (ออกจาก Studio)</title>
<style>
  :root{ --blue:#1B3A8C; --blue-deep:#0D1F4F; --gold:#F4C20F; --gold-hi:#FFD93D;
         --soft:#B8C4DE; --bg:#0b1430; --card:#13204a; --line:#26356b; }
  *{ box-sizing:border-box; }
  body{ margin:0; font-family:"IBM Plex Sans Thai","Sukhumvit Set",-apple-system,
        "Segoe UI",sans-serif; background:linear-gradient(160deg,#0b1430,#0d1f4f);
        color:#eaf0ff; min-height:100vh; }
  header{ padding:26px 30px 18px; border-bottom:1px solid var(--line); }
  h1{ margin:0 0 4px; font-size:24px; letter-spacing:.3px; }
  h1 .chev{ color:var(--gold); }
  .sub{ color:var(--soft); font-size:13px; }
  .sub code{ background:#0008; padding:2px 7px; border-radius:6px; color:#cfe; }
  .stats{ display:flex; gap:12px; flex-wrap:wrap; padding:18px 30px 6px; }
  .stat{ background:var(--card); border:1px solid var(--line); border-radius:14px;
         padding:12px 18px; min-width:120px; cursor:pointer; transition:.15s;
         user-select:none; }
  .stat:hover{ border-color:var(--gold); transform:translateY(-2px); }
  .stat.active{ outline:2px solid var(--gold); }
  .stat .n{ font-size:30px; font-weight:800; line-height:1; }
  .stat .l{ font-size:12px; color:var(--soft); margin-top:6px; }
  .stat.uncut .n{ color:#ff8f6b; } .stat.cut .n{ color:var(--gold-hi); }
  .stat.posted .n{ color:#5fe0a8; } .stat.all .n{ color:#fff; }
  .grid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
         gap:16px; padding:20px 30px 60px; }
  .card{ background:var(--card); border:1px solid var(--line); border-radius:16px;
         overflow:hidden; display:flex; flex-direction:column; transition:.15s; }
  .card:hover{ border-color:var(--gold); transform:translateY(-3px);
               box-shadow:0 10px 30px #0006; }
  .thumb{ aspect-ratio:16/9; background:#06102b center/cover no-repeat;
          position:relative; display:flex; align-items:center; justify-content:center; }
  .thumb .ph{ color:#3b4d85; font-size:34px; }
  .badge{ position:absolute; top:10px; left:10px; font-size:11px; font-weight:700;
          padding:4px 10px; border-radius:20px; backdrop-filter:blur(4px); }
  .b-uncut{ background:#ff8f6bdd; color:#3a1400; }
  .b-cut{ background:#f4c20fdd; color:#3a2c00; }
  .b-posted{ background:#5fe0a8dd; color:#003a22; }
  .body{ padding:13px 15px 15px; flex:1; display:flex; flex-direction:column; gap:8px; }
  .title{ font-size:15px; font-weight:700; line-height:1.35; }
  .meta{ display:flex; flex-wrap:wrap; gap:6px 12px; font-size:12px; color:var(--soft); }
  .meta b{ color:#dfe8ff; font-weight:600; }
  .files{ display:flex; flex-wrap:wrap; gap:5px; margin-top:2px; }
  .chip{ font-size:10.5px; background:#0c1838; border:1px solid var(--line);
         color:#9fb2e6; padding:2px 7px; border-radius:6px; }
  .empty{ padding:60px; text-align:center; color:var(--soft); grid-column:1/-1; }
  footer{ padding:14px 30px 40px; color:#6f80b5; font-size:12px;
          border-top:1px solid var(--line); }
  .hl{ color:var(--gold); }
</style>
</head>
<body>
<header>
  <h1><span class="chev">▸</span> BizDrive Inbox — <span class="hl">ออกจาก Studio</span></h1>
  <div class="sub">ต้นทาง: <code>__INBOX__</code> · อัปเดตล่าสุด __GENAT__
    · รันใหม่: <code>python3 tools/inbox-dashboard.py</code></div>
</header>

<div class="stats" id="stats">
  <div class="stat all active" data-f="all"><div class="n">__TOTAL__</div><div class="l">ทั้งหมด</div></div>
  <div class="stat uncut" data-f="uncut"><div class="n">__UNCUT__</div><div class="l">🔴 ยังไม่ตัด</div></div>
  <div class="stat cut" data-f="cut"><div class="n">__CUT__</div><div class="l">✂️ ตัดแล้ว</div></div>
  <div class="stat posted" data-f="posted"><div class="n">__POSTED__</div><div class="l">🚀 โพสแล้ว</div></div>
</div>

<div class="grid" id="grid"></div>
<footer>BizDrive Video V3 · สถานะอ่านจาก prefix ชื่อโฟลเดอร์ (ตัดแล้ว / โพสแล้ว) — ไม่พึ่ง jobs/ ที่ลบได้</footer>

<script>
const DATA = __DATA__;
const LABEL = { uncut:"🔴 ยังไม่ตัด", cut:"✂️ ตัดแล้ว", posted:"🚀 โพสแล้ว" };
const grid = document.getElementById('grid');
let filter = 'all';

function esc(s){ return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

function render(){
  const list = DATA.filter(d => filter==='all' || d.status===filter);
  if(!list.length){ grid.innerHTML = '<div class="empty">— ไม่มีรายการในกลุ่มนี้ —</div>'; return; }
  grid.innerHTML = list.map(d => `
    <div class="card">
      <div class="thumb" style="${d.thumb?`background-image:url('${d.thumb}')`:''}">
        ${d.thumb?'':'<span class="ph">🎬</span>'}
        <span class="badge b-${d.status}">${LABEL[d.status]}</span>
      </div>
      <div class="body">
        <div class="title">${esc(d.title)}</div>
        <div class="meta"><span>⏱ <b>${d.dur}</b></span><span>💾 <b>${d.size}</b></span>
          <span>📅 ${esc(d.modified)}</span></div>
        <div class="files">${d.videos.map(f=>`<span class="chip">${esc(f)}</span>`).join('')||'<span class="chip">ไม่มีวิดีโอ</span>'}</div>
      </div>
    </div>`).join('');
}
document.querySelectorAll('.stat').forEach(s=>{
  s.onclick=()=>{ filter=s.dataset.f;
    document.querySelectorAll('.stat').forEach(x=>x.classList.remove('active'));
    s.classList.add('active'); render(); };
});
render();
</script>
</body>
</html>
"""

def main():
    items = scan()
    html_out = render(items)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html_out)
    c = {"uncut": 0, "cut": 0, "posted": 0}
    for it in items:
        c[it["status"]] += 1
    print(f"✓ {OUT}")
    print(f"  {len(items)} clips — 🔴 ยังไม่ตัด {c['uncut']} · ✂️ ตัดแล้ว {c['cut']} · 🚀 โพสแล้ว {c['posted']}")
    if "--no-open" not in sys.argv:
        subprocess.run(["open", OUT])

if __name__ == "__main__":
    main()
