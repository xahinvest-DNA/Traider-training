# NEXT TASK

Last updated: 2026-04-05
Status: completed
Task ID: T-115
Task type: implementation

## Goal
Implement one bounded `Partial Close` slice so the current desktop-first/local-first product can support accepted active-trade volume reduction inside the one-trade replay workflow, without turning the product into broader position management, richer risk automation, mentor logic, dashboard/media scope, mobile, sync, or new persistence.

## Result
`T-115 Partial Close` is completed. The current runtime and desktop shell now support one bounded manual partial-close path inside the existing one-trade lifecycle, including execution trace, realised PnL on the closed portion, later manual/protective close on the remainder, and restart recovery from the same local facts.

## What changed
1. Runtime trading loop now accepts bounded manual partial close on an active position and preserves same-trade ownership.
2. Existing trading/context/result/workflow projections and desktop controls now expose partial-close state without a new subsystem.
3. Recovery rebuilds partially closed active-trade state and later final state from existing persisted facts only.
4. Tests cover partial-close execution, remaining-volume continuity, later full/protective close, desktop visibility, and restart recovery.

## Files changed by T-115
- runtime files strictly required for bounded partial close
- desktop-shell files strictly required for bounded partial close
- tests strictly required for bounded partial close
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

## Constraints kept
- `03_MODULES/*` not changed
- `04_TECH/*` not changed
- `01_MASTER/DECISIONS.md` not changed
- no add-on, ladder, preset fractions, trailing stop, break-even automation, mentor, dashboard/media, mobile, sync, or new persistence introduced

## Acceptance criteria status
- The implementation exposes one bounded partial-close path from accepted trading contracts only: completed
- Existing desktop trading/context/result/workflow surfaces can keep the partial-close state visible without a new subsystem: completed
- Restart recovery restores the same partially closed active-trade state or later final result from the same local facts: completed
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the implementation result: completed

## Recommended next step
Run one bounded post-Partial-Close next-slice audit before starting another implementation lane.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
