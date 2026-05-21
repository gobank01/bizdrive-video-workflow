#!/usr/bin/env python3
"""Post-process pass (V88 Step 10) for the claude-package job.
Splits coarse ElevenLabs phrase chunks into karaoke caption groups,
interpolating timing by character weight. Emits caption-groups.json.
"""
import json, datetime

DURATION = 98.861333
G = True   # gold
W = False  # white/normal

# (entry_start, entry_end, [ [ (text, gold), ... ], ... ])
PLAN = [
    (0.28, 2.32, [[("เดี๋ยวคลิปนี้",W),("อธิบาย",W)], [("เรื่องของ",W),("แพ็คเกจ",W)]]),
    (2.36, 2.88, [[("Claude Code",G)]]),
    (2.90, 4.40, [[("ให้ฟัง",W),("นะครับ",W)]]),
    (4.48, 7.14, [[("มันคือ",W),("แพ็คเกจ",W),("เดียวกัน",W)], [("ไม่ว่าใคร",W),("จะใช้",W)]]),
    (7.56, 7.82, [[("Claude",G)]]),
    (8.12, 8.86, [[("Claude Cowork",G)]]),
    (8.88, 9.72, [[("หรือ",W),("Claude Code",G)]]),
    (9.84, 12.28, [[("แต่ที่",W),("ติดลิมิต",W)], [("มันคือ",W)]]),
    (12.32, 12.88, [[("Claude Code",G)]]),
    (13.16, 15.20, [[("นะครับ",W),("เอาไป",W)], [("เขียนโปรแกรม",W)]]),
    (15.22, 17.34, [[("แล้วของ",W),("พี่แบงค์",W)], [("อัปเกรด",W),("มาเรื่อยๆ",W)]]),
    (17.34, 18.78, [[("แล้วก็เริ่ม",W),("ติดลิมิต",W)]]),
    (18.82, 22.08, [[("ติดลิมิต",W),("เป็นยังไง",W)], [("นะครับ",W),("ทุกคน",W)]]),
    (22.12, 25.18, [[("เวลาเรา",W),("พัฒนา",W),("โปรแกรม",W)], [("จะมีตัว",W)]]),
    (25.32, 26.58, [[("Usage",G),("อยู่นะครับ",W)]]),
    (26.98, 30.96, [[("มันจะลิมิต",W),("5 ชั่วโมง",G)], [("แล้วก็",W),("เป็นอาทิตย์",G)]]),
    (31.02, 36.56, [[("คือมันมี",W),("2 จุด",G)], [("นะครับ",W),("5 ชั่วโมง",G)], [("แล้วก็",W),("เป็นอาทิตย์",G)]]),
    (36.60, 40.74, [[("โดยมาก",W),("มันจะ",W),("ติดลิมิต",W)], [("ตรง",W),("5 ชั่วโมง",G)]]),
    (40.76, 44.76, [[("ของพี่แบงค์",W),("เต็มแล้ว",W)], [("100%",G),("เต็มเป๊ะเลย",W)]]),
    (44.80, 46.68, [[("Reset",G),("ในอีก",W),("51 นาที",G)]]),
    (46.70, 50.62, [[("แต่ของ",W),("พี่แบงค์",W)], [("เป็นตัวกลาง",W),("นะครับ",W)]]),
    (50.68, 58.26, [[("มันก็จะมี",W)], [("ตัว",W),("$20",G)], [("แล้วก็",W),("$100",G)], [("แล้วก็",W),("$200",G)]]),
    (58.28, 66.22, [[("เอาเป็นว่า",W),("ถ้าใครทำ",W)], [("แล้วมันเต็ม",W),("นะครับ",W)], [("รู้สึกว่า",W),("จ่ายไหว",W)], [("ก็จ่ายเพิ่ม",W)]]),
    (66.28, 68.94, [[("จะบอกว่า",W),("$100",G)], [("ก็ทำได้",W),("เยอะแล้ว",W)]]),
    (68.96, 72.10, [[("แต่ถ้าเป็น",W),("$200",G)], [("จะตกประมาณ",W),("7,000+ บาท",G)]]),
    (72.16, 76.86, [[("อันนี้",W),("แทบจะ",W),("อมตะ",G)], [("ทำอะไรได้",W),("เยอะมากๆ",W)]]),
    (76.90, 79.04, [[("แต่ของพี่แบงค์",W),("เต็มแล้ว",W)]]),
    (79.12, 83.28, [[("งั้นขอ",W),("อัปเกรด",W)], [("แล้วไป",W),("ลุยกันต่อ",W)]]),
    (83.34, 84.88, [[("กดอัปเกรด",W),("กันไปเลย",W)]]),
    (84.94, 89.78, [[("นะครับ",W),("เพื่อที่จะ",W)], [("พัฒนากัน",W),("ให้สุดเลย",W)]]),
    (89.82, 93.00, [[("นักเรียน",W),("ก็มาเริ่มต้น",W)], [("ที่",W),("$20",G),("ก่อนได้",W)]]),
    (93.02, 94.90, [[("เดี๋ยวเรา",W),("เจอกัน",W),("ในคลาส",W)]]),
    (94.98, 97.00, [[("จ่ายตังแล้ว",W),("สบายใจ",G)]]),
    (97.08, DURATION, [[("Welcome to Max",G),("ครับ",W)]]),
]

groups = []
for estart, eend, gdefs in PLAN:
    span = eend - estart
    weights = [sum(max(len(t), 1) for t, _ in g) for g in gdefs]
    total = sum(weights)
    cursor = estart
    for gi, gdef in enumerate(gdefs):
        gw = weights[gi]
        gend = eend if gi == len(gdefs) - 1 else cursor + span * (gw / total)
        groups.append({
            "start": round(cursor, 3),
            "end": round(gend, 3),
            "tokens": [{"text": t, "gold": bool(gold)} for t, gold in gdef],
        })
        cursor = gend

out = {
    "duration": DURATION,
    "language": "th",
    "source_provider": "elevenlabs",
    "post_processed_at": datetime.datetime.now().isoformat(timespec="seconds"),
    "groups": groups,
    "notes": [
        "Brand fix: STT 'Quad/QuadCode/QuadCowork' -> 'Claude / Claude Code / Claude Cowork' everywhere (Thai STT mishears 'Claude' as 'Quad'); kept Latin for the Thai+tech audience.",
        "Number fixes: 'ห้าชั่วโมง'->'5 ชั่วโมง', 'ร้อยเปอร์เซ็นต์'->'100%', 'ห้าสิบเอ็ดนาที'->'51 นาที', 'สองจุด'->'2 จุด', 'ยี่สิบดอล'->'$20', 'หนึ่งร้อยดอล'->'$100', 'สองร้อยดอล'->'$200', 'เจ็ดพันกว่าบาท'->'7,000+ บาท'.",
        "Kept Latin tech terms 'Usage' and 'Reset' as spoken (on-screen UI labels in the screen recording).",
        "Outro tag: STT 'welcome to Mac' -> 'Welcome to Max' (correct wording per pi — pun on the Claude Max plan); last group end capped to duration 98.861.",
        "Dropped hesitation fillers 'เนี่ย', 'ก็คือ', 'อย่างเงี้ย', 'นี่แหละ' and the STT artifact 'คล้าย/คาย' in 'ไม่ว่าใครจะใช้'; particles ครับ/นะ kept.",
        "Speaker repeated 'ตัวยี่สิบดอล' twice in the $20/$100/$200 list — collapsed to one '$20' token.",
        "Long phrase chunks (raw words 18, 24, 25 at 5.5-7.9s each) split into 3-4 karaoke groups by particle/conjunction boundaries; per-group timing interpolated by character weight inside the original ElevenLabs window.",
        "Gold policy: numbers/money/durations/percentages + brand names (Claude/Claude Code/Usage/Reset) + payoff words (อมตะ, สบายใจ). 26 gold / 116 tokens ~= 1:4.5.",
    ],
}

dst = "assets/intermediates/transcript/caption-groups.json"
json.dump(out, open(dst, "w"), ensure_ascii=False, indent=2)
gold = sum(1 for g in groups for t in g["tokens"] if t["gold"])
toks = sum(len(g["tokens"]) for g in groups)
overlaps = sum(1 for i in range(1, len(groups)) if groups[i]["start"] < groups[i-1]["end"])
print(f"wrote {dst}")
print(f"groups={len(groups)} tokens={toks} gold={gold} ratio=1:{toks/gold:.1f}")
print(f"overlaps={overlaps}  last_end={groups[-1]['end']} <= {DURATION}")
