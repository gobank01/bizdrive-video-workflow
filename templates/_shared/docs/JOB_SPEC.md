# BIZDRIVE Job Spec — feature toggles for the v88 pipeline

A **Job Spec** is a per-clip work order. Instead of describing in prose what to
keep or drop, the user builds it with **`tools/template-manager.html`** (a
standalone HTML tool — double-click to open), toggles features on/off, and
copies one block. That block is what an AI agent receives to run the pipeline.

> **For the user:** open `tools/template-manager.html` → pick a template →
> flip the switches → **คัดลอก Job Spec** → paste it into the AI chat together
> with the video. Done.
>
> **For the AI agent:** a Job Spec replaces guesswork. Read it first, honor
> every toggle. `0` means *skip that step* — do not run it "to be safe".

---

## 1. What a Job Spec looks like

The copied block has two parts. A human-readable `0/1` summary, then a fenced
`json` block — **the AI parses the JSON; the text is for the human.**

```json
{
  "spec": "bizdrive-job-spec",
  "version": 1,
  "template": "04-fullscreen-vertical-karaoke",
  "video": "https://…/clip.mp4",
  "topic": "3 ระดับการใช้ AI",
  "durationTarget": 60,
  "features": {
    "dead_air_cut": { "on": true },
    "audio_polish": { "on": true },
    "captions":     { "on": true },
    "broll":        { "on": false, "mode": "ai-gen", "max": 4 },
    "bgm":          { "on": true, "gain": 5 },
    "sfx":          { "on": false },
    "thumbnail":    { "on": true, "main": "AI มี", "hero": "3 ระดับ", "sub": "คุณอยู่ระดับไหน" }
  },
  "notes": "เน้นช่วงราคา โทนจริงจัง"
}
```

Schema: [`../schemas/job-spec.schema.json`](../schemas/job-spec.schema.json).
The feature surface of each template is declared in its
`templates/NN-*/manifest.json` under `features[]` — that is the single source of
truth the manager reads.

---

## 2. How the AI agent consumes it

1. **Parse the JSON.** Confirm `spec == "bizdrive-job-spec"`.
2. **Scaffold** the job on `template` — `bash tools/new-job.sh <NN> <slug> --raw <raw>`.
3. **Save the spec** into the job: write the JSON to `jobs/<job>/job-spec.json`
   so the run is reproducible and auditable.
4. **Run the V88_PLAYBOOK**, but for each toggleable feature:
   - `on: true`  → run the step(s) normally.
   - `on: false` → **skip** the step(s) in the gating table below, and skip any
     step that exists only to feed it.
5. Apply `notes` as creative direction throughout (editorial picks, B-roll
   taste, tone).
6. In the final report, list which features were on/off so the result is
   traceable back to the spec.

A feature that is **not present** in the spec falls back to the template
manifest's `default` for that feature (all default to `true`).

---

## 3. Feature → pipeline gating table

Steps refer to [`V88_PLAYBOOK.md`](V88_PLAYBOOK.md). "Core" steps are never
toggleable.

| Feature        | Owns step(s) | When `on: false`                                                                                  |
| -------------- | ------------ | -------------------------------------------------------------------------------------------------- |
| `dead_air_cut` | 6            | Skip Silero VAD. Step 7 applies **only** the rough EDL — original speech pacing is kept.            |
| `audio_polish` | 8            | Skip the polish chain. Use the raw audio from the visual master; Step 9 re-transcribes the raw audio. |
| `captions`     | 9 (capt.), 10, 11 (captions) | Skip the post-process subagent + `build-*-captions.py`; do not mount the caption track. Step 9 re-transcribe is still needed only if another feature needs word timing — otherwise skip it too. |
| `broll`        | 11 (B-roll)  | Skip B-roll generation and `add-broll.py`. No inserts.                                             |
| `bgm`          | 14 (BGM)     | `mix-sfx.py` runs without BGM — `final.mp4` is speech (+ SFX) only.                                 |
| `sfx`          | 14 (SFX)     | `sfx-plan.json` has an empty `sfx: []`. No sound effects.                                          |
| `end_card`     | 11 (T03)     | Do not install / mount the `tiktok-follow` block. (Template 03 only.)                              |
| `thumbnail`    | 16           | Skip Step 16. Deliver `output/finals/final.mp4` with no thumbnail poster frame prepended.          |
| `chunked`      | 0c (T07)     | Slice source into chunks, run v88 Steps 2–13 per chunk (resumable), then merge. T07 only. Options: `chunkMinutes` (default 5), `lintMode` (`soft`/`strict`, default `soft`). See [Template 07 README](../../07-fullscreen-horizontal-karaoke/README.md). |

**Core steps — always run, regardless of the spec:** 1 (inspect), 2
(transcribe), 3–5 (editorial rough cut), 7 (apply EDLs), 12 (lint), 13 (visual
render), 14 (final mux), 15 (QA).

### Feature options

- `broll.mode` — `ai-gen` (OpenRouter themed generation, default) or `stock`
  (Pexels / shared library).
- `broll.max` — hard cap on inserts (the v88 rule of ≤4 per 60s still applies as
  the lower bound).
- `bgm.gain` — BGM gain percent (default 5).
- `thumbnail.main / hero / sub` — the three headline lines for
  `build-thumbnail.py`. If blank, the agent writes them from the clip's hook.
- `end_card.name / handle / followers` — the follow-card identity.

---

## 4. Adding a new feature later

The manager is **manifest-driven** — it has no hard-coded feature list. To add a
toggle (e.g. an intro title card):

1. Add an entry to `features[]` in the relevant `templates/NN-*/manifest.json`
   (`id`, `label.th/en`, `section`, `step`, `default`, `whenOff`, optional
   `options[]`).
2. Add a gating row here in §3 so the AI knows what to skip.
3. Run `python3 tools/build-manager.py` — it re-reads every manifest and
   re-injects the data into `tools/template-manager.html`.

No edit to the manager's HTML/JS is needed — new templates and new features show
up automatically.
