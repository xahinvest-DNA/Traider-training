# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-109
Task type: implementation

## Goal
Implement one bounded `Initial Trade Protection` slice so the current desktop-first/local-first product can support optional initial `stopLoss` / `takeProfit` inside the one-trade replay workflow, strengthening live trade discipline without expanding into a broader risk engine, pending-order orchestration, mentor logic, dashboard scope, mobile, sync, or new persistence.

## Why this task matters now
`T-108` confirmed that the review-loop lane is exhausted: further review-derived slices would now be weaker than opening a new productive lane in the product. The strongest broader local desktop frontier is active-trade protection, because the current workflow still relies too heavily on `entry -> manual close` and under-trains bounded protective execution discipline compared with the value already gained from diagnosis, actionability, and digesting after the trade.

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
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/IMPLEMENTATION_RULES.md`
- `05_CODEX/HANDOFF_TEMPLATE.md`
- `05_CODEX/INITIAL_TRADE_PROTECTION.md`

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
13. `05_CODEX/INITIAL_TRADE_PROTECTION.md`

## Exact question to answer
How should the current desktop-first/local-first product expose one bounded initial trade-protection path with optional initial `stopLoss` / `takeProfit` so the active trade loop becomes more useful than `entry -> manual close` only, without expanding into a broader risk engine, pending-order orchestration, mentor logic, dashboard/media scope, mobile, sync, or new persistence?

## Expected implementation outcome
1. One bounded active-trade protection path over existing trading and storage contracts.
2. Desktop-facing exposure only through existing trading/context/result surfaces.
3. Runtime, desktop, and test updates only where required for bounded initial protection.
4. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after implementation.

## Files allowed to change
- runtime files strictly required for bounded initial protection
- desktop-shell files strictly required for bounded initial protection
- tests strictly required for bounded initial protection
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
- Keep the slice bounded to initial `stopLoss` / `takeProfit` support only.
- Do not expand into trailing stops, risk scoring, add-on, partial close, pending-order expiry orchestration, mentor logic, dashboards, mobile, sync, or new persistence.
- Do not move ownership of trade facts into desktop helpers.

## Acceptance criteria
- The implementation supports one bounded active-trade protection path with optional initial `stopLoss` / `takeProfit`.
- Existing desktop trading/context/result surfaces can show the protection state without a new subsystem.
- Protective closes follow the accepted trading/storage contracts and remain restart-recoverable.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the implementation result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
