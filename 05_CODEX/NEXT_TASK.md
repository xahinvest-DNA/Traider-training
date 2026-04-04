# NEXT TASK

Last updated: 2026-04-04
Status: active
Task ID: T-107
Task type: audit

## Goal
Run one bounded `Post-Digest Next-Slice Audit` so the repository selects the single strongest next product-facing slice after `Current Trade Review Digest` instead of continuing digest layering, evidence-chain inertia, recovery-tail polish, or drifting into mentor, dashboard/media, workflow-engine, mobile, sync, or new-persistence scope.

## Why this task matters now
`T-106` solved the current fragmentation problem by exposing one compact trade-level takeaway over existing review/evidence/discipline signals. The next step is not to keep extending the digest layer by habit, but to re-evaluate the current frontier and choose exactly one stronger user-visible slice inside the same desktop-first/local-first review loop.

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
- `05_CODEX/TASKS.md`
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
6. `05_CODEX/TASKS.md`
7. `05_CODEX/NEXT_TASK.md`
8. `05_CODEX/IMPLEMENTATION_RULES.md`
9. `05_CODEX/HANDOFF_TEMPLATE.md`
10. `05_CODEX/DERIVED_REVIEW_OUTPUT.md`
11. `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_STATUS.md`
12. `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_FOLLOW_UP.md`
13. `05_CODEX/CURRENT_TRADE_REVIEW_DIGEST.md`

## Exact question to answer
After implementing `Current Trade Review Digest`, which one bounded next slice gives the strongest user-visible value inside the current desktop-first/local-first review workflow without continuing digest/evidence layering by inertia or drifting into mentor logic, dashboard/media expansion, workflow-engine orchestration, mobile, sync, or new persistence?

## Expected outcome
1. One short, hard managerial/product audit of the current frontier.
2. Explicit rejection of weak candidates that mostly continue digest/evidence layering, cosmetic polish, mentor/dashboard/media drift, or workflow-engine logic.
3. Exactly one bounded next-step decision, or one explicit recommend-only result if no strong slice exists without scope creep.
4. Synchronization of `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` after the audit result.

## Files allowed to change
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`
- one new implementation-facing document in `05_CODEX/` only if the audit selects a clearly justified next slice

## Files not to change
- `03_MODULES/*`
- `04_TECH/*`
- runtime code
- desktop shell code
- tests
- `01_MASTER/DECISIONS.md` unless a true project-level decision becomes unavoidable

## Constraints
- Stay inside desktop-first local-first boundaries.
- Do not continue the current frontier with more digest labels, digest states, digest prose, or evidence-of-evidence layering.
- Do not accept cosmetic wording passes as product progress.
- Do not introduce mentor logic, dashboard/media expansion, workflow-engine logic, queue/blocker/acknowledgment state, mobile, sync, or new persistence.
- Choose one next step only, not a menu of ideas.

## Acceptance criteria
- The audit identifies the real current frontier after `T-106` instead of extending the digest slice by inertia.
- Weak or cosmetic candidates are explicitly rejected.
- Exactly one bounded next-step decision is made, or one explicit recommend-only result is recorded.
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the audit result.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
