# NEXT TASK

Last updated: 2026-04-05
Status: ready
Task ID: T-125
Task type: implementation

## Goal
Implement one bounded `Desktop Trainer Start Flow Clarification` slice so the new chart-first workspace has a user-credible and unambiguous entry path for prepared dataset selection, raw historical import, new session creation, and past-session restore without rewriting runtime ownership or drifting into packaging/platform work.

## Why this is next
`T-124` made the desktop shell read like a trader workspace, but the sequence fixed in `05_CODEX/DESKTOP_TRAINER_WORKSPACE_IMPLEMENTATION_SEQUENCE.md` still requires startup ambiguity to be removed before the mandatory chart boundary is implemented.

## What should change
1. Make the launch/start surface distinguish the accepted start paths: prepared dataset, raw import, new session, restore previous session.
2. Connect that start choice cleanly into the current chart-first workspace instead of leaving startup implicit or shell-centric.
3. Keep replay/trading/journal ownership unchanged and avoid packaging/platform drift.

## What must stay unchanged
- no replay engine rewrite
- no trading engine semantics rewrite
- no journal/schema changes unless truly unavoidable
- no dashboard/mobile/sync/mentor/platform scope
- no mandatory chart-boundary work yet

## Recommended validation
Run one bounded desktop-shell test pass that covers the clarified launch path and confirms the user can reach the existing chart-first workspace skeleton without startup ambiguity.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
