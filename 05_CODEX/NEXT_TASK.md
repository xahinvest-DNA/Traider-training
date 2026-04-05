# NEXT TASK

Last updated: 2026-04-05
Status: active
Task ID: T-114
Task type: audit

## Goal
Run one bounded post-Pending-Stop-Entry audit so the repository selects the one strongest next local desktop product-facing slice after trigger-based stop entry is implemented, without mechanically expanding pending-order management, protection management, plan-management recall, review backfill, mentor logic, dashboard/media scope, mobile, sync, or new persistence.

## Why this task matters now
`T-113` closed the strongest remaining live-loop gap after plan recall by exposing one accepted `BuyStop` / `SellStop` path inside the current one-trade replay workflow. The next step should not be "more pending-order management." It should be a bounded frontier audit that checks whether a stronger next product-facing slice now exists elsewhere inside the local desktop workflow.

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
- `05_CODEX/PENDING_STOP_ENTRY.md`

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
14. `05_CODEX/PENDING_STOP_ENTRY.md`

## Exact question to answer
After bounded Pending Stop Entry is implemented, which one next bounded local desktop slice gives the strongest user-visible product gain without turning the product into pending-order orchestration, richer risk management, mentor logic, workflow-engine behavior, dashboard/media scope, mobile, sync, or a new persistence layer?

## Expected audit outcome
1. One explicit bounded next-step decision only.
2. Rejection of weak candidates that merely continue pending-order management, protection management, plan-management drift, review backfill, or cosmetic polish.
3. One new implementation-facing document only if the audit finds a clearly justified next slice.
4. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after the audit.

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
- desktop-shell code
- tests
- `01_MASTER/DECISIONS.md` unless a true project-level decision becomes unavoidable

## Constraints
- Stay inside desktop-first local-first boundaries.
- Do not continue pending-order management by inertia into expiry, multi-order coordination, richer editing history, or OCO/bracket behavior.
- Do not reopen protection-lane continuation, plan-management drift, or review/digest/evidence backfill.
- Do not introduce mentor logic, dashboard/media scope, mobile, sync, or new persistence.

## Acceptance criteria
- The audit identifies whether a stronger bounded next slice exists after `T-113` without relying on pending-order-management inertia.
- Weak candidates are explicitly rejected when they only deepen pending-order handling, protection management, plan management, review backfill, cosmetic polish, or forbidden drift.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the audit result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

