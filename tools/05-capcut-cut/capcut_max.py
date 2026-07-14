#!/usr/bin/env python3
"""Tool 05 MAX demo — jump cuts + keyframe punch-in + Thai captions + hook/CTA
text (typewriter/slide-up animation) + shake/zoom effects + BGM ลง CapCut draft.

Schema ทุกก้อนตรงตาม pyCapCut (CapCut international, draft version 360000) —
ดูรายงานสกัด schema ใน scratchpad/pycapcut/. Experimental showcase 2026-07-07.

Usage: python3 capcut_max.py <src-draft> --edl edl.json --captions caps.json \
         --bgm file.mp3 --name "0707 AI max" [--hook "..."] [--cta "..."]
"""
import argparse, copy, json, os, shutil, subprocess, sys, time, uuid

DRAFT_ROOT = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")
GOLD, WHITE, BLACK = [1.0, 0.8431, 0.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]
FX_SLIGHT_ZOOM = ("轻微放大", "7399463624906984709")   # free
FX_SHAKE       = ("抖动", "7399465314104249605")       # free
FX_FLASH       = ("Flash", "7399470564022291717")      # VIP (ต้องมี Pro ตอน export)
ANIM_TYPEWRITER = ("打字机 I", "6724920249654710791")   # free intro
ANIM_SLIDEUP    = ("向上滑动", "6763470111253729803")    # free intro
ANIM_ZOOMIN     = ("放大", "6724919499042066958")       # free intro — pop-in แคปชั่น
TRANS_WHITE_FLASH = ("White Flash", "7345079500327096833", 400000, True)  # free transition
# คำเน้นไทย/เลข/แบรนด์ -> ทอง (สไตล์ BIZDRIVE)
import re
KEYWORD_RE = re.compile(r"ฟรี|ทั้งหมด|อัตโนมัติ|ง่าย|เร็ว|สะดวก|ทันที|ครบ|จบ|[0-9๐-๙,]+|[A-Za-z][A-Za-z0-9]*")

def new_id(): return str(uuid.uuid4()).upper()
def die(m): sys.exit(f"error: {m}")

# ---------- pyCapCut-verified shapes ----------
def _style(rng, color, size):
    return {"fill": {"alpha": 1.0, "content": {"render_type": "solid",
                     "solid": {"alpha": 1.0, "color": color}}},
            "range": list(rng), "size": size,
            "bold": True, "italic": False, "underline": False,
            "strokes": [{"content": {"solid": {"alpha": 1.0, "color": BLACK}}, "width": 0.08}],
            "shadows": [{"diffuse": 0.025, "alpha": 0.8, "distance": 5.0,
                         "content": {"solid": {"color": BLACK}}, "angle": -45.0}],
            # ไม่ใส่ font key = CapCut default font (แคตตาล็อก 348 ฟอนต์ไม่มีไทย)
            }

def text_material(text, mid, color, size, gold_spans=None):
    if gold_spans:
        styles, cur = [], 0
        for s, e in gold_spans:
            if s > cur: styles.append(_style((cur, s), color, size))
            styles.append(_style((s, e), GOLD, size))
            cur = e
        if cur < len(text): styles.append(_style((cur, len(text)), color, size))
    else:
        styles = [_style((0, len(text)), color, size)]
    inner = {"styles": styles, "text": text}
    return {"id": mid, "content": json.dumps(inner, ensure_ascii=False),
            "typesetting": 0, "alignment": 1, "letter_spacing": 0.0,
            "line_spacing": 0.02, "line_feed": 1, "line_max_width": 0.82,
            "force_apply_line_max_width": False, "check_flag": 47,  # border+shadow
            "type": "text", "global_alpha": 1.0}

def base_seg_fields():
    return {"enable_adjust": True, "enable_color_correct_adjust": False,
            "enable_color_curves": True, "enable_color_match_adjust": False,
            "enable_color_wheels": True, "enable_lut": True,
            "enable_smart_color_adjust": False, "last_nonzero_volume": 1.0,
            "reverse": False, "track_attribute": 0, "track_render_index": 0,
            "visible": True, "common_keyframes": [], "keyframe_refs": []}

def text_segment(mid, start, dur, y, anim_ref=None):
    seg = base_seg_fields()
    # pyCapCut ใส่ speed ref ค้างไว้โดยไม่ register ใน materials.speeds —
    # ฟอร์มนี้ผ่านการใช้งานจริงของ pyCapCut ทั้ง ecosystem จึงลอกตาม
    refs = [str(uuid.uuid4()).lower().replace("-", "")]
    if anim_ref: refs.append(anim_ref)
    seg.update({"id": new_id(), "material_id": mid,
                "target_timerange": {"start": start, "duration": dur},
                "source_timerange": None, "speed": 1.0, "volume": 1.0,
                "extra_material_refs": refs,
                "clip": {"alpha": 1.0, "flip": {"horizontal": False, "vertical": False},
                         "rotation": 0.0, "scale": {"x": 1.0, "y": 1.0},
                         "transform": {"x": 0.0, "y": y}},
                "uniform_scale": {"on": True, "value": 1.0}, "render_index": 15000})
    return seg

def anim_material(name, rid, dur, aid):
    return {"id": aid, "type": "sticker_animation", "multi_language_current": "none",
            "animations": [{"anim_adjust_params": None, "platform": "all", "panel": "",
                            "material_type": "sticker", "name": name, "id": rid,
                            "type": "in", "resource_id": rid, "start": 0, "duration": dur}]}

def audio_material(path, dur_us, mid):
    return {"app_id": 0, "category_id": "", "category_name": "local", "check_flag": 3,
            "copyright_limit_type": "none", "duration": dur_us, "effect_id": "",
            "formula_id": "", "id": mid, "local_material_id": mid, "music_id": mid,
            "name": os.path.basename(path), "path": path, "source_platform": 0,
            "type": "extract_music", "wave_points": []}

def audio_segment(mid, tgt_start, dur, volume, refs):
    seg = base_seg_fields()
    seg.update({"id": new_id(), "material_id": mid,
                "target_timerange": {"start": tgt_start, "duration": dur},
                "source_timerange": {"start": 0, "duration": dur},
                "speed": 1.0, "volume": volume, "last_nonzero_volume": volume,
                "extra_material_refs": refs, "clip": None, "hdr_settings": None,
                "render_index": 0})
    return seg

def effect_material(name, rid, mid, params):
    return {"adjust_params": [
                {"default_value": v, "max_value": 1.0, "min_value": 0.0,
                 "name": n, "parameterIndex": i, "portIndex": 0, "value": v}
                for i, (n, v) in enumerate(params)],
            "apply_target_type": 2, "apply_time_range": None, "category_id": "",
            "category_name": "", "common_keyframes": [], "disable_effect_faces": [],
            "effect_id": rid, "formula_id": "", "id": mid, "name": name,
            "platform": "all", "render_index": 11000, "resource_id": rid,
            "source_platform": 0, "time_range": None, "track_render_index": 0,
            "type": "video_effect", "value": 1.0, "version": ""}

def effect_segment(mid, start, dur):
    seg = base_seg_fields()
    seg.update({"id": new_id(), "material_id": mid,
                "target_timerange": {"start": start, "duration": dur},
                "render_index": 10000})
    return seg

def scale_keyframes(v0, v1, dur):
    def kf(t, v):
        return {"curveType": "Line", "graphID": "",
                "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
                "id": new_id(), "time_offset": t, "values": [v]}
    return [{"id": new_id(), "keyframe_list": [kf(0, v0), kf(dur, v1)],
             "material_id": "", "property_type": "KFTypeScaleX"}]

def make_track(ttype, segments, name):
    return {"attribute": 0, "flag": 0, "id": new_id(), "is_default_name": False,
            "name": name, "segments": segments, "type": ttype}

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--edl", required=True)
    ap.add_argument("--captions", required=True)
    ap.add_argument("--bgm")
    ap.add_argument("--bgm-volume", type=float, default=0.06)  # ~5% ตาม BGM_LIBRARY
    ap.add_argument("--punch", type=float, default=1.06, help="ปลายทางซูม keyframe/segment")
    ap.add_argument("--cap-size", type=float, default=19.5,
                    help="ขนาดฟอนต์แคปชั่น (19.5 = ค่าที่พี่แบงค์คาลิเบรตกับตา 2026-07-07; 13≈64px เดิมเล็กไป)")
    ap.add_argument("--layout", choices=["keep", "t09"], default="keep",
                    help="t09 = กล้อง cover เต็มครึ่งจอบน/ล่างแบบ Template 09")
    ap.add_argument("--face-center", type=float, default=0.5,
                    help="ตำแหน่งหน้าตามแนวนอนใน source (0-1) — เลื่อนครอปให้หน้าอยู่กลางจอ")
    ap.add_argument("--sfx-dir", help="โฟลเดอร์ SFX (riser.wav/whoosh-fast.mp3/ding.mp3)")
    ap.add_argument("--broll", action="append", default=[],
                    help='insert เต็มจอ: "path@start_s[:dur_s]" ใส่ซ้ำได้หลายตัว')
    ap.add_argument("--cut-transition", choices=["none", "white-flash"], default="white-flash",
                    help="transition ตรงรอยตัด dead air จริง (แทน shake)")
    ap.add_argument("--endcard", type=float, default=0.0,
                    help="วินาที end-card ปิดคลิป (bg เต็มจอ + CTA ทองใหญ่)")
    ap.add_argument("--bg", help="ภาพพื้นหลังชั้นล่างสุด (เช่น bg.png ของ T09)")
    ap.add_argument("--hook", default="")
    ap.add_argument("--cta", default="")
    ap.add_argument("--name", required=True)
    a = ap.parse_args()

    src = os.path.join(DRAFT_ROOT, a.draft)
    dst = os.path.join(DRAFT_ROOT, a.name)
    d = json.load(open(os.path.join(src, "draft_info.json")))
    vtracks = [t for t in d["tracks"] if t["type"] == "video"]
    if not vtracks or any(len(t["segments"]) != 1 for t in vtracks):
        die("ต้องเป็น draft ดิบ (video track ละ 1 segment)")
    vids = {v["id"]: v for v in d["materials"]["videos"]}
    for v in vids.values():
        if not os.path.isfile(v["path"]): die(f"ไฟล์หาย: {v['path']}")

    keeps = [(s["start_ms"]*1000, s["end_ms"]*1000)
             for s in json.load(open(a.edl))["segments"]]
    total = sum(e-s for s, e in keeps)
    caps = json.load(open(a.captions))

    # ---- copy + regenerate internal ids
    # rebuild ทับชื่อเดิม: คง draft_id เดิมไว้ ไม่งั้น CapCut มองเป็นคนละตัวแล้ว rename "(1)"
    reuse_id = None
    old_meta_p = os.path.join(dst, "draft_meta_info.json")
    if os.path.isfile(old_meta_p):
        try: reuse_id = json.load(open(old_meta_p)).get("draft_id")
        except Exception: pass
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    old_tl = d["id"]
    for junk in (".locked", os.path.join("Timelines", old_tl, "draft.extra")):
        p = os.path.join(dst, junk)
        if os.path.exists(p): os.remove(p)
    tl_id = new_id()
    id_map = {old_tl: tl_id}
    pj = os.path.join(dst, "Timelines", "project.json")
    if os.path.exists(pj):
        pd = json.load(open(pj))
        if pd.get("id"): id_map[pd["id"]] = new_id()
    for bd, _, fs in os.walk(dst):
        for fn in fs:
            p = os.path.join(bd, fn)
            try: txt = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError): continue
            if any(k in txt for k in id_map):
                for k, v in id_map.items(): txt = txt.replace(k, v)
                open(p, "w", encoding="utf-8").write(txt)
    otd = os.path.join(dst, "Timelines", old_tl)
    if os.path.isdir(otd): os.rename(otd, os.path.join(dst, "Timelines", tl_id))
    d["id"] = tl_id

    # media กล้องต้องอยู่ในอาณาเขต CapCut (~/Movies/CapCut) ไม่งั้นโดน sandbox
    # บล็อกถ้าไฟล์ไม่เคยผ่านหน้าต่าง import — ก๊อปเข้า draft folder แล้วชี้ใหม่
    for v in vids.values():
        if not v["path"].startswith(dst + os.sep):
            local = os.path.join(dst, os.path.basename(v["path"]))
            if not os.path.exists(local):
                shutil.copy2(v["path"], local)
            v["path"] = local

    # ---- video tracks: jump cuts + keyframe punch-in (Ken Burns สลับทิศ เฉพาะกล้องหน้า)
    mat_index = {}
    for kind, lst in d["materials"].items():
        if isinstance(lst, list):
            for m in lst:
                if isinstance(m, dict) and "id" in m:
                    mat_index[m["id"]] = (kind, m)
    d["materials"].setdefault("transitions", [])
    real_cut_after = {i for i in range(len(keeps) - 1) if keeps[i+1][0] - keeps[i][1] > 50000}
    for track in vtracks:
        base = track["segments"][0]
        mat = vids[base["material_id"]]
        is_face = "bottom" in os.path.basename(mat["path"]).lower()
        if a.layout == "t09":
            # cover เต็มครึ่งจอ: scale = cover(กว้างเต็ม, สูงครึ่ง) / fit(ทั้งจอ)
            cw, ch = d["canvas_config"]["width"], d["canvas_config"]["height"]
            fit = min(cw / mat["width"], ch / mat["height"])
            cover_half = max(cw / mat["width"], (ch / 2) / mat["height"])
            base["clip"]["scale"] = {"x": cover_half / fit, "y": cover_half / fit}
            fx = 0.0
            if is_face and a.face_center != 0.5:
                disp_w = mat["width"] * cover_half           # px บน canvas
                fx = -(a.face_center - 0.5) * disp_w / (cw / 2)
            base["clip"]["transform"] = {"x": fx, "y": -0.5 if is_face else 0.5}
        bs = base["clip"]["scale"]["x"]
        segs, pos = [], 0
        for i, (s, e) in enumerate(keeps):
            seg = copy.deepcopy(base)
            dur = e - s
            seg["source_timerange"] = {"start": s, "duration": dur}
            seg["target_timerange"] = {"start": pos, "duration": dur}
            pos += dur
            if is_face and a.punch > 1.0:
                hi = bs * a.punch
                v0, v1 = (bs, hi) if i % 2 == 0 else (hi, bs)  # ซูมเข้า/ออกสลับกัน
                seg["common_keyframes"] = scale_keyframes(v0, v1, dur)
            if i > 0:
                seg["id"] = new_id()
                refs = []
                for ref in seg["extra_material_refs"]:
                    kind, m = mat_index[ref]
                    c = copy.deepcopy(m); c["id"] = new_id()
                    d["materials"][kind].append(c); refs.append(c["id"])
                seg["extra_material_refs"] = refs
            if a.cut_transition == "white-flash" and i in real_cut_after:
                name, rid, tdur, overlap = TRANS_WHITE_FLASH
                tr = {"category_id": "", "category_name": "", "duration": tdur,
                      "effect_id": rid, "id": new_id(), "is_overlap": overlap,
                      "name": name, "platform": "all", "resource_id": rid,
                      "type": "transition"}
                d["materials"]["transitions"].append(tr)
                seg["extra_material_refs"] = list(seg["extra_material_refs"]) + [tr["id"]]
            segs.append(seg)
        track["segments"] = segs
    d["duration"] = total

    # ---- BG ชั้นล่างสุด (bg.png สไตล์ T09) — ก๊อปเข้า draft folder กัน sandbox
    if a.bg:
        if not os.path.isfile(a.bg): die(f"ไม่พบ BG: {a.bg}")
        bg_local = os.path.join(dst, "bg" + os.path.splitext(a.bg)[1])
        # scale ให้เท่า canvas เสมอ (bg ของเทมเพลตเก่าเป็น 941x1672 — CapCut แม็พพิกเซลตรง)
        bw = d["canvas_config"]["width"]; bh = d["canvas_config"]["height"]
        subprocess.run(["ffmpeg","-y","-v","error","-i", a.bg,
                        "-vf", f"scale={bw}:{bh}:flags=lanczos", bg_local], check=True)
        bmid = new_id()
        d["materials"]["videos"] = list(d["materials"]["videos"])
        d["materials"]["videos"].append({
            "audio_fade": None, "category_id": "", "category_name": "local",
            "check_flag": 63487,
            "crop": {"lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0,
                     "lower_right_y": 1.0, "upper_left_x": 0.0, "upper_left_y": 0.0,
                     "upper_right_x": 1.0, "upper_right_y": 1.0},
            "crop_ratio": "free", "crop_scale": 1.0, "duration": 10800000000,
            "height": bh, "id": bmid, "local_material_id": "", "material_id": bmid,
            "material_name": os.path.basename(bg_local), "media_path": "",
            "path": bg_local, "type": "photo", "width": bw})
        sp = {"curve_speed": None, "id": new_id(), "mode": 0, "speed": 1.0, "type": "speed"}
        d["materials"]["speeds"].append(sp)
        bseg = base_seg_fields()
        bseg.update({"id": new_id(), "material_id": bmid,
                     "target_timerange": {"start": 0, "duration": total},
                     "source_timerange": {"start": 0, "duration": total},
                     "speed": 1.0, "volume": 1.0,
                     "extra_material_refs": [sp["id"]],
                     "clip": {"alpha": 1.0, "flip": {"horizontal": False, "vertical": False},
                              "rotation": 0.0, "scale": {"x": 1.0, "y": 1.0},
                              "transform": {"x": 0.0, "y": 0.0}},
                     "uniform_scale": {"on": True, "value": 1.0},
                     "hdr_settings": {"intensity": 1.0, "mode": 1, "nits": 1000},
                     "render_index": 0})
        d["tracks"].insert(0, make_track("video", [bseg], "bg"))  # track แรก = ชั้นล่างสุด
        bg_material_id = bmid
    else:
        bg_material_id = None

    # ---- B-roll inserts: overlay เต็มจอทับกล้อง (track วิดีโอบนสุด) แคปชั่นยังลอยเหนือ
    if a.broll:
        bsegs = []
        for spec in a.broll:
            path, _, at = spec.partition("@")
            at_s, _, dur_s = at.partition(":")
            if not os.path.isfile(path): die(f"ไม่พบ B-roll: {path}")
            local = os.path.join(dst, "broll-" + os.path.basename(path))
            shutil.copy2(path, local)
            pr = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
                "-show_entries","stream=width,height","-show_entries","format=duration",
                "-of","json", local], capture_output=True, text=True)
            info = json.loads(pr.stdout)
            w, h = info["streams"][0]["width"], info["streams"][0]["height"]
            fdur = int(float(info["format"]["duration"]) * 1e6)
            start = int(float(at_s) * 1e6)
            dur = min(int(float(dur_s) * 1e6) if dur_s else fdur, fdur, total - start)
            if dur <= 0: continue
            bmid = new_id()
            d["materials"]["videos"].append({
                "audio_fade": None, "category_id": "", "category_name": "local",
                "check_flag": 63487,
                "crop": {"lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0,
                         "lower_right_y": 1.0, "upper_left_x": 0.0, "upper_left_y": 0.0,
                         "upper_right_x": 1.0, "upper_right_y": 1.0},
                "crop_ratio": "free", "crop_scale": 1.0, "duration": fdur,
                "height": h, "id": bmid, "local_material_id": "", "material_id": bmid,
                "material_name": os.path.basename(local), "media_path": "",
                "path": local, "type": "video", "width": w})
            cw, ch = d["canvas_config"]["width"], d["canvas_config"]["height"]
            fitf = min(cw / w, ch / h)
            if a.layout == "t09":   # แทนที่เฉพาะจอบน — หน้าคนครึ่งล่างอยู่ตลอด
                coverf = max(cw / w, (ch / 2) / h); by = 0.5
            else:                   # เต็มจอ
                coverf = max(cw / w, ch / h); by = 0.0
            sp = {"curve_speed": None, "id": new_id(), "mode": 0, "speed": 1.0, "type": "speed"}
            d["materials"]["speeds"].append(sp)
            seg = base_seg_fields()
            seg.update({"id": new_id(), "material_id": bmid,
                        "target_timerange": {"start": start, "duration": dur},
                        "source_timerange": {"start": 0, "duration": dur},
                        "speed": 1.0, "volume": 0.0, "last_nonzero_volume": 1.0,
                        "extra_material_refs": [sp["id"]],
                        "clip": {"alpha": 1.0, "flip": {"horizontal": False, "vertical": False},
                                 "rotation": 0.0,
                                 "scale": {"x": coverf / fitf, "y": coverf / fitf},
                                 "transform": {"x": 0.0, "y": by}},
                        "uniform_scale": {"on": True, "value": 1.0},
                        "hdr_settings": {"intensity": 1.0, "mode": 1, "nits": 1000},
                        "render_index": 0})
            bsegs.append(seg)
        if bsegs:
            bsegs.sort(key=lambda s: s["target_timerange"]["start"])
            d["tracks"].append(make_track("video", bsegs, "broll"))
            broll_starts = [s["target_timerange"]["start"] for s in bsegs]
        else:
            broll_starts = []
    else:
        broll_starts = []

    # ---- end-card ปิดคลิป: bg เต็มจอทับกล้อง + ซูมช้า (CTA จะย้ายมากลางจอ)
    endcard_start = None
    if a.endcard > 0 and bg_material_id:
        es = min(int(a.endcard * 1e6), total)
        endcard_start = total - es
        sp = {"curve_speed": None, "id": new_id(), "mode": 0, "speed": 1.0, "type": "speed"}
        d["materials"]["speeds"].append(sp)
        eseg = base_seg_fields()
        eseg.update({"id": new_id(), "material_id": bg_material_id,
                     "target_timerange": {"start": endcard_start, "duration": es},
                     "source_timerange": {"start": 0, "duration": es},
                     "speed": 1.0, "volume": 1.0,
                     "extra_material_refs": [sp["id"]],
                     "clip": {"alpha": 1.0, "flip": {"horizontal": False, "vertical": False},
                              "rotation": 0.0, "scale": {"x": 1.0, "y": 1.0},
                              "transform": {"x": 0.0, "y": 0.0}},
                     "uniform_scale": {"on": True, "value": 1.0},
                     "hdr_settings": {"intensity": 1.0, "mode": 1, "nits": 1000},
                     "render_index": 0})
        eseg["common_keyframes"] = scale_keyframes(1.0, 1.06, es)  # ซูมช้าให้มีชีวิต
        d["tracks"].append(make_track("video", [eseg], "endcard"))

    # ---- captions: pop-in ทุกชิ้น + คำเน้น (ไทย/เลข/แบรนด์) เป็นทอง + เงา
    d["materials"].setdefault("texts", [])
    d["materials"].setdefault("material_animations", [])
    tsegs = []
    for c in caps:
        start = c["start_ms"]*1000
        if start >= total: continue
        dur = min(c["end_ms"]*1000, total) - start
        spans = [(m.start(), m.end()) for m in KEYWORD_RE.finditer(c["text"])]
        full_kw = len(spans) == 1 and spans[0] == (0, len(c["text"]))
        size = a.cap_size + (1.5 if full_kw else 0)   # คำเน้นล้วน = ใหญ่ขึ้นนิด
        mid = new_id()
        d["materials"]["texts"].append(text_material(
            c["text"], mid, WHITE, size, gold_spans=None if full_kw else spans or None))
        if full_kw:
            d["materials"]["texts"][-1] = text_material(c["text"], mid, GOLD, size)
        aid = new_id()
        d["materials"]["material_animations"].append(
            anim_material(*ANIM_ZOOMIN, min(150000, dur // 2), aid))
        tsegs.append(text_segment(mid, start, dur, y=0.0, anim_ref=aid))
    d["tracks"].append(make_track("text", tsegs, "captions"))

    # ---- hook + CTA (text อีก track มี intro animation)
    extra_tsegs = []
    if a.hook:
        aid, mid = new_id(), new_id()
        d["materials"]["material_animations"].append(
            anim_material(*ANIM_TYPEWRITER, 600000, aid))
        d["materials"]["texts"].append(text_material(a.hook, mid, GOLD, a.cap_size + 2))
        extra_tsegs.append(text_segment(mid, 0, min(3200000, total), y=0.62, anim_ref=aid))
    if a.cta:
        aid, mid = new_id(), new_id()
        d["materials"]["material_animations"].append(
            anim_material(*ANIM_SLIDEUP, 500000, aid))
        if endcard_start is not None:   # บน end-card: CTA ทองใหญ่กลางจอ
            d["materials"]["texts"].append(text_material(a.cta, mid, GOLD, a.cap_size + 5))
            extra_tsegs.append(text_segment(mid, endcard_start, total - endcard_start,
                                            y=0.45, anim_ref=aid))
        else:
            d["materials"]["texts"].append(text_material(a.cta, mid, WHITE, a.cap_size + 1))
            st = max(0, total - 3000000)
            extra_tsegs.append(text_segment(mid, st, total - st, y=-0.62, anim_ref=aid))
    if extra_tsegs:
        d["tracks"].append(make_track("text", extra_tsegs, "titles"))

    # ---- effects: zoom-in ช่วง hook + shake ตรงรอยตัด dead air + Flash เปิดคลิป
    d["materials"].setdefault("video_effects", [])
    esegs = []
    cut_points = []  # target µs ของรอยตัด dead air จริง (ใช้ร่วมกับ SFX)
    mzoom = new_id()
    d["materials"]["video_effects"].append(effect_material(
        *FX_SLIGHT_ZOOM, mzoom, [("effects_adjust_speed", 0.33), ("effects_adjust_range", 0.5)]))
    esegs.append(effect_segment(mzoom, 0, min(2500000, total)))
    pos = 0
    for i, (s, e) in enumerate(keeps):
        if i > 0 and s - keeps[i-1][1] > 50000:  # dead air จริง (>50ms) ถูกตัดตรงนี้
            cut_points.append(pos)
            mfx = new_id()
            d["materials"]["video_effects"].append(effect_material(
                *FX_SHAKE, mfx, [("effects_adjust_speed", 0.33),
                ("effects_adjust_horizontal_chromatic", 0.75),
                ("effects_adjust_vertical_chromatic", 0.75)]))
            esegs.append(effect_segment(mfx, pos, min(500000, total - pos)))
        pos += e - s
    if a.cut_transition != "none":   # transition แทน shake แล้ว — เก็บ shake ไว้เฉพาะโหมด none
        esegs = [esegs[0]]
    d["tracks"].append(make_track("effect", esegs, "fx"))
    mflash = new_id()  # VIP — Pro export ได้; แยก track กันซ้อนกับ zoom
    d["materials"]["video_effects"].append(effect_material(
        *FX_FLASH, mflash, [("effects_adjust_speed", 0.33), ("effects_adjust_color", 0.65),
        ("effects_adjust_intensity", 0.5), ("effects_adjust_luminance", 0.5),
        ("effects_adjust_blur", 0.5)]))
    d["tracks"].append(make_track("effect", [effect_segment(mflash, 0, min(600000, total))], "fx2"))

    # ---- SFX: riser เปิดคลิป + whoosh ตรงรอยตัด + ding ตอน CTA (ก๊อปไฟล์เข้า draft)
    if a.sfx_dir and os.path.isdir(a.sfx_dir):
        d["materials"].setdefault("audios", [])
        d["materials"].setdefault("speeds", [])
        def sfx_events():
            yield "riser.wav", 0, 0.35
            for cp in cut_points:
                yield "whoosh-fast.mp3", max(0, cp - 120000), 0.4
            for bs_ in broll_starts:
                yield "whoosh-soft.mp3", max(0, bs_ - 100000), 0.35
            if a.cta:
                yield "ding.mp3", max(0, endcard_start if endcard_start is not None
                                      else total - 3000000), 0.45
        sfx_mats = {}
        ssegs = []
        for fname, at, vol in sfx_events():
            srcp = os.path.join(a.sfx_dir, fname)
            if not os.path.isfile(srcp): continue
            if fname not in sfx_mats:
                local = os.path.join(dst, "sfx-" + fname)
                shutil.copy2(srcp, local)
                pr = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                                     "-of","csv=p=0", local], capture_output=True, text=True)
                mid = new_id()
                d["materials"]["audios"].append(audio_material(local, int(float(pr.stdout)*1e6), mid))
                sfx_mats[fname] = (mid, int(float(pr.stdout)*1e6))
            mid, fdur = sfx_mats[fname]
            dur = min(fdur, 1200000, total - at)
            if dur <= 0: continue
            sp = {"curve_speed": None, "id": new_id(), "mode": 0, "speed": 1.0, "type": "speed"}
            d["materials"]["speeds"].append(sp)
            ssegs.append(audio_segment(mid, at, dur, vol, [sp["id"]]))
        if ssegs:
            ssegs.sort(key=lambda s: s["target_timerange"]["start"])
            for i in range(len(ssegs) - 1):  # ห้ามซ้อนใน track เดียว — clamp ให้จบก่อนตัวถัดไป
                cur, nxt = ssegs[i]["target_timerange"], ssegs[i+1]["target_timerange"]
                if cur["start"] + cur["duration"] > nxt["start"]:
                    cur["duration"] = nxt["start"] - cur["start"]
                    ssegs[i]["source_timerange"]["duration"] = cur["duration"]
            ssegs = [s for s in ssegs if s["target_timerange"]["duration"] > 0]
            d["tracks"].append(make_track("audio", ssegs, "sfx"))

    # ---- BGM (loop จนจบ + fade out)
    if a.bgm:
        if not os.path.isfile(a.bgm): die(f"ไม่พบ BGM: {a.bgm}")
        # CapCut เป็นแอป sandbox — อ่านไฟล์นอก ~/Movies/CapCut ไม่ได้ ("File not
        # accessible" เจอจริง 2026-07-07) จึงก๊อป BGM เข้า draft folder เสมอ
        bgm_local = os.path.join(dst, "bgm-" + os.path.basename(a.bgm))
        shutil.copy2(a.bgm, bgm_local)
        a.bgm = bgm_local
        probe = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                                "-of","csv=p=0", a.bgm], capture_output=True, text=True)
        bgm_dur = int(float(probe.stdout.strip())*1e6)
        d["materials"].setdefault("audios", [])
        d["materials"].setdefault("speeds", [])
        d["materials"].setdefault("audio_fades", [])
        amid = new_id()
        d["materials"]["audios"].append(audio_material(a.bgm, bgm_dur, amid))
        asegs, pos = [], 0
        while pos < total:
            dur = min(bgm_dur, total - pos)
            sp = {"curve_speed": None, "id": new_id(), "mode": 0, "speed": 1.0, "type": "speed"}
            d["materials"]["speeds"].append(sp)
            refs = [sp["id"]]
            if pos + dur >= total:  # ท่อนสุดท้าย fade out 2s
                fd = {"id": new_id(), "fade_in_duration": 800000,
                      "fade_out_duration": 2000000, "fade_type": 0, "type": "audio_fade"}
                d["materials"]["audio_fades"].append(fd); refs.append(fd["id"])
            asegs.append(audio_segment(amid, pos, dur, a.bgm_volume, refs))
            pos += dur
        d["tracks"].append(make_track("audio", asegs, "bgm"))

    # ---- write ทุกสำเนา timeline + meta + registry
    payload = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
    for rel in ("draft_info.json", "draft_info.json.bak", "template-2.tmp",
                f"Timelines/{tl_id}/draft_info.json", f"Timelines/{tl_id}/draft_info.json.bak",
                f"Timelines/{tl_id}/template.tmp", f"Timelines/{tl_id}/template-2.tmp"):
        p = os.path.join(dst, rel)
        if os.path.exists(p): open(p, "w", encoding="utf-8").write(payload)
    meta = json.load(open(os.path.join(dst, "draft_meta_info.json")))
    draft_id = reuse_id or new_id()
    meta.update({"draft_id": draft_id, "draft_fold_path": dst})
    if "draft_name" in meta: meta["draft_name"] = a.name
    if "tm_duration" in meta: meta["tm_duration"] = total
    open(os.path.join(dst, "draft_meta_info.json"), "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, separators=(",", ":")))
    face = next(v for v in vids.values() if "bottom" in os.path.basename(v["path"]).lower())
    subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{keeps[0][0]/1e6:.2f}","-i",face["path"],
                    "-frames:v","1","-vf","scale=-2:480", os.path.join(dst,"draft_cover.jpg")], check=False)
    rp = os.path.join(DRAFT_ROOT, "root_meta_info.json")
    root = json.load(open(rp))
    store = [e for e in root["all_draft_store"] if e.get("draft_fold_path") != dst]
    tpl = next((e for e in store if e["draft_fold_path"] == src), store[0])
    now = int(time.time()*1e6)
    ent = copy.deepcopy(tpl)
    ent.update({"draft_id": draft_id, "draft_fold_path": dst,
                "draft_json_file": os.path.join(dst, "draft_info.json"),
                "draft_cover": os.path.join(dst, "draft_cover.jpg"),
                "draft_name": a.name, "tm_draft_create": now,
                "tm_draft_modified": now, "tm_duration": total})
    store.insert(0, ent)
    root["all_draft_store"] = store
    tmp = rp + ".tmp"
    open(tmp, "w", encoding="utf-8").write(json.dumps(root, ensure_ascii=False, separators=(",", ":")))
    os.replace(tmp, rp)

    print(f"OK ✅ '{a.name}': {len(vtracks)} cams × {len(keeps)} jump cuts (keyframe punch-in), "
          f"{len(tsegs)} captions + {len(extra_tsegs)} titles, {len(esegs)} effects, "
          f"BGM={'yes' if a.bgm else 'no'}, {total/1e6:.1f}s")

if __name__ == "__main__":
    main()
