# Tool 02 calls the clean-cut scripts directly instead of scaffolding a job/workspace/template

The v88 pipeline and Tool 01 both run cutting through a full job scaffold: a
`jobs/<date>-<slug>/` dir with a HyperFrames `workspace/`, a `job-spec.json`, a
chosen template, and `npm run` wrappers (`apply:edits`, `rough:cut:padbleed`,
`jump:cut:edl`). Tool 02 deliberately does NOT do this — it calls the underlying
python scripts in `templates/_shared/scripts/clean-cut/` (`apply_edits.py`,
`editorial_pass.py`, `vad_detect.py`, `speech_to_edl.py`) directly with absolute
paths, writing everything into a lightweight `staging/roughcut/<date>-<slug>/`.

**Why:** A rough cut produces no captions, B-roll, template framing, or render,
so a template + workspace would be dead weight — the npm scripts are thin
wrappers over those same python files, which run from any cwd. Keeping Tool 02
scaffold-free makes it a fast, standalone "raw in → finished cut out" tool.

**Consequence / the explicit no:** Tool 02 must never depend on a template being
chosen or a `job-spec.json` existing. If its output is later fed into v88, that
is a separate, manual hand-off (drop `rough-cut.mp4` in as a new job's
`input/bottom.mp4`) — Tool 02 itself stops at the cut.
