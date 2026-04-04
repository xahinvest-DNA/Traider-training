# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-105
Task type: bounded audit

## Goal
Run one bounded post-implementation audit after `Bill Williams Review Evidence Follow-Up` so the repository selects the single strongest next product-facing slice without continuing the evidence chain, reopening recovery-tail polish, or drifting into media workflow, dashboards, mentor logic, mobile, sync, or new persistence.

## Why this task matters now
`T-104` closed the actionability gap inside the current review loop: missing or partial chart evidence now maps to one clear next step. The next move should not be another evidence label, another follow-up state, or a small wording pass. The repository now needs one disciplined selection step to determine which bounded post-MVP slice genuinely moves the product forward.

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
6. `05_CODEX/TASKS.md`
7. `05_CODEX/NEXT_TASK.md`
8. `05_CODEX/IMPLEMENTATION_RULES.md`
9. `05_CODEX/HANDOFF_TEMPLATE.md`
10. `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_STATUS.md`
11. `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_FOLLOW_UP.md`

## Exact question to answer
After Bill Williams review evidence follow-up is implemented, what single bounded next slice now gives the strongest user-visible value inside the current local desktop review workflow without expanding architecture or continuing the evidence chain by inertia?

## Expected implementation outcome
1. One short managerial audit of the current frontier after `T-104`.
2. One explicit decision: `implement now` or `recommend only`.
3. If a next slice is clearly justified, one bounded implementation-facing document for it.
4. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after the audit.

## Files allowed to change
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`
- one new implementation-facing document in `05_CODEX/` only if the audit selects a clear next slice

## Files not to change
- `01_MASTER/DECISIONS.md` unless a true project-level decision becomes unavoidable
- `03_MODULES/*`
- `04_TECH/*`
- runtime code
- desktop shell code
- tests

## Constraints
- Stay inside desktop-first local-first boundaries.
- Do not continue the current slice with more evidence labels, extra follow-up states, or cosmetic text churn.
- Do not reopen recovery-tail polish unless a real new product problem is found.
- Do not introduce gallery/media workflow, mentor scoring, dashboard expansion, mobile, sync, or new persistence.
- Select only one next step.
- Prefer a stronger user-visible step over internal neatness.

## Acceptance criteria
- The audit identifies the real current frontier after `T-104`.
- Low-value follow-ups are explicitly rejected if they are mostly cosmetic or duplicative.
- One next bounded slice is selected or one recommend-only decision is made.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the audit result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
