#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const DURATION = 103.466667;
const BROLL_DIR = "assets/broll/optimized/v87-video-div";
const REPORT_PHASE8 = "reports/phase8/v87-video-div-context-index.json";
const REPORT_PHASE9 = "reports/phase9/v87-video-div-broll-report.md";
const MANIFEST = `${BROLL_DIR}/manifest.json`;

const brollSlots = [
  {
    slot: 1,
    id: "broll01",
    start: 7,
    duration: 3,
    keyword: "ai_stock_research",
    query: "AI stock research on computer",
    source: "assets/broll/optimized/v80-setB/broll-02.mp4",
    sourceUrl: "https://www.pexels.com/video/blue-colored-cables-1085656/",
    output: `${BROLL_DIR}/broll-01.mp4`,
    provider: "pexels-index-reuse",
    contextSegment: "AI scans thousands of US stocks."
  },
  {
    slot: 2,
    id: "broll02",
    start: 28,
    duration: 3,
    keyword: "ai_calculation_workflow",
    query: "AI calculation workflow computer",
    source: "assets/broll/optimized/v80-setB/broll-01.mp4",
    sourceUrl: "https://www.pexels.com/video/person-editing-a-video-8100337/",
    output: `${BROLL_DIR}/broll-02.mp4`,
    provider: "pexels-index-reuse",
    contextSegment: "AI calculates dividend stock output."
  },
  {
    slot: 3,
    id: "broll03",
    start: 48,
    duration: 3,
    keyword: "long_term_investing",
    query: "long term investing workspace",
    source: "assets/broll/optimized/v80-setB/broll-04.mp4",
    sourceUrl: "https://www.pexels.com/video/creative-workspace-with-camera-gear-and-editing-setup-35639289/",
    output: `${BROLL_DIR}/broll-03.mp4`,
    provider: "pexels-index-reuse",
    contextSegment: "Long-term investing over 20-30 years."
  },
  {
    slot: 4,
    id: "broll04",
    start: 70,
    duration: 3,
    keyword: "us_stock_ai_assistant",
    query: "US stock investing AI assistant",
    source: "assets/broll/optimized/v80-setB/broll-05.mp4",
    sourceUrl: "https://www.pexels.com/video/a-woman-drinking-in-a-mug-while-working-in-front-of-a-computer-8100340/",
    output: `${BROLL_DIR}/broll-04.mp4`,
    provider: "pexels-index-reuse",
    contextSegment: "Use AI as an assistant for US investing."
  },
  {
    slot: 5,
    id: "broll05",
    start: 92,
    duration: 3,
    keyword: "monthly_dividend_check",
    query: "monthly dividend check computer workflow",
    source: "assets/broll/optimized/v80-setB/broll-03.mp4",
    sourceUrl: "https://www.pexels.com/video/an-audio-sequence-on-a-computer-screen-6892725/",
    output: `${BROLL_DIR}/broll-05.mp4`,
    provider: "pexels-index-reuse",
    contextSegment: "Monthly dividend method final check."
  }
];

const captions = [
  [0.0, 2.1, "cap-md", 'มีเงินใช้ฟรี'],
  [2.1, 4.5, "cap-lg", 'ปีละ <span class="gold">100,000 บาท</span>'],
  [4.5, 6.48, "cap-md", 'สุดมาก'],
  [6.48, 9.6, "cap-md", 'ให้ <span class="gold">AI</span> หาข้อมูล'],
  [9.6, 13.56, "cap-md", 'หุ้นอเมริกา'],
  [13.56, 17.52, "cap-md", 'เจอตัวดีที่สุด'],
  [17.52, 20.5, "cap-md", 'มีเงินปันผล'],
  [20.5, 24.6, "cap-md", 'แค่ลงทุนไว้'],
  [24.6, 26.56, "cap-lg", 'ปีหนึ่งเป็น <span class="gold">แสน</span>'],
  [26.56, 31.48, "cap-md", '<span class="gold">AI</span> คำนวณทั้งหมด'],
  [31.48, 36.04, "cap-md", 'เว็บทำจาก <span class="gold">AI</span>'],
  [36.04, 39.0, "cap-lg", 'ปีละ <span class="gold">แสนกว่า</span>'],
  [39.0, 41.6, "cap-md", 'ได้เงินกลับมา'],
  [41.6, 45.2, "cap-md", 'ไม่ต้องทำงานเลย'],
  [45.2, 49.0, "cap-md", 'ลงทุนระยะยาว'],
  [49.0, 51.68, "cap-lg", '<span class="gold">20-30 ปี</span>'],
  [51.68, 56.56, "cap-lg", 'กลับมาอีก <span class="gold">หลายล้าน</span>'],
  [56.56, 60.7, "cap-md", 'มีเงินเย็นหนึ่งก้อน'],
  [60.7, 62.76, "cap-md", 'ให้มันงอกเงย'],
  [62.76, 67.96, "cap-md", 'ดีกว่าฝากประจำ'],
  [67.96, 70.8, "cap-md", 'ลงทุนหุ้นสหรัฐ'],
  [70.8, 77.12, "cap-md", 'ใช้ <span class="gold">AI</span> เป็นผู้ช่วย'],
  [77.12, 81.4, "cap-md", 'ลองเรียนรู้กัน'],
  [81.4, 86.8, "cap-md", 'ฝั่งอเมริกานิยมมาก'],
  [86.8, 90.04, "cap-lg", '<span class="gold">S&P 500</span>'],
  [90.04, 93.84, "cap-md", 'ตัวดีระดับโลก'],
  [93.84, 97.0, "cap-md", 'ให้ <span class="gold">AI</span> แนะนำ'],
  [97.0, 101.84, "cap-md", 'ได้ปันผลทุกเดือน'],
  [101.84, 103.46, "cap-md", 'ลองกันนะครับ']
];

const contextIndex = {
  version: "v87",
  setId: "video-div",
  sourceFolder: "../video div",
  goal: "Full final render from video div folder after user approved trim 24s and Phase 5 sync proof.",
  originalDuration: 130.433333,
  trimStart: 24,
  phase5Duration: DURATION,
  outputDuration: DURATION,
  droppedSegments: [
    { id: "trim_front", start: 0, end: 24, duration: 24, reason: "User requested trimming the first 24 seconds." },
    { id: "opening_dead_air", start: 24.0171875, end: 24.533042, duration: 0.533333, reason: "Silence >0.5s after trim start." },
    { id: "mid_dead_air", start: 118.393771, end: 118.900688, duration: 0.533333, reason: "Silence >0.5s in edited source." },
    { id: "tail_dead_air", start: 128.541958, end: 130.433333, duration: 1.9, reason: "Trailing silence/tail dead air." }
  ],
  keptSegments: [
    { id: "hook_income", newStart: 0, newEnd: 6.48, topic: "annual dividend hook", speech: "มีเงินใช้ฟรีฟรีปีละหนึ่งแสนบาท", captionKeywords: ["100,000 บาท", "ปันผล"], keyTermsIncluded: ["ปันผล"] },
    { id: "ai_stock_research", newStart: 6.48, newEnd: 17.52, topic: "AI finds US stocks", speech: "ให้เอไอหาข้อมูล หุ้นอเมริกาหลายพันตัว", captionKeywords: ["AI", "หุ้นอเมริกา"], keyTermsIncluded: ["AI", "หุ้นอเมริกา"] },
    { id: "dividend_mechanism", newStart: 17.52, newEnd: 31.48, topic: "dividend income", speech: "มีเงินปันผล แค่ลงทุนไว้", captionKeywords: ["เงินปันผล", "ปันผล"], keyTermsIncluded: ["เงินปันผล", "ปันผล"] },
    { id: "ai_calculation", newStart: 31.48, newEnd: 45.2, topic: "AI-built web and calculation", speech: "เว็บทำจาก AI คำนวณเงินกลับมา", captionKeywords: ["AI", "แสนกว่า"], keyTermsIncluded: ["AI"] },
    { id: "long_term_result", newStart: 45.2, newEnd: 56.56, topic: "long term result", speech: "20-30 ปี ได้กลับมาหลายล้าน", captionKeywords: ["20-30 ปี", "หลายล้าน"], keyTermsIncluded: [] },
    { id: "idle_cash", newStart: 56.56, newEnd: 67.96, topic: "idle cash growth", speech: "เงินเย็นหนึ่งก้อนให้งอกเงย", captionKeywords: ["เงินเย็น", "งอกเงย"], keyTermsIncluded: [] },
    { id: "us_stock_ai", newStart: 67.96, newEnd: 83.84, topic: "US investing with AI", speech: "ลงทุนหุ้นสหรัฐ ใช้ AI เป็นผู้ช่วย", captionKeywords: ["หุ้นสหรัฐ", "AI"], keyTermsIncluded: ["AI"] },
    { id: "sp500_dividend", newStart: 83.84, newEnd: 97, topic: "S&P 500 and dividend funds", speech: "S&P 500 กองทุนปันผล ตัวดีระดับโลก", captionKeywords: ["S&P 500", "กองทุนปันผล"], keyTermsIncluded: ["S&P 500", "ปันผล"] },
    { id: "monthly_dividend", newStart: 97, newEnd: 103.466667, topic: "monthly dividend CTA", speech: "ได้ปันผลทุกเดือน อยากให้ลอง", captionKeywords: ["ปันผลทุกเดือน"], keyTermsIncluded: ["ปันผล"] }
  ],
  brollSlots: brollSlots.map((slot) => ({
    id: slot.id,
    start: slot.start,
    duration: slot.duration,
    keyword: slot.keyword,
    query: slot.query,
    provider: slot.provider,
    output: slot.output,
    qaStatus: "reuse_pass",
    contextSegment: slot.contextSegment
  })),
  protectedTerms: ["AI", "หุ้นอเมริกา", "เงินปันผล", "100,000 บาท", "20-30 ปี", "S&P 500", "ปันผลทุกเดือน"]
};

fs.mkdirSync("assets/v87-video-div", { recursive: true });
fs.mkdirSync(BROLL_DIR, { recursive: true });
fs.mkdirSync("reports/phase8", { recursive: true });
fs.mkdirSync("reports/phase9", { recursive: true });
fs.copyFileSync("../video div/bg.png", "assets/v87-video-div/bg.png");

for (const slot of brollSlots) {
  fs.copyFileSync(slot.source, slot.output);
}

fs.writeFileSync(REPORT_PHASE8, `${JSON.stringify(contextIndex, null, 2)}\n`);
fs.writeFileSync(MANIFEST, `${JSON.stringify({
  version: "v87",
  setId: "video-div",
  summary: {
    externalDownloadsNew: 0,
    openRouterGenerationsNew: 0,
    reusedSourceCount: 5,
    optimizedDerivativeCount: 5,
    rejectedCandidateCount: 0,
    freshSourcingBlockedReason: "PEXELS_API_KEY and OPENROUTER_API_KEY were not present in shell env."
  },
  qaRule: "No visible text/logo/brand/graphic from previously QA-passed indexed stock.",
  slots: brollSlots.map((slot) => ({
    slot: slot.slot,
    id: slot.id,
    start: slot.start,
    duration: slot.duration,
    keyword: slot.keyword,
    query: slot.query,
    provider: slot.provider,
    source: slot.source,
    sourceUrl: slot.sourceUrl,
    output: slot.output,
    usage: "top-frame replacement only",
    transitionMix: {
      mode: "soft",
      inDuration: 0.22,
      outDuration: 0.22
    },
    contextSegment: slot.contextSegment,
    qaStatus: "reuse_pass"
  }))
}, null, 2)}\n`);

fs.writeFileSync(REPORT_PHASE9, renderBrollReport());
fs.writeFileSync("index.html", renderHtml());

function renderBrollReport() {
  return `# v87 Video Div Phase 9 - B-roll Reuse Report

## Summary

\`\`\`text
fresh downloads: 0
AI generations: 0
reused indexed sources: 5
optimized derivatives/copies: 5
rejected candidates: 0
blocked fresh sourcing: PEXELS_API_KEY and OPENROUTER_API_KEY were not present in shell env
\`\`\`

## Slots

${brollSlots.map((slot) => `- ${slot.slot} @ ${slot.start}s / ${slot.keyword} / ${slot.provider} / ${slot.output}`).join("\n")}

## Sync Impact

\`\`\`text
B-roll replaces only the top frame.
Bottom face, bottom audio, and captions remain on the edited bottom-master timeline.
\`\`\`
`;
}

function renderHtml() {
  const captionHtml = captions.map(([start, end, klass, html], index) => {
    const id = `subtitle-${String(index + 1).padStart(2, "0")}`;
    const duration = Math.max(0.05, end - start - 0.001);
    return `      <div id="${id}" class="clip subtitle-cue ${klass}" data-start="${start.toFixed(3)}" data-duration="${duration.toFixed(3)}" data-track-index="3"><span class="caption-box">${html}</span></div>`;
  }).join("\n");

  const brollHtml = brollSlots.map((slot, index) => {
    const panPairs = [
      ["49% 50%", "51% 50%"],
      ["50% 49%", "50% 51%"],
      ["51% 50%", "49% 50%"],
      ["50% 51%", "50% 49%"],
      ["49% 50%", "51% 50%"]
    ];
    const [panFrom, panTo] = panPairs[index % panPairs.length];
    return `        <video
          id="${slot.id}"
          class="clip top-media broll-frame"
          data-layout-allow-overflow="true"
          src="${slot.output}"
          data-start="${slot.start.toFixed(3)}"
          data-duration="${slot.duration}"
          data-media-start="0"
          data-transition-mode="soft"
          data-transition-in="0.22"
          data-transition-out="0.22"
          data-pan-from="${panFrom}"
          data-pan-to="${panTo}"
          data-motion-kind="slow-broll-inner-zoom"
          data-motion-duration="${slot.duration}"
          data-track-index="${4 + index}"
          data-volume="0"
          muted
          playsinline
        ></video>`;
  }).join("\n\n");

  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@800;900&family=Inter:wght@800;900&display=swap" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; }
      .clip { position: absolute; }
      .background { inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0; }
      .video-frame { overflow: hidden; background: #000; border: 4px solid transparent; background: linear-gradient(#02040d, #02040d) padding-box, linear-gradient(135deg, #ffec7a 0%, #ffd93d 28%, rgba(244,194,15,.95) 56%, rgba(184,134,11,.9) 78%, #ffec7a 100%) border-box; box-shadow: 0 10px 26px rgba(0,0,0,.38), 0 0 22px rgba(244,194,15,.28), inset 0 0 14px rgba(255,217,61,.12); z-index: 2; }
      .top-frame-shell { position: absolute; left: 0; top: 198.9px; width: 1080px; height: 607.5px; border-radius: 30px; }
      .top-media { position: absolute; left: 4px; top: 4px; width: calc(100% - 8px); height: calc(100% - 8px); border-radius: 26px; background: #000; object-fit: contain; object-position: 50% 50%; transform-origin: center center; will-change: transform, object-position, opacity, filter; z-index: 1; }
      .bottom-frame { left: 50%; top: 846.4px; width: 607.5px; height: 607.5px; border-radius: 50%; transform: translateX(-50%); object-fit: cover; }
      .broll-frame { object-fit: cover; object-position: 50% 50%; opacity: 0; visibility: hidden; filter: brightness(.98) contrast(1.02) saturate(1.02); z-index: 4; }
      .subtitle-cue { left: 60px; right: 60px; top: 1490px; height: 160px; color: #fff; display: flex; align-items: center; justify-content: center; font-family: "IBM Plex Sans Thai", "Inter", sans-serif; font-weight: 800; line-height: 1; letter-spacing: -0.01em; text-align: center; z-index: 7; }
      .caption-box { display: inline-flex; align-items: center; justify-content: center; max-width: 92%; padding: 18px 36px; border: 1px solid rgba(244,194,15,.35); border-radius: 20px; background: linear-gradient(180deg, rgba(10,22,64,.78), rgba(8,16,50,.88)); backdrop-filter: blur(8px); box-shadow: 0 10px 28px rgba(0,0,0,.55), inset 0 0 18px rgba(244,194,15,.05); text-shadow: 0 4px 20px rgba(0,0,0,.85), 0 0 30px rgba(0,0,0,.7); white-space: nowrap; }
      .cap-xl .caption-box { font-size: 100px; }
      .cap-lg .caption-box { font-size: 84px; }
      .cap-md .caption-box { font-size: 60px; }
      .cap-sm .caption-box { font-size: 50px; }
      .gold { display: inline-block; margin: 0 .08em; padding: 0 .02em; font-family: "Inter", "IBM Plex Sans Thai", sans-serif; font-weight: 900; line-height: 1.25; vertical-align: baseline; transform-origin: center center; background: linear-gradient(180deg, #ffd93d 0%, #f4c20f 50%, #b8860b 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent; text-shadow: 0 4px 20px rgba(244,194,15,.35); }
      .caption-box > .gold:first-child { margin-left: 0; }
      .caption-box > .gold:last-child { margin-right: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${DURATION}" data-width="1080" data-height="1920">
      <img id="background" class="clip background" src="assets/v87-video-div/bg.png" alt="" data-start="0" data-duration="${DURATION}" data-track-index="0" />
      <div id="topFrameShell" class="video-frame top-frame-shell">
        <video id="topVideo" class="clip top-media" data-layout-allow-overflow="true" src="assets/v87-video-div/top_phase5.mp4" data-start="0" data-duration="${DURATION}" data-track-index="1" data-motion-kind="slow-top-inner-zoom" data-motion-duration="${DURATION}" data-volume="0" muted playsinline></video>

${brollHtml}
      </div>
      <video id="bottomVideo" class="clip video-frame bottom-frame" src="assets/v87-video-div/bottom_phase5.mp4" data-start="0" data-duration="${DURATION}" data-track-index="2" data-volume="0" muted playsinline></video>

${captionHtml}
    </div>

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const compositionDuration = ${DURATION};
      tl.from("#topVideo", { opacity: 0, duration: 0.35, ease: "power2.out" }, 0);
      tl.set("#topVideo", { scale: 1, objectPosition: "50% 50%", transformOrigin: "center center" }, 0);
      tl.to("#topVideo", { scale: 1.018, duration: compositionDuration / 2, ease: "sine.inOut" }, 0);
      tl.to("#topVideo", { scale: 1.006, duration: compositionDuration / 2, ease: "sine.inOut" }, compositionDuration / 2);

      document.querySelectorAll(".broll-frame").forEach((clip) => {
        const start = Number(clip.dataset.start || 0);
        const duration = Number(clip.dataset.duration || 0);
        const mode = clip.dataset.transitionMode || "soft";
        const fallbackDuration = mode === "bridge" ? 0.26 : 0.22;
        const inDuration = Math.min(Number(clip.dataset.transitionIn || fallbackDuration), duration / 3);
        const outDuration = Math.min(Number(clip.dataset.transitionOut || fallbackDuration), duration / 3);
        const exitStart = Math.max(start + duration - outDuration, start + inDuration);
        const panFrom = clip.dataset.panFrom || "50% 50%";
        const panTo = clip.dataset.panTo || "50% 50%";
        const enterEase = mode === "bridge" ? "power3.out" : "power2.out";
        const exitEase = mode === "bridge" ? "power2.inOut" : "power2.out";
        tl.set(clip, { autoAlpha: 0, scale: 1.006, objectPosition: panFrom, transformOrigin: "center center", filter: "brightness(0.98) contrast(1.02) saturate(1.02)" }, start - 0.001);
        tl.fromTo(clip, { autoAlpha: 0, filter: "brightness(0.98) contrast(1.02) saturate(1.02)" }, { autoAlpha: 1, filter: "brightness(1) contrast(1.03) saturate(1.04)", duration: inDuration, ease: enterEase, immediateRender: false }, start);
        tl.to(clip, { objectPosition: panTo, duration, ease: "sine.inOut" }, start);
        tl.to(clip, { scale: 1.022, duration, ease: "sine.inOut" }, start);
        tl.to(clip, { autoAlpha: 0, filter: "brightness(0.96) contrast(1.01) saturate(1.01)", duration: outDuration, ease: exitEase }, exitStart);
      });

      document.querySelectorAll(".subtitle-cue").forEach((cue) => {
        const start = Number(cue.dataset.start || 0);
        const duration = Number(cue.dataset.duration || 0);
        const enterDuration = Math.min(0.4, Math.max(0.2, duration * 0.3));
        const exitStart = Math.max(start + duration - 0.3, start + enterDuration);
        tl.fromTo(cue, { y: 30, scale: 0.92, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: enterDuration, ease: "back.out(1.7)", immediateRender: false }, start);
        const goldTargets = Array.from(cue.querySelectorAll(".gold"));
        if (goldTargets.length > 0) {
          tl.fromTo(goldTargets, { scale: 0.7, opacity: 0, transformOrigin: "center center" }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)", transformOrigin: "center center", immediateRender: false }, start + 0.1);
        }
        tl.to(cue, { opacity: 0, duration: 0.3, ease: "power2.out" }, exitStart);
      });
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
`;
}
