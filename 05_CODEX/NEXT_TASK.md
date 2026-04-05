# NEXT TASK

Last updated: 2026-04-05
Status: ready
Task ID: T-126
Task type: implementation

## Goal
Implement one bounded `Desktop Trainer Mandatory Chart Boundary` slice so the existing chart-first workspace reaches the accepted product minimum: `bar chart only`, `Alligator`, `Fractals`, and a separate lower `AO` pane, without drifting into a broad charting platform or reopening startup/workspace architecture.

## Why this is next
`T-125` removed startup ambiguity and now routes users into the chart-first workspace through explicit start choices. The next missing product boundary is the mandatory chart surface fixed in `05_CODEX/DESKTOP_TRAINER_WORKSPACE_V1.md` and sequenced in `05_CODEX/DESKTOP_TRAINER_WORKSPACE_IMPLEMENTATION_SEQUENCE.md`.

## What should change
1. Replace the current generic replay trace with the accepted mandatory chart boundary.
2. Keep the central chart area from `T-124` but make it product-credible for the trainer.
3. Preserve replay/trading/journal ownership and avoid chart-platform drift.

## What must stay unchanged
- no launch/start-flow redesign again
- no trading-panel redesign
- no review redesign
- no broader chart toolkit or multi-chart system
- no dashboard/mobile/sync/mentor/platform scope

## Recommended validation
Run one bounded desktop-shell test pass that confirms the chart area now enforces `bar chart only + Alligator + Fractals + AO` while the rest of the workspace remains intact.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
