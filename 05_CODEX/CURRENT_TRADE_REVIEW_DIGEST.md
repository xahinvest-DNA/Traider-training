# Current Trade Review Digest

Date fixed: 2026-04-04
Status: implementation boundary v1
Priority: current

## Purpose and Scope

`CURRENT_TRADE_REVIEW_DIGEST.md` fixes one bounded post-evidence-follow-up slice for the current desktop-first/local-first review workflow.

The purpose of this slice is:

- turn the growing set of existing review signals into one compact user-facing feedback unit for the latest/current closed trade;
- assemble that digest only from already available review output, evidence follow-up, rule/behavior findings, and current review context;
- make post-trade feedback easier to read without adding mentor logic, dashboards, queueing, or new persistence;
- stop the repository from continuing the evidence chain with more labels instead of improving the usefulness of the current review loop.

This document does not change source-of-truth ownership in `03_MODULES/JOURNAL_ANALYTICS.md`, `03_MODULES/BILL_WILLIAMS_LAYER.md`, `03_MODULES/DESKTOP_WORKSPACE.md`, or `04_TECH/JOURNAL_SCHEMA.md`.

## Why this Slice is Next

This slice is next because:

- `T-102` solved diagnosis by making evidence status visible;
- `T-104` solved local actionability by mapping missing or partial evidence to one safe next step;
- the main remaining friction is now fragmentation: the user can see many useful review signals, but still has to mentally assemble them into one coherent takeaway;
- a compact digest creates stronger user-visible value than another evidence-derived label because it improves the usefulness of the whole current review loop, not just one sub-signal inside it.

## Preconditions / Dependencies

This slice depends on already working layers:

- derived trade review output;
- current session review summary;
- Bill Williams review completeness / prompts / rule-context / discipline-reason outputs where already available;
- Bill Williams review evidence status and evidence follow-up;
- existing `BehavioralFlag` / `RuleViolation` bounded exposure;
- existing desktop result/history/context/workflow surfaces.

## In-Scope Behavior

This slice includes:

- one compact derive-on-read `current_trade_review_digest` for the latest/current closed trade;
- digest assembly only from already available persisted facts and already accepted derived review outputs;
- one bounded headline-level takeaway showing what is most important about the current trade review right now;
- one bounded primary gap or pressure point when the review is still incomplete, unsupported, or rule/discipline pressured;
- one bounded next-step line only when the current review loop already has an accepted next action from existing derived signals;
- desktop-facing visibility only through existing result/history/context/workflow surfaces.

## Explicit Out-of-Scope

This slice does not include:

- new evidence states or evidence-of-evidence logic;
- new queue, blocker, acknowledgment, or workflow-engine state;
- mentor coaching or semantic grading;
- dashboard or multi-session digest expansion;
- image/media workflow expansion;
- new persistence entities or derived cache tables;
- mobile or sync continuity;
- freeform AI-generated review prose.

## Runtime Contract

Runtime contract for this slice:

- digest remains derive-on-read only;
- digest is assembled from existing trade/journal source facts plus already accepted derived review outputs;
- digest is a compact synthesis layer, not a new owner of review truth;
- digest is descriptive and workflow-supporting, not a mentor verdict and not a hard gate.

## Minimum Digest Contract

Minimum digest payload may expose:

- `current_trade_review_digest_status`
- `current_trade_review_digest_headline`
- `current_trade_review_digest_primary_gap`
- `current_trade_review_digest_next_step`

Recommended bounded status values in this slice:

- `not_applicable`
- `pending_review`
- `reviewed_clear`
- `reviewed_gap_open`

Derivation rule for this slice:

- `not_applicable` when there is no current closed trade to summarize;
- `pending_review` when the trade is closed but no meaningful review output exists yet;
- `reviewed_clear` when the trade has a reviewed interpretation and no major current-session review gap needs foregrounding;
- `reviewed_gap_open` when the trade is reviewed but existing derived output still exposes a stronger unresolved gap such as missing evidence follow-up, missing review parts, or explicit rule/discipline pressure that should stay visible.

Priority rule for a bounded `primary_gap`:

1. pending review
2. evidence follow-up still needed
3. missing review completeness parts
4. explicit rule/discipline pressure already surfaced by existing review outputs

The digest must not invent new pressure categories beyond already accepted source/derived signals.

## Desktop-Facing Needs

Desktop can use this slice to:

- show one readable post-trade takeaway without forcing the user to scan multiple small review signals;
- keep the current review loop useful inside existing result/history/context/workflow surfaces;
- foreground the strongest open review problem without introducing a queue or blocker system;
- preserve desktop as a thin projection consumer only.

## Persistence Expectations

Persistence expectations remain strict:

- no new source entity is introduced;
- no digest cache is required;
- source facts remain `TradeRecord`, `PostTradeReview`, `BehavioralFlag`, `RuleViolation`, `ChartSnapshot`, and existing journal links;
- any digest output must rebuild from local restored facts and existing derive-on-read review layers after restart.

## Acceptance Scenario

1. User runs a local desktop training session.
2. Closes a trade.
3. If no post-trade review exists yet, desktop surfaces show one compact digest centered on `pending_review`.
4. If review exists and current derived outputs are already clear enough, desktop surfaces show one compact digest summarizing that reviewed state.
5. If review exists but accepted derived outputs still expose a stronger unresolved gap, the digest foregrounds that gap and reuses the already accepted next-step signal when available.
6. User restarts the app.
7. Runtime restores source facts and rebuilds the same digest from the same local facts.

## Acceptance Criteria

This slice is accepted if:

- one bounded current-trade review digest is exposed only from existing source facts and accepted derived review outputs;
- digest improves readability of the current review loop without adding new ownership or persistence;
- pending-review, review-clear, and review-gap-open states remain compact and current-trade scoped;
- desktop surfaces can show the digest through existing result/history/context/workflow projections only;
- restart recovery rebuilds the same digest from existing local facts;
- no mentor logic, dashboard expansion, media workflow, queue/blocker orchestration, mobile/sync continuity, or new persistence is introduced.

## Non-Goals / Deferred Items

Deferred for later steps:

- multi-trade session digesting;
- mentor-facing review summaries;
- scored or weighted review ranking;
- persisted summary caches;
- LLM-authored narrative coaching;
- dashboard cards or progress tracking over digests.

## Risks / Boundary Protections

Main risks:

- turning the digest into mentor advice instead of bounded synthesis;
- quietly adding a review state machine or blocker engine;
- rebuilding the evidence chain inside a new digest wrapper;
- drifting into session/dashboard aggregation instead of current-trade usefulness.

Boundary protections:

- one current-trade digest only;
- derive-on-read only;
- current desktop workflow only;
- no new persistence;
- digest may reuse existing accepted gaps and next-step cues, but may not create a new chain of follow-up states.
