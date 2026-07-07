#!/usr/bin/env python3
"""แปลง EL transcript + fine-VAD -> EDL ละเอียด + caption chunks (edited timeline).

Usage: prep_captions.py --transcript raw.json --vad vad-fine.json --out-prefix x
เขียน: <prefix>-edl.json (jump cuts ทุก phrase boundary) + <prefix>-captions.json
กฎ caption ตาม repo: แบ่ง <=14 ตัว (pythainlp), ตัด นะครับ/นะคับ, แก้สะกด
Claude Code/Vibe Code, offset -120ms (EL phrase lag)
"""
import argparse, json, re
from pythainlp import word_tokenize

FIX = [(r"[Qq]uod\s*Code", "Claude Code"), (r"คอร์สโค้ช|คลอสโค้ด|Cloud Code", "Claude Code"),
       (r"^[Qq]uod$", "Claude"), (r"^คลอด$", "Claude"),
       (r"[Ww]rite\s*Code", "Vibe Code"), (r"นะครับผม|นะครับ|นะคับ", " ")]
MAXC = 14

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--vad", required=True)
    ap.add_argument("--out-prefix", required=True)
    a = ap.parse_args()
    vad = json.load(open(a.vad))
    tr = json.load(open(a.transcript))

    # keeps + จุดตัดภายใน (boundary ที่ padding เชื่อมชิดกัน = จุด jump cut ธรรมชาติ)
    keeps = []
    for r in vad:
        s, e = int(r["start"]*1000), int(r["end"]*1000)
        if keeps and s - keeps[-1][1] < 50:
            keeps[-1][2].append(s); keeps[-1][1] = e
        else:
            keeps.append([s, e, []])
    fine = []
    for s, e, cuts in keeps:
        pts = [s] + cuts + [e]
        fine += [{"start_ms": pts[i], "end_ms": pts[i+1]} for i in range(len(pts)-1)]
    json.dump({"segments": fine}, open(f"{a.out_prefix}-edl.json", "w"), ensure_ascii=False)
    tot = sum(x["end_ms"]-x["start_ms"] for x in fine)

    spans, pos = [], 0
    for s, e, _ in keeps:
        spans.append((s, e, pos)); pos += e - s
    def remap(ms):
        for s, e, t in spans:
            if ms < s: return t
            if ms <= e: return t + ms - s
        return pos

    chunks = []
    for w in tr["words"]:
        txt = w["text"]
        for pat, rep in FIX: txt = re.sub(pat, rep, txt)
        txt = re.sub(r"\s+", " ", txt).strip()
        if not txt: continue
        toks = [t for t in word_tokenize(txt, engine="newmm") if t.strip()]
        groups, cur = [], ""
        for t in toks:
            if cur and len(cur) + len(t) > MAXC: groups.append(cur); cur = t
            else: cur += t
        if cur: groups.append(cur)
        n = sum(len(g) for g in groups) or 1
        t0, t1 = w["start"]*1000, w["end"]*1000
        acc = 0
        for g in groups:
            gs = t0 + (t1-t0)*acc/n; acc += len(g)
            chunks.append({"text": g.strip(), "src_s": gs, "src_e": t0 + (t1-t0)*acc/n})
    caps = []
    for c in chunks:
        s = max(0, remap(c["src_s"]) - 120); e = max(0, remap(c["src_e"]) - 120)
        if e - s < 120: e = s + 120
        if caps and s < caps[-1]["end_ms"]: s = caps[-1]["end_ms"]
        if e <= s: e = s + 100
        caps.append({"text": c["text"], "start_ms": int(s), "end_ms": int(e)})
    caps = [c for c in caps if c["end_ms"] <= tot + 500 and c["text"]]
    json.dump(caps, open(f"{a.out_prefix}-captions.json", "w"), ensure_ascii=False)
    print(f"EDL {len(fine)} segments ({tot/1000:.1f}s) | captions {len(caps)} chunks")

if __name__ == "__main__":
    main()
