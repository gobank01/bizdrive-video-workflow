# Contributing

How to work on the BIZDRIVE video workflow without breaking it. Read
[ONBOARDING.md](ONBOARDING.md) first if you haven't set up your environment.

## Ground rules

1. **Template 01 is locked.** `templates/01-stacked-vertical-burst/` is the v88
   PERFECT CHECKPOINT. Don't change its layout, colors, or caption system for a
   new requirement — a structurally different video is a **new template**
   (`bash tools/new-template.sh NN slug`). Bug fixes to Template 01 are fine.

2. **Subagent prompts are immutable.** `templates/_shared/docs/SUBAGENT_PROMPTS.md`
   Sections A and B are load-bearing — every clause exists because of a past
   failure (see `MISTAKES.md`). Fill the `{{...}}` slots; never rewrite the rules.

3. **The 15-step pipeline order is locked.** See `V88_PLAYBOOK.md`. Steps may be
   improved internally, but the sequence (transcribe → editorial → cut → VAD →
   polish → re-transcribe → post-process → captions → render → mux → QA) stays.

4. **Edit-first + lip-sync.** Bottom audio is the master timeline; top is muted.
   All cuts happen before HyperFrames layout. Top and bottom are always trimmed
   in parallel with the same EDL. Never break this.

5. **Never commit secrets.** `.env` is gitignored. API keys live only there.
   Before every commit, confirm `git status` shows no `.env` and no key strings.

6. **Never commit large media.** `*.mp4 *.mov *.wav *.mp3`, `raw-media/`,
   `jobs/*/intermediates/`, `jobs/*/output/` are gitignored. Keep it that way.

## Workflow

```
1. Branch from main:        git checkout -b fix/<short-name>
2. Make the change.
3. Lint a composition:      cd jobs/<a-job>/workspace && npm run check
4. If you touched a script, run it against a real job to confirm.
5. Commit (see message style below).
6. Open a PR to main.
```

## Commit messages

Follow the existing history style — a one-line summary, then a body explaining
**why**, then **what changed** as bullets. Example:

```
Fix caption layer z-index — render captions above bottom video + B-roll

The #captions-mount div had no z-index, so it fell behind bottomVideo...

* templates/01.../index.html — add style="z-index: 10;"
* build-burst-captions.py — same in the generated mount line
```

## What lives where

| Change type | Where |
|-------------|-------|
| New video pattern (aspect/layout) | new template via `tools/new-template.sh` |
| Bug fix in the locked pattern | `templates/01-stacked-vertical-burst/` |
| Shared tooling (transcribe, VAD, editorial) | `templates/_shared/scripts/` |
| Pipeline docs | `templates/_shared/docs/` |
| A produced video | `jobs/YYYY-MM-DD-slug/` (via `tools/new-job.sh`) |
| Incident / lesson learned | append to `templates/_shared/docs/MISTAKES.md` |

## Adding a new template

```bash
bash tools/new-template.sh 02 horizontal-talking-head
```

Then fill in `manifest.json`, `DESIGN.md`, `index.html`, and `prompts/`. Add a
row to `templates/README.md`. Validate it against a real clip before relying on it.

## Testing a change

There is no unit-test suite — this is a media pipeline. Verify changes by:

- `npm run check` from a job workspace (HyperFrames lint/validate/inspect)
- Running the affected pipeline step against a real job's intermediates
- For composition changes: render and watch the result
- For Template 01 changes: run the golden test (see ONBOARDING.md section 4)

## When something breaks

Record real incidents in `templates/_shared/docs/MISTAKES.md` with: what
happened, why, and the locked fix. That file is the project's memory — future
contributors (and AI agents) read it before editing.
