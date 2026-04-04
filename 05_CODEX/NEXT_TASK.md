# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-106
Task type: implementation

## Goal
Implement one bounded `Current Trade Review Digest` slice so the current desktop-first/local-first review workflow can turn fragmented review signals into one compact user-facing takeaway without continuing the evidence chain, drifting into dashboard or mentor scope, or introducing new persistence.

## Why this task matters now
`T-102` solved diagnosis and `T-104` solved evidence actionability. The post-implementation audit in `T-105` concluded that the main remaining friction is no longer missing evidence signals, but fragmented feedback: the user still has to mentally assemble many small review outputs into one trade-level takeaway. The strongest next bounded gain is therefore one compact current-trade digest built from already accepted review outputs.

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
- `04_TECH/JOURNAL_SCHEMA.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/IMPLEMENTATION_RULES.md`
- `05_CODEX/HANDOFF_TEMPLATE.md`
- `05_CODEX/DERIVED_REVIEW_OUTPUT.md`
- `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_STATUS.md`
- `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_FOLLOW_UP.md`
- `05_CODEX/CURRENT_TRADE_REVIEW_DIGEST.md`

## Read first
1. `00_INDEX.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/ROADMAP.md`
5. `01_MASTER/SSOT_MAP.md`
6. `05_CODEX/NEXT_TASK.md`
7. `05_CODEX/IMPLEMENTATION_RULES.md`
8. `05_CODEX/HANDOFF_TEMPLATE.md`
9. `05_CODEX/DERIVED_REVIEW_OUTPUT.md`
10. `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_STATUS.md`
11. `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_FOLLOW_UP.md`
12. `05_CODEX/CURRENT_TRADE_REVIEW_DIGEST.md`

## Exact question to answer
How should the current desktop-first/local-first review workflow expose one compact current-trade digest from already accepted review outputs so users get a clearer post-trade takeaway without adding mentor logic, dashboards, queue/blocker orchestration, mobile, sync, or new persistence?

## Expected implementation outcome
1. One bounded derive-on-read current-trade digest over existing source facts and accepted derived review outputs.
2. Desktop-facing exposure only through existing result/history/context/workflow surfaces.
3. Runtime, desktop, and test updates only where required for the bounded digest.
4. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after implementation.

## Files allowed to change
- runtime files strictly required for the digest
- desktop-shell files strictly required for the digest
- tests strictly required for the digest
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

## Files not to change
- `03_MODULES/*`
- `04_TECH/*`
- `01_MASTER/DECISIONS.md` unless a true project-level decision becomes unavoidable

## Constraints
- Stay inside desktop-first local-first boundaries.
- Do not continue the current slice with more evidence labels, extra follow-up states, or cosmetic text churn.
- Do not turn the digest into mentor coaching, semantic grading, or AI-authored prose.
- Do not introduce queue, blocker, acknowledgment, or workflow-engine state.
- Do not introduce gallery/media workflow, dashboard expansion, mobile, sync, or new persistence.
- Keep the digest current-trade scoped and derive-on-read only.

## Acceptance criteria
- The implementation exposes one bounded current-trade digest from existing source facts and accepted derived review outputs only.
- The digest improves current review readability without becoming a new owner of truth.
- Desktop surfaces show the digest only through existing result/history/context/workflow projections.
- Restart recovery rebuilds the same digest from existing local facts.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the implementation result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
