# NEXT TASK

Last updated: 2026-04-05
Status: completed
Task ID: T-117
Task type: validation

## Goal
Run one bounded local desktop workflow validation pass on the already implemented product loop and identify the strongest recurring user-visible friction point, if any, that could justify exactly one later bounded slice.

## Result
`T-117 Desktop Workflow Validation / Friction Discovery Pass` is completed. The validation does find one sufficiently strong recurring product-facing friction: transition-state language is not fully coherent across existing `trade`, `workflow`, `result`, `finalization`, `readiness`, and `pause-point` surfaces. A future bounded slice candidate is justified and recorded as `05_CODEX/DESKTOP_TRANSITION_STATE_COHERENCE.md`. No code implementation was started in this pass.

## Validation coverage
1. Empty desktop start and readiness-to-action state.
2. Market entry into active trade without declared plan context.
3. Active trade with initial protection.
4. Pending stop staging and manual cancellation.
5. Pending stop trigger into active trade.
6. Partial close while the trade remains active.
7. Full workflow through note, review, finalization, and finalized session state.
8. Restart recovery for a partially closed active trade.
9. Closed trade with review still pending.

## Observed friction points
1. Transition-state language across existing surfaces is recurring, product-facing, and slice-worthy. It appears in pending-entry, partial-close, review-pending, finalization, readiness, and recovery states where the user must reconcile multiple surfaces to infer the real next step.
2. Scientific-notation PnL formatting is visible but not selected as the strongest friction because it is mostly presentation-level and does not repeatedly distort workflow continuity by itself.
3. Rich review/evidence guidance remains dense, but validation does not show it as the strongest next-step blocker compared with the stronger cross-surface state-coherence issue.

## Rejected non-friction / weak candidates
1. Cosmetic-only layout or text-polish ideas without repeated continuity break.
2. Learning-curve discomfort that comes from the product already exposing rich but valid review vocabulary.
3. Broader adjacent feature growth in position management, pending-order orchestration, protection automation, or review backfill.
4. Mentor/dashboard/media/mobile/sync/new-persistence drift.
5. Hidden architecture rewrite or new subsystem temptation.

## Strongest conclusion
The strongest recurring friction point is bounded desktop transition-state coherence across existing workflow/result/finalization/readiness surfaces.

## Constraints kept
- no runtime files changed
- no desktop-shell files changed
- no tests changed
- `03_MODULES/*` not changed
- `04_TECH/*` not changed
- `01_MASTER/DECISIONS.md` not changed

## Acceptance criteria status
- The current desktop-first/local-first workflow is validated through realistic bounded scenario coverage: completed
- The output distinguishes real recurring friction from noise, polish, and later-phase drift: completed
- Weak adjacent candidates are explicitly rejected when they are not truly justified by validation evidence: completed
- The result ends with exactly one strongest conclusion: completed
- No runtime, desktop, test, module, or tech-schema files were changed: completed
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the validation result: completed

## Recommended next step
If implementation resumes, activate one bounded `Desktop Transition-State Coherence` slice using `05_CODEX/DESKTOP_TRANSITION_STATE_COHERENCE.md`.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
