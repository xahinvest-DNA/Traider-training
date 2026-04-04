# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-101
Task type: bounded Project Brain / product-value audit

## Goal
Run a bounded product-value audit now that desktop chart snapshot authoring is implemented, then choose the strongest next post-MVP Bill Williams/journal slice without drifting into media workflow, dashboard scope, mentor logic, mobile, sync, packaging, or unrelated desktop polish.

## Why this task matters now
The current project state explicitly says the next working step is another bounded product-value audit after snapshot authoring so the project returns to the strongest real friction point instead of continuing symbolic or low-value micro-slices.

## Required source-of-truth documents
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `01_MASTER/DECISIONS.md`
- `01_MASTER/ROADMAP.md`
- `01_MASTER/PRODUCT_SCOPE.md`
- `01_MASTER/MVP_vs_FULL.md`
- `01_MASTER/SSOT_MAP.md`
- `03_MODULES/BILL_WILLIAMS_LAYER.md`
- `03_MODULES/JOURNAL_ANALYTICS.md`
- `03_MODULES/DESKTOP_WORKSPACE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/BILL_WILLIAMS_REVIEW_DEPTH_PAUSE_REALIGNMENT.md`
- `05_CODEX/BILL_WILLIAMS_REVIEW_DISCIPLINE_PAUSE_REALIGNMENT.md`
- `05_CODEX/CHART_SNAPSHOT_REFERENCES.md`
- `05_CODEX/SNAPSHOT_TIMELINE_EXPOSURE.md`
- `05_CODEX/SNAPSHOT_AWARE_REVIEW_OUTPUT.md`

## Read first
1. `01_MASTER/CURRENT_STATE.md`
2. `01_MASTER/DECISIONS.md`
3. `01_MASTER/ROADMAP.md`
4. `01_MASTER/PRODUCT_SCOPE.md`
5. `05_CODEX/TASKS.md`
6. The two pause/realignment documents listed above

## Exact question to answer
What is the strongest next bounded slice that increases actual training value inside the accepted desktop-first Bill Williams workflow more than any other candidate, while preserving the replay-centered architecture and current local-first boundaries?

## Expected output of the audit
1. A short ranked list of 3-5 candidate next slices.
2. One recommended slice with a clear reason for selection.
3. Explicit reasons the rejected candidates are not next.
4. A bounded implementation-facing document for the chosen slice.
5. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, and `CODEX_WORKLOG.md`.

## Files allowed to change
- `01_MASTER/CURRENT_STATE.md`
- `01_MASTER/ROADMAP.md` only if sequencing text must be clarified
- `05_CODEX/TASKS.md`
- `05_CODEX/CODEX_WORKLOG.md`
- one new bounded implementation-facing document in `05_CODEX/`
- `05_CODEX/NEXT_TASK.md`
- `00_INDEX.md` only if a new bounded document must be linked for navigation

## Files not to change
- `01_MASTER/DECISIONS.md` unless the audit produces a true project-level decision that cannot remain implicit
- `03_MODULES/*`
- `04_TECH/*`
- runtime code
- desktop shell code
- tests

## Constraints
- Preserve replay as the architectural center.
- Stay inside desktop-first local-first boundaries.
- Do not reopen mentor, mobile, sync, dashboard, packaging, or signal-engine scope.
- Do not continue symbolic naming-chain slices unless the audit proves they still create the strongest product value.
- Prefer a user-friction or training-value slice over representational or cosmetic polish.
- Keep the next slice narrow enough for one bounded Codex pass.

## Acceptance criteria
- A single next slice is explicitly selected.
- The selected slice is justified against alternative candidates.
- The selected slice has a bounded implementation-facing document in `05_CODEX/`.
- `CURRENT_STATE.md` points to the selected next focus.
- `TASKS.md` records the new task state clearly.
- `CODEX_WORKLOG.md` captures the audit outcome.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
