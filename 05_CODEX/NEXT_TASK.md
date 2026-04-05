# NEXT TASK

Last updated: 2026-04-05
Status: completed
Task ID: T-118
Task type: implementation

## Goal
Implement one bounded `Desktop Transition-State Coherence` slice so the current desktop-first/local-first workflow stops forcing the user to reconcile inconsistent or misleading transition-state language across existing `trade`, `workflow`, `result`, `finalization`, `readiness`, and `pause-point` surfaces.

## Result
`T-118 Desktop Transition-State Coherence` is completed. Existing desktop-facing surfaces now tell one semantically aligned transition-state story for pending entry, clean dataset finalization/recovery, partially closed active trades, and closed/review-pending or finalized/recovered states, without changing runtime/domain logic, schemas, or ownership.

## What was implemented
1. Added one bounded desktop helper for transition-state normalization from existing replay/trading/journal facts only.
2. Updated existing `trade`, `workflow`, `finalization`, `readiness`, `pause-point`, and control-availability surfaces so pending-entry states are not described like an already open active trade.
3. Normalized clean dataset finalization/recovery wording in desktop-facing reporting so warned-dataset copy no longer leaks into clean states.
4. Kept partially closed active-trade messaging aligned across trade/workflow/result surfaces and finalized/recovered messaging aligned across workflow/finalization/readiness surfaces.
5. Added only narrow desktop-shell tests required for the bounded slice.

## Constraints kept
- no runtime/domain logic changes
- no schema changes
- no new persistence
- no new subsystem or architectural ownership change
- `03_MODULES/*` not changed
- `04_TECH/*` not changed
- `01_MASTER/DECISIONS.md` not changed

## Acceptance criteria status
- Pending-entry states are described consistently across trade/workflow/finalization surfaces and are not misleadingly treated as an already open active trade: completed
- Clean dataset states do not emit warned-dataset copy in finalization/readiness/pause-point reporting: completed
- Partially closed active states keep one semantically aligned next-step message across existing trade/workflow/result surfaces: completed
- Closed-but-review-pending and finalized/recovered states keep one semantically aligned next-step story across workflow/finalization/readiness surfaces: completed
- No runtime, schema, persistence, or architectural ownership changes were introduced unless truly unavoidable and explicitly justified: completed
- No broader feature growth was introduced: completed
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the implementation result: completed

## Recommended next step
Run one bounded post-implementation validation pass on `T-118 Desktop Transition-State Coherence` before selecting any further implementation frontier.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
