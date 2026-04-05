# Desktop Transition-State Coherence

Last updated: 2026-04-05
Status: implementation-facing candidate
Origin: `T-117 Desktop Workflow Validation / Friction Discovery Pass`

## Goal
Fix one bounded recurring product-facing friction inside the already implemented desktop-first/local-first workflow: user-visible transition-state language is not consistently aligned across existing `trade`, `workflow`, `result`, `finalization`, `readiness`, and `pause-point` surfaces.

## Why this slice is justified
The bounded validation pass found repeated friction in realistic desktop-loop scenarios where the product is technically capable, but the user must reconcile conflicting or misleading state messages across existing surfaces.

Repeated evidence from validation:
1. Pending-stop staging can show `Active trade: no` in trade context while finalization/blocker surfaces still behave as if an active trade is already open.
2. Clean accepted datasets can still surface `finalized_warned_link` / `pending_warned_link` / `recovered_warned_close_context` language in readiness, pause-point, and finalization messaging, which contradicts the underlying clean dataset state.
3. Transition states such as `pending entry`, `partially closed but active`, `closed but review pending`, and `finalized and recovered` require the user to manually reconcile multiple surfaces before understanding the actual next step.

This is not a new feature gap. It is a repeated continuity/clarity break inside the current accepted workflow.

## In scope
One bounded coherence pass over existing desktop-facing projection language only:
- `workflow` guidance wording
- `trade` context wording for transition states
- `result` wording where it summarizes still-active or just-closed state
- `finalization` blocker/link wording
- `readiness` and `pause-point` transition wording where they replay the same current-session state

## Explicitly out of scope
- runtime/domain logic changes
- new persistence
- new subsystem or dashboard
- broader desktop redesign
- pending-order feature growth
- protection automation
- position-management growth
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
Use only existing owners and existing desktop surfaces. The slice should correct state semantics and next-step clarity without inventing a new summary owner or orchestration layer.

## Minimum acceptance criteria
1. Pending-entry states are described consistently across trade/workflow/finalization surfaces and are not mislabeled as an already open active trade.
2. Clean dataset states do not emit warned-dataset copy in finalization/readiness/pause-point reporting.
3. Partially closed active states keep one semantically aligned next-step message across existing trade/workflow/result surfaces.
4. Closed-but-review-pending and finalized/recovered states keep one semantically aligned next-step story across workflow/finalization/readiness surfaces.
5. No runtime, schema, or architectural ownership changes are introduced.

## Why this remains bounded
The slice does not add capability. It only makes already implemented capability understandable and trustworthy in the current desktop loop, especially at the stage transitions where user confidence currently depends on cross-checking multiple surfaces by hand.
