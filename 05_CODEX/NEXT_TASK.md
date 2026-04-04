# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-110
Task type: audit

## Goal
Run one bounded `Post-Initial-Trade-Protection Next-Slice Audit` so the current desktop-first/local-first product can choose the next strongest user-visible slice after bounded initial `stopLoss` / `takeProfit` support landed, without mechanically expanding into a broader risk engine, protection-edit workflow, mentor logic, dashboard/media scope, mobile, sync, or new persistence.

## Why this task matters now
`T-109` already strengthened the live trade loop by moving the product beyond `entry -> manual close` only. The next step should not be a reflexive extension into trailing stops, richer protection management, or other orchestration-heavy trade control. The repository now needs one disciplined frontier audit so the next slice is selected for product value rather than by local momentum inside the protection lane.

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
After bounded initial `stopLoss` / `takeProfit` support is implemented in the current one-trade replay workflow, what one strongest next local desktop product-facing slice should follow without expanding into a broader risk engine, richer trade-protection orchestration, review-loop backfill, mentor logic, dashboard/media scope, mobile, sync, or new persistence?

## Expected audit outcome
1. One explicit bounded next-step decision after initial trade protection.
2. Clear rejection of weak candidates that would only continue protection management by inertia or drift into forbidden scope.
3. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after the audit.

## Files allowed to change
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`
- one new implementation-facing document in `05_CODEX/` only if the audit finds a clearly justified next slice

## Files not to change
- `03_MODULES/*`
- `04_TECH/*`
- runtime code
- desktop-shell code
- tests
- `01_MASTER/DECISIONS.md` unless a true project-level decision becomes unavoidable

## Constraints
- Stay inside desktop-first local-first boundaries.
- Do not mechanically continue the protection lane with trailing stops, break-even automation, SL/TP edit history, pending-order orchestration, add-on, or partial-close expansion.
- Do not mechanically revive review-loop, digest, or evidence-layer micro-slices.
- Do not drift into mentor logic, dashboard/media scope, mobile, sync, or new persistence.
- Select exactly one next step only if it is materially stronger than any continuation of the bounded protection slice.

## Acceptance criteria
- The audit identifies whether a stronger bounded next slice exists after `T-109` without relying on protection-lane inertia.
- Weak candidates are explicitly rejected when they only deepen protection management, cosmetic polish, or forbidden scope.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the audit result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
