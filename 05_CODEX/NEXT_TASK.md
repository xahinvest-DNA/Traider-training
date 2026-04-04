# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-111
Task type: implementation

## Goal
Implement one bounded `Current Trade Plan Context` slice so the current desktop-first/local-first product can keep existing linked pre-trade setup/thesis/risk-plan facts visible inside the active/current trade loop, without creating a new owner of truth, mentor logic, dashboard/media scope, mobile, sync, or new persistence.

## Why this task matters now
`T-109` made the live trade loop stronger by adding bounded initial `stopLoss` / `takeProfit`. The next strongest gain is not deeper protection management. It is keeping the user inside the context of the already declared pre-trade plan while the trade is active and immediately after it closes, because the current workflow still loses that declared setup/thesis/risk-plan context after entry and forces the user to rely on memory or jump back into note authoring.

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
How should the current desktop-first/local-first product expose one compact current-trade plan context from already linked `PreTradeNote` facts so the active/current trade loop keeps the user anchored to the declared setup, thesis, and risk plan without turning notes into a new owner of truth or drifting into mentor/workflow-engine behavior?

## Expected implementation outcome
1. One bounded derive-on-read current-trade plan context over existing linked `PreTradeNote` and trade facts.
2. Desktop-facing exposure only through existing context/result/workflow surfaces.
3. Runtime, desktop, and test updates only where required for compact current-trade plan visibility and restart recovery.
4. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after implementation.

## Files allowed to change
- runtime files strictly required for bounded current-trade plan context
- desktop-shell files strictly required for bounded current-trade plan context
- tests strictly required for bounded current-trade plan context
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
- Reuse existing `PreTradeNote` ownership and trade linkage only.
- Do not introduce a new persisted summary, plan-status machine, checklist engine, acknowledgment flow, or mentor layer.
- Do not reopen protection-lane expansion such as trailing stops, break-even automation, SL/TP edit history, add-on, partial close, or pending-order orchestration.
- Do not backfill review/digest/evidence micro-slices.

## Acceptance criteria
- The implementation exposes one compact current-trade plan context from existing linked `PreTradeNote` facts only.
- Existing desktop context/result/workflow surfaces can keep the declared plan visible without a new subsystem.
- Restart recovery restores the same plan context from the same local note and trade facts.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the implementation result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
