# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: T-132
Task type: coding

## Goal
Implement one bounded `Active Trade Protection Adjustment` slice so the accepted desktop trainer workspace can support trader-visible live protection adjustment on an already active trade without reopening workspace reset, startup, chart-boundary, or review-flow scope.

## Why this is next
`T-131` compared post-acceptance frontier candidates from the accepted `dataset -> chart -> replay -> trade -> close -> review` workspace baseline and selected active-trade protection adjustment as the strongest next product-facing gain. It improves the live `manage` part of the core trainer loop, fits the existing trader rail, and stays more product-meaningful than another review layer, another cleanup pass, or a platform-like replay/mode expansion.

## What should change
1. Add one bounded active-trade protection-adjustment path for the current live trade inside the accepted desktop trainer workspace.
2. Keep protection state and the available next action legible beside the existing trader panel and compact context.
3. Preserve replay/trading/journal ownership while extending the accepted workspace through one real product-facing manage-trade slice.

## What must stay unchanged
- no chart/startup/trader-rail/review-form redesign
- no trailing-stop automation, break-even automation, or protection-history subsystem
- no broker-terminal, dashboard, mentor, mobile, sync, or platform expansion
- no replay/trading/journal ownership rewrite

## Recommended validation
Use bounded runtime and desktop-shell tests to prove that an active trade can expose, update, and retain compact protection facts and actionability without reopening the accepted workspace baseline or creating broader risk-engine behavior.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
