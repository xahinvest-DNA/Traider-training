# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-108
Task type: audit

## Goal
Run one bounded `Post-Review-Loop Frontier Audit` so the repository can choose the next real product-facing frontier after the now-completed current-trade review loop improvements, instead of forcing another digest/evidence micro-slice or drifting into mentor, dashboard/media, workflow-engine, mobile, sync, or new-persistence scope.

## Why this task matters now
`T-102`, `T-104`, and `T-106` already solved the main diagnosis, actionability, and fragmentation gaps inside the current review loop. The `T-107` audit found that additional review-loop micro-slices would now mostly become decorative layering or workflow orchestration. The next step is therefore to re-evaluate the broader local desktop frontier instead of continuing the same lane by inertia.

## Required source-of-truth documents
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `01_MASTER/DECISIONS.md`
- `01_MASTER/ROADMAP.md`
- `01_MASTER/PRODUCT_SCOPE.md`
- `01_MASTER/MVP_vs_FULL.md`
- `01_MASTER/SSOT_MAP.md`
- `03_MODULES/DESKTOP_WORKSPACE.md`
- `03_MODULES/JOURNAL_ANALYTICS.md`
- `03_MODULES/BILL_WILLIAMS_LAYER.md`
- `04_TECH/JOURNAL_SCHEMA.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/IMPLEMENTATION_RULES.md`
- `05_CODEX/HANDOFF_TEMPLATE.md`
- `05_CODEX/DERIVED_REVIEW_OUTPUT.md`
- `05_CODEX/CURRENT_TRADE_REVIEW_DIGEST.md`

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
10. `05_CODEX/DERIVED_REVIEW_OUTPUT.md`
11. `05_CODEX/CURRENT_TRADE_REVIEW_DIGEST.md`

## Exact question to answer
If the current desktop-first/local-first review loop no longer has a strong bounded next implementation slice, which one broader local desktop product frontier should be selected next without drifting into mentor logic, dashboard/media expansion, workflow-engine state, mobile, sync, or new persistence?

## Expected outcome
1. One short, hard managerial/product audit of the broader local desktop frontier after the review-loop lane is exhausted.
2. Explicit rejection of weak candidates that merely continue review-derived layering or reopen forbidden drift areas.
3. Exactly one bounded next-step decision, or one explicit recommend-only result if no strong slice exists without scope creep.
4. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after the audit result.

## Files allowed to change
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`
- one new implementation-facing document in `05_CODEX/` only if the audit selects a clearly justified next slice

## Files not to change
- `03_MODULES/*`
- `04_TECH/*`
- runtime code
- desktop shell code
- tests
- `01_MASTER/DECISIONS.md` unless a true project-level decision becomes unavoidable

## Constraints
- Stay inside desktop-first local-first boundaries.
- Do not continue review-loop work through more digest layers, evidence layers, labels, or cosmetic wording passes.
- Do not introduce mentor logic, dashboard/media expansion, workflow-engine logic, queue/blocker/acknowledgment state, mobile, sync, or new persistence.
- Choose one next step only, not a menu of ideas.

## Acceptance criteria
- The audit identifies whether a stronger frontier now exists beyond the exhausted current review-loop lane.
- Weak or decorative candidates are explicitly rejected.
- Exactly one bounded next-step decision is made, or one explicit recommend-only result is recorded.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the audit result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
