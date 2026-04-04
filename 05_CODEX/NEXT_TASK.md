# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-102
Task type: bounded coding slice

## Goal
Implement the bounded `Bill Williams Review Evidence Status` slice so the current desktop-first review flow can show whether reviewed Bill Williams interpretation is backed by linked chart context, without drifting into media workflow, dashboard scope, mentor logic, mobile, sync, or new persistence entities.

## Why this task matters now
The bounded audit after desktop snapshot authoring showed that the strongest remaining user friction is not another snapshot surface and not another symbolic Bill Williams label. The real gap is that a reviewed method interpretation can look complete even when no linked chart evidence is attached. This slice gives snapshot authoring direct training value inside the current review loop.

## Required source-of-truth documents
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `01_MASTER/DECISIONS.md`
- `01_MASTER/ROADMAP.md`
- `01_MASTER/PRODUCT_SCOPE.md`
- `01_MASTER/MVP_vs_FULL.md`
- `01_MASTER/SSOT_MAP.md`
- `03_MODULES/BILL_WILLIAMS_LAYER.md`
- `03_MODULES/JOURNAL_ANALYTICS.md`
- `03_MODULES/DESKTOP_WORKSPACE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_STATUS.md`
- `05_CODEX/CHART_SNAPSHOT_REFERENCES.md`
- `05_CODEX/SNAPSHOT_AWARE_REVIEW_OUTPUT.md`
- `05_CODEX/SESSION_REVIEW_SUMMARY.md`
- `05_CODEX/IMPLEMENTATION_RULES.md`
- `05_CODEX/HANDOFF_TEMPLATE.md`

## Read first
1. `00_INDEX.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/ROADMAP.md`
5. `01_MASTER/SSOT_MAP.md`
6. `05_CODEX/NEXT_TASK.md`
7. `05_CODEX/IMPLEMENTATION_RULES.md`
8. `05_CODEX/HANDOFF_TEMPLATE.md`
9. `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_STATUS.md`

## Exact question to answer
How can the current local desktop review flow expose one useful evidence-status signal for reviewed Bill Williams interpretation, using only already persisted review facts and linked snapshot refs, without turning snapshot context into media workflow, scoring, or mentor logic?

## Expected implementation outcome
1. One compact derive-on-read Bill Williams review evidence status in current trade review output.
2. One lightweight current-session summary exposure for reviewed-trades-with-evidence vs reviewed-trades-missing-evidence.
3. Desktop-facing visibility only through existing result/history/context/workflow surfaces.
4. Restart recovery of the same status from existing local facts.
5. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after the slice is done.

## Files allowed to change
- `runtime_bootstrap/review_projection.py`
- `runtime_bootstrap/desktop_projection.py`
- existing desktop surface/helper files strictly needed to expose the new status
- `tests/test_replay_bootstrap.py`
- `tests/test_desktop_shell.py`
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/CODEX_WORKLOG.md`
- `05_CODEX/NEXT_TASK.md`

## Files not to change
- `01_MASTER/DECISIONS.md` unless a true project-level decision becomes unavoidable
- `03_MODULES/*`
- `04_TECH/*`
- any packaging, sync, or mobile layer
- any new gallery/media-management subsystem

## Constraints
- Preserve replay as the architectural center.
- Stay inside desktop-first local-first boundaries.
- Do not reopen screenshot automation, gallery/media workflow, validation, mentor scoring, dashboard expansion, mobile, or sync.
- Do not create new persistence entities.
- Keep the slice narrow enough for one bounded Codex pass.
- Prefer one useful user-visible signal over additional symbolic label chains.

## Acceptance criteria
- Reviewed trades can expose one bounded Bill Williams review evidence status.
- Current session summary can expose lightweight evidence-present vs evidence-missing counts for reviewed trades.
- Desktop surfaces show the signal without a new UI subsystem.
- Restart recovery preserves the same behavior from existing local facts.
- The slice does not introduce gallery/media workflow, scoring, dashboard scope, mentor logic, mobile, sync, or new persistence.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
