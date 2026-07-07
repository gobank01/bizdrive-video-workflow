#!/usr/bin/env python3
"""Tool 05 — CapCut pre-cut: ตัด dead air ลง draft CapCut ให้เสร็จ ผู้ใช้แค่เปิดแอปแล้ว export

Usage:
  python3 tools/05-capcut-cut/capcut_cut.py <draft-name> [--media PATH]
      [--min-silence-ms 300] [--pad-ms 200] [--merge-gap-ms 0] [--suffix " AI cut"]
      [--edl PATH]

--edl = ข้าม VAD แล้วใช้ EDL shape กลางของ repo {"segments":[{start_ms,end_ms}]}
(ผลจาก editorial pass / speech_to_edl.py / refine_edl.py ใช้ได้หมด)
สร้าง draft สำเนาชื่อ "<draft-name><suffix>" — ไม่แตะ draft ต้นฉบับเด็ดขาด
ต้องมี: ffmpeg, ~/.bizdrive/vad-env (Silero VAD จาก install_vad.sh), macOS CapCut
Contract: draft ต้นฉบับต้องมี video track เดียวที่มี segment เต็มเส้น 1 ชิ้น
(workflow "โยนคลิปดิบเข้า CapCut แล้วให้ Claude ตัด") — เกินกว่านั้นสคริปต์จะ refuse
"""
import argparse, copy, json, os, shutil, subprocess, sys, tempfile, time, uuid

DRAFT_ROOT = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")
VAD_PY = next((p for p in (
    os.path.expanduser("~/.bizdrive/vad-env/bin/python3"),
    os.path.expanduser("~/.bizdrive/vad-env/Scripts/python.exe"),
) if os.path.exists(p)), None)
VAD_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "..", "templates", "_shared", "scripts", "clean-cut", "vad_detect.py")

def die(msg):
    sys.exit(f"error: {msg}")

def new_id():
    return str(uuid.uuid4()).upper()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--media", help="override media path ถ้าไฟล์ใน draft ย้าย/rename ไปแล้ว")
    ap.add_argument("--min-silence-ms", type=int, default=300)
    ap.add_argument("--pad-ms", type=int, default=200)
    ap.add_argument("--merge-gap-ms", type=int, default=0)
    ap.add_argument("--suffix", default=" AI cut")
    ap.add_argument("--edl", help="EDL JSON {'segments':[{start_ms,end_ms}]} — ข้าม VAD")
    ap.add_argument("--name", help="ชื่อ draft ปลายทางตรงๆ (แทน <draft><suffix>)")
    a = ap.parse_args()

    src = os.path.join(DRAFT_ROOT, a.draft)
    dst_name = a.name or (a.draft + a.suffix)
    dst = os.path.join(DRAFT_ROOT, dst_name)
    if not os.path.isfile(os.path.join(src, "draft_info.json")):
        die(f"ไม่พบ draft: {src}")
    if not a.edl and not VAD_PY:
        die("ไม่พบ ~/.bizdrive/vad-env — รัน templates/_shared/scripts/clean-cut/install_vad.sh ก่อน")

    d = json.load(open(os.path.join(src, "draft_info.json")))
    vtracks = [t for t in d["tracks"] if t["type"] == "video"]
    others = [t for t in d["tracks"] if t["type"] != "video" and t.get("segments")]
    if not vtracks or others or any(len(t["segments"]) != 1 for t in vtracks):
        die("รองรับเฉพาะ draft ดิบ (video track ละ 1 segment เต็มเส้น, ไม่มี track อื่น) — draft นี้ถูกตัดไปแล้วหรือซับซ้อนเกิน")
    vids = d["materials"]["videos"]
    by_id = {v["id"]: v for v in vids}

    # ไฟล์เสียงสำหรับ VAD: --media > ไฟล์ชื่อ bottom* (face master ตามธรรมเนียม repo) > ตัวแรกที่มีเสียง
    if len(vids) == 1 and a.media:
        vids[0]["path"] = a.media  # single-cam: ยอมให้ย้าย path ได้ด้วย
    cands = [v for v in vids if "bottom" in os.path.basename(v["path"]).lower()] \
            or [v for v in vids if v.get("has_audio")] or vids
    media = a.media or cands[0]["path"]
    missing = [v["path"] for v in vids if not os.path.isfile(v["path"])]
    if missing:
        die(f"ไฟล์วิดีโอหาย: {missing} — ย้ายไฟล์กลับหรือ (single-cam) ใช้ --media")
    if not os.path.isfile(media):
        die(f"ไฟล์เสียงสำหรับ VAD ไม่อยู่ที่ {media}")
    mat_dur = min(v["duration"] for v in vids)  # µs — cap ที่กล้องที่สั้นสุด กัน source เกิน

    # 1) keep ranges: จาก EDL (editorial/ภายนอก) หรือจาก Silero VAD
    if a.edl:
        edl = json.load(open(a.edl))
        segs_in = edl["segments"] if isinstance(edl, dict) else edl
        keeps = [(int(s["start_ms"] * 1000), min(int(s["end_ms"] * 1000), mat_dur)) for s in segs_in]
        src_label = "EDL"
    else:
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "a.wav")
            vad_out = os.path.join(tmp, "vad.json")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", media, "-ac", "1", "-ar", "16000", wav], check=True)
            subprocess.run([VAD_PY, VAD_SCRIPT, wav,
                            "--min-silence-ms", str(a.min_silence_ms), "--pad-ms", str(a.pad_ms),
                            "--merge-gap-ms", str(a.merge_gap_ms), "--output", vad_out], check=True)
            keeps = [(int(r["start"] * 1e6), min(int(r["end"] * 1e6), mat_dur))
                     for r in json.load(open(vad_out))]
        src_label = "VAD"
    keeps = [(s, e) for s, e in keeps if e > s]
    if not keeps:
        die("ไม่มีช่วงให้เก็บเลย")
    if any(keeps[i][0] < keeps[i-1][1] for i in range(1, len(keeps))):
        die("keep ranges ทับซ้อน/ไม่เรียงเวลา — เช็ก EDL")
    total = sum(e - s for s, e in keeps)
    cut_s = (mat_dur - total) / 1e6
    print(f"{src_label}: {len(keeps)} ช่วง | เก็บ {total/1e6:.1f}s | ตัดทิ้ง {cut_s:.1f}s")

    # 2) copy draft folder (rerun-safe: ทับสำเนาเก่าของตัวเองได้ แต่ไม่แตะต้นฉบับ)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    old_tl = d["id"]
    for junk in (".locked", os.path.join("Timelines", old_tl, "draft.extra")):
        p = os.path.join(dst, junk)
        if os.path.exists(p):
            os.remove(p)

    # regenerate internal ids — สำเนาที่แชร์ timeline/project id กับต้นฉบับทำให้
    # CapCut เห็นเป็น draft ซ้ำแล้ว auto-rename ต้นฉบับเป็น "(1)" (เจอจริง 2026-07-07)
    tl_id = new_id()
    id_map = {old_tl: tl_id}
    proj_path = os.path.join(dst, "Timelines", "project.json")
    if os.path.exists(proj_path):
        proj = json.load(open(proj_path))
        if proj.get("id"):
            id_map[proj["id"]] = new_id()
    for base_dir, _, files in os.walk(dst):
        for fn in files:
            p = os.path.join(base_dir, fn)
            try:
                txt = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue  # binary (cover, crypto store, buffers)
            if any(k in txt for k in id_map):
                for k, v in id_map.items():
                    txt = txt.replace(k, v)
                open(p, "w", encoding="utf-8").write(txt)
    old_tl_dir = os.path.join(dst, "Timelines", old_tl)
    if os.path.isdir(old_tl_dir):
        os.rename(old_tl_dir, os.path.join(dst, "Timelines", tl_id))
    d["id"] = tl_id

    # 3) rewrite timeline: ทุก video track ตัดด้วย keeps ชุดเดียวกัน (multi-cam ยัง sync)
    d["duration"] = total
    if len(vids) == 1:
        vids[0]["path"] = media
        vids[0]["material_name"] = os.path.basename(media)
    mat_index = {}
    for kind, lst in d["materials"].items():
        if isinstance(lst, list):
            for m in lst:
                if isinstance(m, dict) and "id" in m:
                    mat_index[m["id"]] = (kind, m)
    for track in vtracks:
        base = track["segments"][0]
        segs, pos = [], 0
        for i, (s, e) in enumerate(keeps):
            seg = copy.deepcopy(base)
            dur = e - s  # keeps ถูก cap ที่กล้องสั้นสุดแล้ว — ทุก track ได้ target เท่ากัน ไม่ desync
            seg["source_timerange"] = {"start": s, "duration": dur}
            seg["target_timerange"] = {"start": pos, "duration": dur}
            pos += dur
            if i > 0:
                seg["id"] = new_id()
                refs = []
                for ref in seg["extra_material_refs"]:
                    kind, m = mat_index[ref]
                    clone = copy.deepcopy(m)
                    clone["id"] = new_id()
                    d["materials"][kind].append(clone)
                    refs.append(clone["id"])
                seg["extra_material_refs"] = refs
            segs.append(seg)
        track["segments"] = segs

    # CapCut 8.7+/9.x เก็บ timeline ซ้ำหลายไฟล์ — ต้องเขียนให้ตรงกันทุกสำเนา
    payload = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
    for rel in ("draft_info.json", "draft_info.json.bak", "template-2.tmp",
                f"Timelines/{tl_id}/draft_info.json", f"Timelines/{tl_id}/draft_info.json.bak",
                f"Timelines/{tl_id}/template.tmp", f"Timelines/{tl_id}/template-2.tmp"):
        p = os.path.join(dst, rel)
        if os.path.exists(p):
            open(p, "w", encoding="utf-8").write(payload)

    # 4) draft_meta_info.json: id ใหม่ + path ใหม่ + duration ใหม่
    meta_path = os.path.join(dst, "draft_meta_info.json")
    meta_txt = open(meta_path, encoding="utf-8").read()
    old_media = json.load(open(os.path.join(src, "draft_info.json")))["materials"]["videos"][0]["path"]
    meta = json.loads(meta_txt.replace(old_media, media))
    draft_id = new_id()
    meta.update({k: v for k, v in {
        "draft_id": draft_id, "draft_fold_path": dst,
        "draft_name": dst_name if "draft_name" in meta else None,
        "tm_duration": total if "tm_duration" in meta else None,
    }.items() if v is not None})
    open(meta_path, "w", encoding="utf-8").write(json.dumps(meta, ensure_ascii=False, separators=(",", ":")))

    # 5) cover จากเฟรมแรกที่มีเสียงพูด (ให้จำ draft ได้ในหน้า home)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{keeps[0][0]/1e6:.2f}", "-i", media,
                    "-frames:v", "1", "-vf", "scale=-2:480", os.path.join(dst, "draft_cover.jpg")], check=False)

    # 6) register ใน root_meta_info.json (atomic; CapCut rescan ตอนเปิดแอปอยู่แล้ว — นี่แค่ให้โผล่ไว)
    root_path = os.path.join(DRAFT_ROOT, "root_meta_info.json")
    root = json.load(open(root_path))
    store = [e for e in root["all_draft_store"] if e.get("draft_fold_path") != dst]
    tpl = next((e for e in store if e["draft_fold_path"] == src), store[0] if store else None)
    if tpl:
        now = int(time.time() * 1e6)
        entry = copy.deepcopy(tpl)
        entry.update({"draft_id": draft_id, "draft_fold_path": dst,
                      "draft_json_file": os.path.join(dst, "draft_info.json"),
                      "draft_cover": os.path.join(dst, "draft_cover.jpg"),
                      "draft_name": dst_name, "tm_draft_create": now,
                      "tm_draft_modified": now, "tm_duration": total})
        store.insert(0, entry)
        root["all_draft_store"] = store
        tmp_f = root_path + ".tmp"
        open(tmp_f, "w", encoding="utf-8").write(json.dumps(root, ensure_ascii=False, separators=(",", ":")))
        os.replace(tmp_f, root_path)

    # 7) self-check
    chk = json.load(open(os.path.join(dst, "draft_info.json")))
    for t in (t for t in chk["tracks"] if t["type"] == "video"):
        end = 0
        for sg in t["segments"]:
            assert sg["target_timerange"]["start"] == end, "timeline ไม่ต่อเนื่อง"
            end += sg["target_timerange"]["duration"]
            st = sg["source_timerange"]
            assert 0 <= st["start"] and st["start"] + st["duration"] <= mat_dur, "source เกินไฟล์"
        assert end == total == chk["duration"], "duration ไม่ตรง"
    orig_now = json.load(open(os.path.join(src, "draft_info.json")))
    assert all(len(t["segments"]) == 1 for t in orig_now["tracks"] if t["type"] == "video"), "ต้นฉบับเปลี่ยน?!"
    ntr = len(vtracks)
    print(f"OK ✅ draft '{dst_name}' พร้อมแล้ว ({ntr} track x {len(keeps)} segment, {total/1e6:.1f}s)")
    print("เปิด CapCut ใหม่ (ปิด-เปิดถ้ายังไม่เห็น) -> เปิด draft -> Export ได้เลย")

if __name__ == "__main__":
    main()
