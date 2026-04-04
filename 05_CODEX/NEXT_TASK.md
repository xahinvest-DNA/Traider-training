# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-104
Task type: bounded coding slice

## Goal
Implement the bounded `Bill Williams Review Evidence Follow-Up` slice so the current desktop-first review flow can show one clear next step when reviewed Bill Williams interpretation still lacks linked chart context, without extending the evidence chain into mentor logic, dashboards, media workflow, mobile, sync, or new persistence.

## Why this task matters now
`T-102` made missing chart evidence visible. The strongest remaining friction is now actionability: users can see `missing` or `partial` evidence, but the workflow still stops at diagnosis. This slice turns the existing evidence status into one compact follow-up cue that helps the user complete review context without opening a new subsystem.

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
- `04_TECH/JOURNAL_SCHEMA.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/IMPLEMENTATION_RULES.md`
- `05_CODEX/HANDOFF_TEMPLATE.md`
- `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_STATUS.md`
- `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_FOLLOW_UP.md`

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
10. `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_FOLLOW_UP.md`

## Exact question to answer
How can the current local desktop review flow expose one useful follow-up signal after Bill Williams review evidence status so the user sees the safest next evidence-completion step when chart context is still missing or partial, without creating a new workflow engine or persistence state?

## Expected implementation outcome
1. One compact derive-on-read Bill Williams review evidence follow-up in current trade review output.
2. One lightweight current-session summary exposure for evidence-follow-up-needed counts/status.
3. Desktop-facing visibility only through existing result/history/context/workflow surfaces.
4. Restart recovery of the same follow-up state from existing local facts.
5. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after the slice is done.

## Files allowed to change
- `runtime_bootstrap/review_projection.py`
- `runtime_bootstrap/desktop_projection.py`
- existing desktop surface/helper files strictly needed to expose the new follow-up
- `tests/test_replay_bootstrap.py`
- `tests/test_desktop_shell.py`
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/CODEX_WORKLOG.md`
- `05_CODEX/NEXT_TASK.md`

## Files not to change
- `01_MASTER/DECISIONS.md` unless a true project-level decision becomes unavoidable
- `03_MODULES/*`
- `04_TECH/*`
- any packaging, sync, mobile, dashboard, or media-management layer
- any new persistence model or follow-up queue

## Constraints
- Preserve replay as the architectural center.
- Stay inside desktop-first local-first boundaries.
- Keep the slice derive-on-read only.
- Do not create a persisted evidence-follow-up acknowledgment or queue.
- Do not reopen screenshot automation, gallery/media workflow, scoring, mentor logic, mobile, sync, or dashboard expansion.
- Prefer one clear user-visible next step over additional symbolic status chains.

## Acceptance criteria
- Reviewed trades can expose one bounded Bill Williams review evidence follow-up when evidence is missing or partial.
- Current session summary can expose lightweight evidence-follow-up-needed counts/status for reviewed trades.
- Desktop surfaces show the follow-up through existing result/history/context/workflow surfaces only.
- Restart recovery preserves the same behavior from existing local facts.
- The slice does not introduce new persistence, workflow engine behavior, gallery/media workflow, scoring, dashboard scope, mentor logic, mobile, or sync.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
