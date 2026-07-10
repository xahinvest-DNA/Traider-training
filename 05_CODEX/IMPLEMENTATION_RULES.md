# Codex Implementation Rules

Last updated: 2026-07-10
Status: active
Purpose: define how Codex reads context, interprets one task, changes files, validates work, and hands the repository back.

## Core rule

Treat this repository as the source-of-truth project system, not a loose code folder and not a continuation of chat memory.

## Automatic guidance

Codex must load the root `AGENTS.md` and the closest nested `AGENTS.md` before work. Repository-scoped skills under `.agents/skills/` should be used when their descriptions match the task.

Project hooks under `.codex/hooks.json` are advisory lifecycle checks. They require explicit trust in Codex and do not replace tests or review.

## Mandatory reading order

1. `AGENTS.md`
2. `00_INDEX.md`
3. `01_MASTER/CURRENT_STATE.md`
4. `01_MASTER/DECISIONS.md`
5. `01_MASTER/ROADMAP.md`
6. `01_MASTER/SSOT_MAP.md`
7. `01_MASTER/PRODUCT_TRUTH_GATE.md`
8. `05_CODEX/NEXT_TASK.md`
9. Relevant module/schema documents named in the active packet

## Task interpretation

- Implement only `05_CODEX/NEXT_TASK.md`.
- Historical or paused tasks in `TASKS.md` are not active scope.
- Prefer the smallest bounded change that proves the task acceptance path.
- If a change conflicts with a master decision, re-scope before coding.
- Do not start the next task inside the current task.

## Scope control

- Do not broaden scope under labels such as polish, hardening, cleanup, support, or future-proofing.
- Do not introduce new layers, abstractions, entities, caches, persistence, or UI surfaces unless the active packet requires them.
- Do not convert derive-on-read output into persisted truth.
- Do not move domain ownership into the UI.
- Do not reopen mentor, mobile, sync, dashboard, broker, portfolio, order-flow, or platform scope without an explicit master decision and active packet.
- New review cue/badge/token/marker/glyph or synonym layers are frozen.
- After T-132, correctness gates in `PRODUCT_TRUTH_GATE.md` have priority over new feature breadth.

## Git and pull request rules

- One task uses one branch and one pull request.
- Do not commit directly to `main`.
- Keep unrelated formatting and cleanup out of the task diff.
- Review the complete diff before handoff.
- CI must pass before merge.
- Prefer squash merge so one bounded task becomes one main-branch commit.

## Validation

Use Python 3.11.

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m compileall runtime_bootstrap desktop_shell
```

Additional rules:

- persistence or lifecycle changes require restart-recovery tests;
- replay/time/bar/indicator changes require sequential-vs-seek-vs-recovery equivalence tests;
- GUI behavior changes require a manual Windows/Tk smoke result;
- test success does not justify a product acceptance claim when the test only checks constant status text.

## Documentation updates

Always update on completed work:

- `05_CODEX/CODEX_WORKLOG.md`

Update when the active focus changes:

- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`

Update when authority or navigation changes:

- `00_INDEX.md`
- `01_MASTER/SSOT_MAP.md`

Update when project-level meaning changes:

- `01_MASTER/DECISIONS.md`
- the relevant master boundary document

## File authority

- Use `01_MASTER/SSOT_MAP.md` to determine ownership.
- If documents overlap, preserve the primary SSOT and reduce the weaker document to a link or implementation note.
- Do not redefine schema, domain, or product boundaries inside implementation documents.
- `00_INDEX.md` is navigation only.
- Current state lives in `CURRENT_STATE.md`.
- The active implementation packet lives in `NEXT_TASK.md`.

## Handoff

At completion, use `05_CODEX/HANDOFF_TEMPLATE.md` exactly and include:

- files changed;
- observable behavior delivered;
- commands and test results;
- manual GUI result when applicable;
- residual risks and limitations;
- confirmation that forbidden scope stayed unchanged;
- recommended next step without implementing it.

A good pass solves one bounded problem, improves repository resumability, leaves state synchronized, and creates no hidden architectural drift.