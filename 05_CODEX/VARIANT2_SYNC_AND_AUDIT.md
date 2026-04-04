# Variant 2 State Sync and Next-Slice Audit

Last updated: 2026-04-04
Status: active
Task ID: T-101

## Purpose
Synchronize the existing Project Brain with the new Variant 2 operating layer, then choose the strongest next bounded slice for implementation.

## Problem being solved
The repository already has strong architecture, master docs, and a long Codex task ledger. The new Variant 2 operating layer is now present, but older state documents do not yet explicitly point to it. This creates a gap where the repo contains the right operating files but the main project-entry documents still behave as if the old mode is the only mode.

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
- `05_CODEX/CODEX_WORKLOG.md`
- `05_CODEX/IMPLEMENTATION_RULES.md`
- `05_CODEX/HANDOFF_TEMPLATE.md`
- `05_CODEX/BILL_WILLIAMS_REVIEW_DEPTH_PAUSE_REALIGNMENT.md`
- `05_CODEX/BILL_WILLIAMS_REVIEW_DISCIPLINE_PAUSE_REALIGNMENT.md`

## Deliverables

### Deliverable 1 — Variant 2 state synchronization
Update the existing state/navigation files so they explicitly acknowledge the new operating layer.

#### Required changes
1. Update `00_INDEX.md`
   - add links to:
     - `01_MASTER/SSOT_MAP.md`
     - `05_CODEX/NEXT_TASK.md`
     - `05_CODEX/CODEX_WORKLOG.md`
     - `05_CODEX/IMPLEMENTATION_RULES.md`
     - `05_CODEX/HANDOFF_TEMPLATE.md`
   - add one short section explaining that implementation now runs through the Variant 2 operating layer.

2. Update `01_MASTER/CURRENT_STATE.md`
   - mention that the repository now includes the Variant 2 operating layer;
   - mention that `SSOT_MAP`, `NEXT_TASK`, `CODEX_WORKLOG`, and `IMPLEMENTATION_RULES` are now part of the working operating system;
   - keep the current product focus consistent unless the audit changes it.

3. Update `05_CODEX/TASKS.md`
   - add task `T-101` as active/completed depending on the final state of this pass;
   - do not rewrite the historical ledger;
   - keep prior task history intact.

### Deliverable 2 — Next-slice audit
Run a bounded audit and choose the strongest next slice.

#### Required audit output
- rank 3 to 5 candidate next slices;
- choose one recommended slice;
- state why the selected slice wins now;
- state why the others are not next;
- create one new bounded implementation document in `05_CODEX/` for the chosen slice.

### Deliverable 3 — State handoff
- append a new entry to `05_CODEX/CODEX_WORKLOG.md`;
- update `05_CODEX/NEXT_TASK.md` so it points to the next actual implementation step after the audit;
- follow `05_CODEX/HANDOFF_TEMPLATE.md` exactly in the response.

## Constraints
- Preserve replay as the architectural center.
- Do not reopen mentor/mobile/sync/dashboard/packaging/platform scope.
- Do not continue symbolic naming-chain slices unless explicitly justified by the audit.
- Prefer real training-value or user-friction improvement.
- Keep the chosen next slice small enough for one bounded Codex pass.

## Files allowed to change
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `01_MASTER/ROADMAP.md` if needed for wording only
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`
- one new bounded task document in `05_CODEX/`

## Files not to change
- `01_MASTER/DECISIONS.md` unless a true new project-level decision is required
- `03_MODULES/*`
- `04_TECH/*`
- runtime code
- desktop shell code
- tests

## Acceptance criteria
- `00_INDEX.md` links the new operating-layer files.
- `CURRENT_STATE.md` explicitly acknowledges the Variant 2 operating layer.
- `TASKS.md` clearly records `T-101`.
- one strongest next slice is selected and documented.
- `NEXT_TASK.md` is updated to the post-audit implementation step.
- `CODEX_WORKLOG.md` records the whole pass.
