# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-112
Task type: audit

## Goal
Run one bounded post-`Current Trade Plan Context` audit so the repository selects the next strongest local desktop product-facing slice without mechanically extending plan visibility, reopening protection-lane expansion, backfilling review-derived micro-slices, or drifting into mentor logic, dashboard/media scope, mobile, sync, or new persistence.

## Why this task matters now
`T-111` closed the bounded factual plan-recall gap: the current desktop-first/local-first product can now keep linked pre-trade setup/thesis/risk-plan facts visible during the active/current trade loop and immediately after close. The next step must not turn that recall layer into plan management, scoring, or orchestration. The repository now needs one honest frontier audit to choose the strongest next local desktop slice after plan context, instead of continuing the same lane by inertia.

## Required source-of-truth documents
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `01_MASTER/DECISIONS.md`
- `01_MASTER/ROADMAP.md`
- `01_MASTER/PRODUCT_SCOPE.md`
- `01_MASTER/MVP_vs_FULL.md`
- `01_MASTER/SSOT_MAP.md`
- `03_MODULES/TRADING_ENGINE.md`
- `03_MODULES/DESKTOP_WORKSPACE.md`
- `04_TECH/DATA_SCHEMA.md`
- `04_TECH/JOURNAL_SCHEMA.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/IMPLEMENTATION_RULES.md`
- `05_CODEX/HANDOFF_TEMPLATE.md`
- `05_CODEX/CURRENT_TRADE_PLAN_CONTEXT.md`

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
10. `03_MODULES/TRADING_ENGINE.md`
11. `03_MODULES/DESKTOP_WORKSPACE.md`
12. `04_TECH/DATA_SCHEMA.md`
13. `04_TECH/JOURNAL_SCHEMA.md`
14. `05_CODEX/CURRENT_TRADE_PLAN_CONTEXT.md`

## Exact question to answer
After bounded current-trade plan recall is implemented, which one next bounded local desktop slice now gives the strongest user-visible product gain without turning the product toward plan management, protection-lane continuation, review-loop layering, mentor logic, dashboard/media scope, mobile, sync, or new persistence?

## Expected audit outcome
1. One bounded managerial/product decision about the next strongest local desktop frontier after `T-111`.
2. Explicit rejection of weak candidates that merely extend plan visibility, protection management, review-derived layering, cosmetic polish, or forbidden drift areas.
3. Exactly one new implementation-facing document only if the audit finds a clearly justified next slice.
4. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after the audit.

## Files allowed to change
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`
- one new implementation-facing doc in `05_CODEX/` only if the audit finds a clearly justified next slice

## Files not to change
- runtime code
- desktop-shell code
- tests
- `03_MODULES/*`
- `04_TECH/*`
- `01_MASTER/DECISIONS.md` unless a true project-level decision becomes unavoidable

## Constraints
- Stay inside desktop-first local-first boundaries.
- Do not continue plan visibility into plan management, plan scoring, richer note workflow, checklist logic, or acknowledgment/orchestration behavior.
- Do not reopen protection-lane expansion such as trailing stops, break-even automation, SL/TP edit history, add-on, partial close, or pending-order orchestration.
- Do not backfill review/digest/evidence micro-slices.
- Do not drift into mentor logic, dashboard/media scope, mobile, sync, or new persistence.

## Acceptance criteria
- The audit identifies whether a stronger bounded next slice exists after `T-111` without extending plan visibility by inertia.
- Weak candidates are explicitly rejected when they only deepen plan management, protection management, review backfill, cosmetic polish, or forbidden drift.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the audit result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.