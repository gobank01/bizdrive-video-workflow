# Tool 02's rough cut condenses (removes Water, and Content to hit a target) — not just invisible cleaning

`editorial-rules.md` defines the editorial pass as *invisible cuts only*: remove
spoiled material (retakes, false starts, fillers, stumbles, dead air) so the
result reads as if said correctly the first time, and keep everything else — its
quality bar even targets "30-50% of original for raw recordings with retakes."
Tool 02 deliberately goes further. Its default (**Clean Mode**) also removes
**Water** (rambling, over-explanation, redundant restatement, tangents) judged
against the clip's **Context**, treating rough-cutting as *condensing* / summary-
like. Its **Target Mode** (`--target <sec>`) additionally makes **Content Cuts**
— dropping whole good points — to hit a requested duration.

**Why:** The user wants short, watchable clips from possibly very watery raw
footage ("เผื่อมีน้ำเยอะ"), and explicitly accepts losing content to hit a
length. Pure invisible-cut output would still be too long and too watery.

**Consequence:** Context becomes the load-bearing input (supplied, or inferred
from the transcript when absent), and the editorial pass carries a coherence
guardrail — never cut so much that a surviving point becomes unintelligible
("ระวังการตัดทิ้งมากๆ"). The mechanical **Jump-Cut** (VAD) pass always runs
afterward to keep the condensed result smooth.
