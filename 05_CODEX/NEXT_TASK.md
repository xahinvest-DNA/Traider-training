# NEXT TASK

Last updated: 2026-04-05
Status: active
Task ID: T-115
Task type: implementation

## Goal
Implement one bounded `Partial Close` slice so the current desktop-first/local-first product can support accepted active-trade volume reduction inside the one-trade replay workflow, without turning the product into broader position management, richer risk automation, mentor logic, dashboard/media scope, mobile, sync, or new persistence.

## Why this task matters now
`T-113` closed the strongest trigger-based entry gap in the live loop. The next strongest product gain is not more pending-order handling. It is exposing accepted partial-close behavior from the trading contract, because the current product still collapses live trade management to hold-until-full-close behavior even though the trading contract already allows bounded scale-out inside the same one-trade lifecycle.

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
- `05_CODEX/PARTIAL_CLOSE.md`

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
14. `05_CODEX/PARTIAL_CLOSE.md`

## Exact question to answer
How should the current desktop-first/local-first product expose one bounded partial-close path from already accepted trading contracts so the live one-trade replay loop gains real active-trade management value without drifting into broader position management, risk automation, mentor logic, or a new persistence layer?

## Expected implementation outcome
1. One bounded partial-close path over existing order/position/trade/execution contracts only.
2. Desktop-facing exposure only through existing trading/context/result/workflow surfaces.
3. Runtime, desktop, and test updates only where required for partial-close visibility, correct execution/result behavior, and restart recovery.
4. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after implementation.

## Files allowed to change
- runtime files strictly required for bounded partial close
- desktop-shell files strictly required for bounded partial close
- tests strictly required for bounded partial close
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

## Files not to change
- `03_MODULES/*`
- `04_TECH/*`
- `01_MASTER/DECISIONS.md` unless a true project-level decision becomes unavoidable

## Constraints
- Stay inside desktop-first local-first boundaries.
- Reuse existing `Order`, `Position`, `TradeRecord`, and `ExecutionRecord` ownership only.
- Do not introduce a new persisted scale-out subsystem, queue, scheduler, or orchestration state.
- Do not broaden into add-on, scale-out ladders, trailing-stop logic, break-even automation, preset close templates, mentor logic, dashboard/media scope, mobile, sync, or new persistence.
- Do not backfill pending-order handling, plan-management drift, or review/digest/evidence lanes.

## Acceptance criteria
- The implementation exposes one bounded partial-close path from accepted trading contracts only.
- Existing desktop trading/context/result/workflow surfaces can keep the partial-close state visible without a new subsystem.
- Restart recovery restores the same partially closed active-trade state or later final result from the same local facts.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the implementation result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
