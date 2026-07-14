#!/usr/bin/env python3
"""สร้าง CapCut draft ดิบจากโฟลเดอร์คลิป — จากศูนย์ ไม่ต้องเปิด CapCut ไม่ต้องมี draft เดิม

Usage: python3 new_draft.py <โฟลเดอร์ที่มี top.mp4 + Bottom02.mp4> --name "ชื่อ draft"

ใช้ template ของ pyCapCut (templates/draft_content_template.json, version 360000)
CapCut เปิดครั้งแรกจะ adopt + สร้างไฟล์ที่เหลือเอง (Timelines ฯลฯ)
ผลลัพธ์: draft ดิบ 2 กล้อง (แต่ละ track 1 segment เต็มเส้น) canvas 1080x1920
พร้อมป้อนต่อให้ t09-show.sh
"""
import argparse, json, os, subprocess, sys, time, uuid

DRAFT_ROOT = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")
TPL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

def new_id(): return str(uuid.uuid4()).upper()
def die(m): sys.exit(f"error: {m}")

def probe(path):
    pr = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream=width,height","-show_entries","format=duration",
        "-of","json", path], capture_output=True, text=True)
    j = json.loads(pr.stdout)
    return j["streams"][0]["width"], j["streams"][0]["height"], int(float(j["format"]["duration"])*1e6)

def video_material(path, mid, w, h, dur):
    return {"audio_fade": None, "category_id": "", "category_name": "local",
            "check_flag": 63487,
            "crop": {"lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0,
                     "lower_right_y": 1.0, "upper_left_x": 0.0, "upper_left_y": 0.0,
                     "upper_right_x": 1.0, "upper_right_y": 1.0},
            "crop_ratio": "free", "crop_scale": 1.0, "duration": dur,
            "height": h, "id": mid, "local_material_id": "", "material_id": mid,
            "material_name": os.path.basename(path), "media_path": "",
            "path": path, "type": "video", "width": w}

def video_segment(mid, dur, y, speed_id):
    return {"enable_adjust": True, "enable_color_correct_adjust": False,
            "enable_color_curves": True, "enable_color_match_adjust": False,
            "enable_color_wheels": True, "enable_lut": True,
            "enable_smart_color_adjust": False, "last_nonzero_volume": 1.0,
            "reverse": False, "track_attribute": 0, "track_render_index": 0,
            "visible": True, "common_keyframes": [], "keyframe_refs": [],
            "id": new_id(), "material_id": mid,
            "source_timerange": {"start": 0, "duration": dur},
            "target_timerange": {"start": 0, "duration": dur},
            "speed": 1.0, "volume": 1.0,
            "extra_material_refs": [speed_id],
            "clip": {"alpha": 1.0, "flip": {"horizontal": False, "vertical": False},
                     "rotation": 0.0, "scale": {"x": 1.0, "y": 1.0},
                     "transform": {"x": 0.0, "y": y}},
            "uniform_scale": {"on": True, "value": 1.0},
            "hdr_settings": {"intensity": 1.0, "mode": 1, "nits": 1000},
            "render_index": 0}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--name", required=True)
    ap.add_argument("--canvas", default="1080x1920")
    a = ap.parse_args()

    mp4s = [f for f in os.listdir(a.folder) if f.lower().endswith((".mp4", ".mov"))]
    face = next((f for f in mp4s if "bottom" in f.lower()), None)
    screen = next((f for f in mp4s if "top" in f.lower()), None)
    if not face or not screen:
        die(f"ต้องมีไฟล์ top*.mp4 + bottom*.mp4 ในโฟลเดอร์ (เจอ: {mp4s})")
    face, screen = os.path.join(a.folder, face), os.path.join(a.folder, screen)
    cw, ch = (int(x) for x in a.canvas.split("x"))

    d = json.load(open(os.path.join(TPL_DIR, "draft_content_template.json")))
    tl_id = new_id()
    d["id"] = tl_id
    d["fps"] = 30.0
    d["canvas_config"] = {"background": None, "height": ch, "ratio": "original", "width": cw}
    d["materials"].setdefault("videos", [])
    d["materials"].setdefault("speeds", [])
    d.setdefault("tracks", [])

    dst = os.path.join(DRAFT_ROOT, a.name)
    if os.path.exists(dst):
        import shutil as _sh; _sh.rmtree(dst)
    os.makedirs(dst)

    total = 0
    # ลำดับ track: จอ (ล่างสุดใน z) ก่อน แล้วหน้าคน — หน้าอยู่บนเสมอ
    # media ก๊อปเข้าโฟลเดอร์ draft เสมอ: ไฟล์ที่ไม่เคยผ่านหน้าต่าง import ของ
    # CapCut จะโดน sandbox บล็อก (เจอจริง 2026-07-10 — "top bottom ไม่มี")
    import shutil
    for src_path, y in ((screen, 0.5), (face, -0.5)):
        path = os.path.join(dst, os.path.basename(src_path))
        shutil.copy2(src_path, path)
        w, h, dur = probe(path)
        total = max(total, dur)
        mid = new_id()
        d["materials"]["videos"].append(video_material(path, mid, w, h, dur))
        sp = {"curve_speed": None, "id": new_id(), "mode": 0, "speed": 1.0, "type": "speed"}
        d["materials"]["speeds"].append(sp)
        d["tracks"].append({"attribute": 0, "flag": 0, "id": new_id(),
                            "is_default_name": True, "name": "",
                            "segments": [video_segment(mid, dur, y, sp["id"])],
                            "type": "video"})
    d["duration"] = total

    payload = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
    for fn in ("draft_info.json", "draft_info.json.bak", "template-2.tmp"):
        open(os.path.join(dst, fn), "w", encoding="utf-8").write(payload)

    meta = json.load(open(os.path.join(TPL_DIR, "draft_meta_info.json")))
    draft_id = new_id()
    meta.update({"draft_id": draft_id, "draft_fold_path": dst,
                 "draft_name": a.name, "tm_duration": total,
                 "draft_root_path": DRAFT_ROOT,
                 "tm_draft_create": int(time.time()*1e6),
                 "tm_draft_modified": int(time.time()*1e6)})
    open(os.path.join(dst, "draft_meta_info.json"), "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, separators=(",", ":")))
    subprocess.run(["ffmpeg","-y","-v","error","-ss","1","-i",face,"-frames:v","1",
                    "-vf","scale=-2:480", os.path.join(dst,"draft_cover.jpg")], check=False)

    # register (รองรับ store ว่างเปล่า — สร้าง entry เต็มรูปแบบเอง)
    rp = os.path.join(DRAFT_ROOT, "root_meta_info.json")
    root = json.load(open(rp)) if os.path.isfile(rp) else \
        {"all_draft_store": [], "draft_ids": 0, "root_path": DRAFT_ROOT}
    now = int(time.time()*1e6)
    entry = {"cloud_draft_cover": False, "cloud_draft_sync": False,
             "draft_cloud_last_action_download": False, "draft_cloud_purchase_info": "",
             "draft_cloud_template_id": "", "draft_cloud_tutorial_info": "",
             "draft_cloud_videocut_purchase_info": "",
             "draft_cover": os.path.join(dst, "draft_cover.jpg"),
             "draft_fold_path": dst, "draft_id": draft_id,
             "draft_is_ai_shorts": False, "draft_is_cloud_temp_draft": False,
             "draft_is_invisible": False, "draft_is_pippit_draft": False,
             "draft_is_web_article_video": False,
             "draft_json_file": os.path.join(dst, "draft_info.json"),
             "draft_name": a.name, "draft_new_version": "",
             "draft_root_path": DRAFT_ROOT, "draft_timeline_materials_size": 0,
             "draft_type": "", "draft_web_article_video_enter_from": "",
             "pippit_avatar_url": "", "pippit_extra_info": "", "pippit_id": "",
             "pippit_user_name": "", "streaming_edit_draft_ready": True,
             "tm_draft_cloud_completed": "", "tm_draft_cloud_entry_id": -1,
             "tm_draft_cloud_modified": 0, "tm_draft_cloud_parent_entry_id": -1,
             "tm_draft_cloud_space_id": -1, "tm_draft_cloud_user_id": -1,
             "tm_draft_create": now, "tm_draft_modified": now,
             "tm_draft_removed": 0, "tm_duration": total}
    root["all_draft_store"] = [e for e in root["all_draft_store"]
                               if e.get("draft_fold_path") != dst]
    root["all_draft_store"].insert(0, entry)
    tmp = rp + ".tmp"
    open(tmp, "w", encoding="utf-8").write(json.dumps(root, ensure_ascii=False, separators=(",", ":")))
    os.replace(tmp, rp)
    print(f"OK ✅ draft ดิบ '{a.name}' ({total/1e6:.1f}s, 2 กล้อง, canvas {cw}x{ch}) พร้อมป้อน t09-show.sh")

if __name__ == "__main__":
    main()
