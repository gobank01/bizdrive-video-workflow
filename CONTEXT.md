# BIZDRIVE Video V3 — Domain Language

Glossary for the editing pipeline. Defines the terms used across the v88 pipeline,
the longform→shorts tool (Tool 01), and the rough-cut tool (Tool 02).

## Language

### Cutting

**Rough Cut**:
A tightened, watchable version of a raw recording: mistakes, dead air, and
**Water** removed, audio leveled (loudnorm) so it is listenable — but NOT yet
given captions, B-roll, template framing, thumbnail, or aspect-ratio reframe.
The single terminal deliverable of Tool 02 (raw in → finished file out, one
command). Keeps the source's aspect ratio and frame rate.
_Avoid_: rough edit, draft, pre-cut.

**Invisible Cut**:
A cut that removes only spoiled material — retakes, false starts, fillers,
stumbles, dead air — so the result reads as if the speaker said everything
correctly on the first try. The viewer never perceives a cut. Governed by
`editorial-rules.md`.

**Water** (a.k.a. fluff):
Words that surround a point without serving it — rambling, over-explanation,
repeated examples, tangents. The *point survives* when water is removed; only
the padding goes. Distinct from a **Content Cut** (which removes the point
itself) and from spoiled material (which is an **Invisible Cut**). Judged
against the clip's **Context**.

**Water Cut**:
Removing **Water**. Always performed in both modes — Tool 02 treats rough-cutting
as *condensing* (summary-like), not merely cleaning. The guardrail is coherence:
never cut so much that a surviving point becomes unintelligible.

**Content Cut**:
A cut that removes a whole *good* point purely to reach a shorter duration.
Unlike a **Water Cut**, the viewer loses a point. Only happens in **Target Mode**.

**Context**:
A short statement of what the clip is meant to say and what must survive. The
primary lever for telling **Water** from substance. The user may supply it; if
absent, the **Editorial Pass** infers it from the transcript before cutting.

**Clean Mode** (Tool 02 default):
Apply **Invisible Cuts** + **Water Cuts** (no **Content Cuts**), yielding the
recording's *natural length*, then *suggest* (but do not perform) which points
could be dropped to go shorter.
_Avoid_: auto mode.

**Target Mode** (Tool 02 `--target <sec>`):
Run **Clean Mode** first; if still over the target, perform **Content Cuts** on
the lowest-value points until the duration fits, and report what was dropped.

**Natural Length**:
The duration after **Invisible Cuts** + **Water Cuts** — the floor that
**Clean Mode** produces and the point at which **Target Mode** starts making
**Content Cuts**.

### Pipeline artifacts

**EDL** (Edit Decision List):
An ordered, non-overlapping list of `{start_ms, end_ms}` segments to keep from a
source, with `notes[]` documenting every cut. The editorial pass emits one; the
apply step renders it.

**Editorial Pass**:
The LLM step that reads the transcript + `editorial-rules.md` and produces the
rough EDL. Spawned as a subagent (it is load-bearing — only fill its slots,
never rewrite its rules).

**Jump-Cut**:
A second, mechanical tightening pass (Silero VAD) that removes micro-pauses
*inside* kept segments after the editorial EDL is applied. Not editorial — it
never makes content decisions.
