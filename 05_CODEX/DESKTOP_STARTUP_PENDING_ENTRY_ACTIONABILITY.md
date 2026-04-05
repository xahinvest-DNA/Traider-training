# Desktop Startup Pending-Entry Actionability

Last updated: 2026-04-05
Status: implementation-facing candidate
Origin: `T-120 Desktop Shell Startup-State Diagnostic Pass`

## Goal
Fix one bounded startup-state defect in the current desktop-first/local-first shell: when the default launch recovers a session with a generic pending market entry, the desktop should surface that state coherently and actionably instead of looking idle while most trade controls stay disabled.

## Why this slice is justified
The diagnostic pass found a real product-facing startup defect in the actual default launch path.

Repeated practical evidence:
1. Default launch reuses `desktop_shell/.local_state`, so the shell recovers the last local session whenever persisted state exists.
2. The observed persisted state contained `lifecycle_state: EntryRequested` with a placed `BuyMarket` order and `pending_order_id`, but no active trade yet.
3. Control gating correctly disables new entry actions because `entry_pending_present` is true.
4. At the same time, existing transition/workflow/finalization surfaces do not treat this generic pending market entry as a staged entry state:
   - trade context reports `Trade lifecycle focus: idle`
   - workflow guidance says `No trade is active and no review is pending`
   - finalization blockers show only `Replay is still running`
5. The user therefore lands in a recovered non-idle session that looks non-tradable and poorly explained, even though replay advance can still move the lifecycle forward.

This is not a new feature request. It is a bounded startup-state defect over already implemented capability.

## In scope
One bounded correction over existing desktop startup/recovery surfaces only:
- launch/readiness wording where recovered local-session state is summarized
- trade context wording for generic `entry_pending_present`
- workflow guidance for recovered pending market-entry state
- finalization/blocker wording where pending entry blocks close-state actions
- control/action hints where the next step should be explicit

## Explicitly out of scope
- runtime/domain logic changes
- new persistence
- new trading capability
- startup wizard or multi-screen flow
- dashboard/archive shell growth
- broader pending-order management
- broader workflow-engine growth
- mentor/media/mobile/sync scope

## Required source-of-truth documents
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `01_MASTER/DECISIONS.md`
- `01_MASTER/ROADMAP.md`
- `01_MASTER/PRODUCT_SCOPE.md`
- `01_MASTER/MVP_vs_FULL.md`
- `01_MASTER/SSOT_MAP.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/IMPLEMENTATION_RULES.md`
- `05_CODEX/HANDOFF_TEMPLATE.md`
- `03_MODULES/DESKTOP_WORKSPACE.md`
- `03_MODULES/TRADING_ENGINE.md`
- `04_TECH/DATA_SCHEMA.md`
- `04_TECH/JOURNAL_SCHEMA.md`

## Intended implementation boundary
Use existing desktop launch/controller/projection/surface owners only. The slice should make recovered pending-entry startup state truthful and actionable without inventing a new owner, reset subsystem, or startup orchestration layer.

## Minimum acceptance criteria
1. A recovered generic market-entry `EntryRequested` state is surfaced as staged entry, not as idle/no-trade state.
2. Workflow guidance tells one actionable next-step story for recovered pending market entry.
3. Finalization/readiness/blocker reporting acknowledges staged generic pending entry when it blocks normal actions.
4. The shell does not require the user to reconcile disabled trade controls with idle/no-trade wording by hand.
5. No runtime/schema/persistence or architectural ownership changes are introduced.

## Why this remains bounded
The slice does not add a new startup subsystem or new trading behavior. It only makes the already recovered one-trade lifecycle understandable and actionable when the default local launch lands in a persisted pending-entry state.
