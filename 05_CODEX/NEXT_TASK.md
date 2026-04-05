# NEXT TASK

Last updated: 2026-04-05
Status: ready
Task ID: T-129
Task type: implementation

## Goal
Implement one bounded `Desktop Review Entry Path and Post-Close Flow` slice so the accepted chart-first workspace gives the user an explicit and usable route from closed trade state into review without turning the main surface into a review text dump or reopening startup/chart/trader-panel scope.

## Why this is next
`T-128` made the trader-side rail coherent, so the next remaining desktop-reset gap from `05_CODEX/DESKTOP_TRAINER_WORKSPACE_IMPLEMENTATION_SEQUENCE.md` is making review entry and the post-close path explicit inside the now-stable workspace.

## What should change
1. Make the route from closed trade state to review clearer and more immediate from the main workspace.
2. Keep review-needed and review-available cues compact and action-oriented.
3. Preserve the existing chart boundary, startup chooser, trader panel, and secondary/debug separation.

## What must stay unchanged
- no chart-boundary redesign again
- no startup-flow redesign again
- no trading semantic rewrite
- no review-form redesign into a new subsystem
- no dashboard/mobile/sync/mentor/platform scope

## Recommended validation
Run one bounded desktop-shell test pass that confirms post-close review entry is explicit and usable from the workspace while primary surfaces remain compact and chart-first.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
