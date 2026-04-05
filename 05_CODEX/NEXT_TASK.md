# NEXT TASK

Last updated: 2026-04-05
Status: active
Task ID: T-113
Task type: implementation

## Goal
Implement one bounded `Pending Stop Entry` slice so the current desktop-first/local-first product can support accepted `BuyStop` / `SellStop` trigger-based entry inside the one-trade replay workflow, without turning the product into pending-order orchestration, broader risk management, mentor logic, dashboard/media scope, mobile, sync, or new persistence.

## Why this task matters now
`T-111` closed the bounded factual plan-recall gap. The next strongest product gain is not more plan visibility or more protection behavior. It is exposing the already accepted trigger-based entry path from the trading contract, because the current product still relies too heavily on immediate market entry even though the trading and desktop contracts already assume manual stop orders belong in the live loop.

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
How should the current desktop-first/local-first product expose one bounded pending stop entry path from already accepted `BuyStop` / `SellStop` contracts so the live one-trade replay loop gains real trigger-based entry behavior without drifting into pending-order orchestration, richer risk management, mentor logic, or a new persistence layer?

## Expected implementation outcome
1. One bounded pending stop entry path over existing order/trade/execution contracts only.
2. Desktop-facing exposure only through existing trading/context/result/workflow surfaces.
3. Runtime, desktop, and test updates only where required for pending stop entry visibility, trigger execution, cancellation if needed in the bounded flow, and restart recovery.
4. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after implementation.

## Files allowed to change
- runtime files strictly required for bounded pending stop entry
- desktop-shell files strictly required for bounded pending stop entry
- tests strictly required for bounded pending stop entry
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
- Reuse existing `Order`, `TradeRecord`, and `ExecutionRecord` ownership only.
- Do not introduce a new persisted queue, scheduler, order-management subsystem, or orchestration state.
- Do not broaden into pending-order expiry, OCO/bracket behavior, multiple concurrent pending orders, add-on, partial close, trailing-stop logic, or break-even automation.
- Do not backfill review/digest/evidence or reopen plan-management drift.

## Acceptance criteria
- The implementation exposes one bounded pending stop entry path from accepted `BuyStop` / `SellStop` contracts only.
- Existing desktop trading/context/result/workflow surfaces can keep the pending stop state visible without a new subsystem.
- Restart recovery restores the same pending stop state or triggered result from the same local order/trade facts.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the implementation result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.