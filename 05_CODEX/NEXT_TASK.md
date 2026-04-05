# NEXT TASK

Last updated: 2026-04-05
Status: completed
Task ID: T-121
Task type: implementation

## Goal
Implement one bounded `Desktop Startup Pending-Entry Actionability` slice so that when the default local desktop launch recovers a session with a generic pending market entry, existing desktop-facing surfaces describe that state truthfully and actionably instead of looking idle while most trade controls stay disabled.

## Result
`T-121 Desktop Startup Pending-Entry Actionability` is completed. Recovered generic market-entry `EntryRequested` startup state is now surfaced as staged entry across existing trade/workflow/finalization/readiness/pause reporting, so the shell no longer tells an idle/no-trade story while new entry controls are correctly disabled.

## What changed
1. `desktop_shell/transition_state.py` now recognizes generic recovered `entry_pending_present` state, not only pending stop staging.
2. Trade context now exposes pending entry explicitly and reports lifecycle as `market_entry_pending` for recovered generic market entry.
3. Workflow guidance now tells the user to advance/resume replay and wait for the staged entry fill instead of opening a new trade.
4. Finalization blocker/reporting continues to reflect staged entry in progress coherently.
5. Readiness and MVP pause-point reports now include lifecycle label/text so startup summaries no longer imply idle state.
6. Narrow desktop-shell tests now cover recovered generic pending market-entry startup state.

## Acceptance criteria status
- A recovered generic market-entry `EntryRequested` state is surfaced as staged entry, not as idle/no-trade state: completed
- Workflow guidance tells one actionable next-step story for recovered pending market entry: completed
- Finalization/readiness/blocker reporting acknowledges staged generic pending entry when it blocks normal actions: completed
- The shell no longer requires the user to reconcile disabled trade controls with idle/no-trade wording by hand in this startup state: completed
- No runtime, schema, persistence, or architectural ownership changes are introduced unless truly unavoidable and explicitly justified: completed
- No broader startup redesign or adjacent feature growth is introduced: completed
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the implementation result: completed

## Constraints kept
- no runtime files changed
- no `03_MODULES/*` changes
- no `04_TECH/*` changes
- no `01_MASTER/DECISIONS.md` changes
- no new persistence or startup subsystem

## Recommended next step
Run one bounded post-implementation validation pass on `T-121 Desktop Startup Pending-Entry Actionability`.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
