# NEXT TASK

Last updated: 2026-04-05
Status: ready
Task ID: T-130
Task type: validation

## Goal
Run one bounded `Desktop Trainer Workspace Acceptance Pass` over the now-complete desktop-reset lane so the chart-first workspace, trader rail, post-close review routing, and secondary/debug separation are validated together as one coherent training loop without opening a new feature frontier.

## Why this is next
`T-129` closed the core workspace loop from market to trade to review, so the next strongest bounded step is to validate that the assembled desktop trainer workspace behaves coherently end-to-end before choosing any broader follow-up.

## What should change
1. Verify the current desktop workspace against the accepted chart-first trainer boundary and acceptance scenario.
2. Fix only small bounded issues discovered during that validation pass.
3. Explicitly reject accidental reopening of chart/startup/trader-panel/review-subsystem scope under the label of validation.

## What must stay unchanged
- no new workspace subsystem
- no chart-boundary redesign again
- no startup-flow redesign again
- no trading semantic rewrite
- no review-form redesign
- no dashboard/mobile/sync/mentor/platform scope

## Recommended validation
Run one bounded desktop-shell acceptance-oriented test pass and record whether the current workspace now satisfies the intended `dataset -> chart -> replay -> trade -> close -> review` trainer loop without shell regression.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
