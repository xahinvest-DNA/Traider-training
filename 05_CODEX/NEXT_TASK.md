# NEXT TASK

Last updated: 2026-04-05
Status: ready
Task ID: T-128
Task type: implementation

## Goal
Implement one bounded `Desktop Trader Panel and Compact Context Surface` slice so the accepted chart-first workspace presents trading actions and nearby factual trade/session context as one coherent trader-facing surface without reopening startup, chart-boundary, review-form, or ownership scope.

## Why this is next
`T-127` protected the primary workspace from shell-text regression, so the next remaining desktop-reset gap from `05_CODEX/DESKTOP_TRAINER_WORKSPACE_IMPLEMENTATION_SEQUENCE.md` is tightening the trader panel and compact context surface around the now-stable chart-first workspace.

## What should change
1. Make the trading interaction area read as one coherent trader panel instead of a control cluster carried forward from the shell.
2. Keep only the accepted factual trade/session context next to chart and trading actions.
3. Preserve the existing chart boundary, startup chooser, review entry, and secondary/debug visibility.

## What must stay unchanged
- no chart-boundary redesign again
- no startup-flow redesign again
- no trading semantic rewrite
- no review-form redesign
- no dashboard/mobile/sync/mentor/platform scope

## Recommended validation
Run one bounded desktop-shell test pass that confirms the trading panel and compact context remain coherent, factual, and adjacent to the chart-first workspace without disturbing secondary/debug separation.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
