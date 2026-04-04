# Bill Williams Review Depth

Date fixed: 2026-03-30
Status: implementation-facing boundary v1
Priority: current

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_DEPTH.md` fixes the first bounded implementation slice inside the selected post-MVP direction `Bill Williams Method Depth`.

The purpose of this slice is to deepen the quality of Bill Williams review without pretending that the product already has:

- a full signal engine;
- chart-reading automation;
- mentor workflow;
- dashboard analytics expansion;
- mobile or sync surfaces.

This slice is review-depth-first. It improves how one completed trade is interpreted and recorded inside the already accepted local-first desktop workflow.

## Why This Slice Is First

This slice is first because:

- the frozen MVP already proves replay, manual trade, local journal, review loop, and desktop usability;
- the strongest next product gain comes from making the method review more teachable and more specific;
- deeper review semantics increase training value without reopening platform scope;
- it keeps Bill Williams growth inside the core loop `replay -> trade -> review -> summary`, instead of broadening surfaces.

## Preconditions / Dependencies

This slice depends on already accepted boundaries and working implementation:

- `DATA_SCHEMA.md` remains the source of truth for trade facts;
- `JOURNAL_SCHEMA.md` remains the source of truth for session/journal facts;
- `JOURNAL_ANALYTICS.md` remains derive-on-read by default;
- `BILL_WILLIAMS_LAYER.md` remains the method boundary document;
- the local-first desktop MVP, acceptance pass, readiness, and pause-point boundaries remain frozen;
- current runtime and desktop shell already support `PreTradeNote`, `PostTradeReview`, `BehavioralFlag`, `RuleViolation`, snapshot refs, derived review output, and session review summary.

## Slice Summary

The first Bill Williams method-depth slice is:

- richer structured review-time method decomposition for one finished trade.

The slice should focus on making a reviewed trade easier to describe in Bill Williams terms through bounded structured fields and derived projections.

It should not focus on:

- automated setup detection;
- runtime trade decision support;
- mentor commentary;
- multi-session dashboards.

## In-Scope Behavior

This slice may add only the minimum review-depth structures needed for one reviewed trade:

- bounded decomposition of reviewed setup into a small set of method-specific facets;
- clearer structured distinction between declared setup intent, reviewed setup interpretation, and reviewed entry/exit quality;
- bounded review-time capture of method context that is still human-authored;
- minimum derive-on-read projection of these new review-depth fields into desktop-facing current-session review output;
- bounded validation rules so new method-depth fields stay vocabulary-backed and local-first.

## First Implementation Target

The first implementation target inside this slice is:

- `Bill Williams Review Facets` for `PostTradeReview`.

The initial facet set should stay narrow and review-authored, for example:

- `setup family` or `setup variant` refinement where current `setupTag` is too coarse;
- `entry timing` judgment in Bill Williams terms;
- `market context quality` judgment in Bill Williams terms;
- `exit quality` judgment in Bill Williams terms;
- `review confidence` or `review clarity` only if it remains a human-entered bounded label and not a scoring engine.

The exact field names may be implementation-shaped, but the semantic boundary must remain narrow and structured.

## Explicit Out-of-Scope

This slice does not include:

- full Bill Williams auto-detection;
- runtime chart-reading or signal extraction;
- auto-confirmation of Wise Man setups;
- mentor workflow or mentor-authored overlays;
- mobile review or sync continuity;
- new dashboard surfaces or multi-session analytics;
- scoring/ranking engine;
- probabilistic confidence engine;
- replay redesign;
- new trading logic;
- archive browser or broader desktop platform work.

## Runtime Contract with Existing Local-First MVP

The working local-first MVP remains the operational base.

This slice must preserve:

- replay, trading, and journal runtime contracts as already accepted;
- `PostTradeReview` as the primary review-time interpretation entity;
- `PreTradeNote` as intent, not proof;
- `RuleViolation` and `BehavioralFlag` as separate layers, not substitutes for method facets;
- current desktop shell as a thin consumer of runtime projections.

The new review-depth layer may read:

- `TradeRecord` and `ExecutionRecord` links;
- `PreTradeNote` intent fields;
- `PostTradeReview` existing fields;
- related `ChartSnapshot` refs;
- current derived review output and session timeline context.

The new review-depth layer must not become:

- a second source of truth for trade facts;
- an analytics cache;
- a signal engine;
- a UI-owned state subsystem.

## Journal Contract Expectations

If this slice needs persistence changes, they must stay inside `JOURNAL_SCHEMA.md` boundaries and attach to review entities already accepted.

Preferred persistence shape:

- extend `PostTradeReview` with bounded structured review-depth fields;
- keep `PreTradeNote` mostly unchanged except where a strictly necessary intent/refinement link is justified;
- keep `BehavioralFlag` and `RuleViolation` unchanged unless a new bounded mapping field is strictly required.

Do not introduce:

- a new primary `BillWilliamsReviewRecord` root entity;
- a separate analytics-owned method summary entity;
- multi-trade or multi-session methodology caches.

## Desktop-Facing Projection Needs

Desktop needs only bounded projection support for the current session and current trade review flow.

Minimum projection needs:

- show the richer review facets next to existing reviewed result output;
- keep declared-vs-reviewed distinction visible;
- surface missing review-depth parts as `review still partial`, not as runtime certainty;
- expose new fields through current desktop notes/review and result/history surfaces without introducing a new dashboard.

## Persistence Expectations

Persistence remains local-first.

Expectations:

- review-depth fields persist together with the current session/journal layer;
- restart recovery preserves the same reviewed trade interpretation;
- derived projections can be rebuilt from persisted review facts;
- no derived method-depth cache is introduced.

## Acceptance Scenario

A bounded acceptance scenario for this slice is:

1. User runs the already working local-first desktop workflow on one replay trade.
2. User creates or already has a `PreTradeNote` with basic Bill Williams intent.
3. User opens and closes one trade.
4. User fills `PostTradeReview` with existing fields plus the new bounded Bill Williams review facets.
5. The runtime validates and persists the review.
6. Desktop current-session result/history surfaces show the richer reviewed method interpretation.
7. After restart, the same trade review facets and projections are restored.

## Acceptance Criteria

This slice is accepted if:

- the first post-MVP Bill Williams step remains review-depth-first;
- richer method review can be captured for one trade through bounded structured fields;
- the new fields remain human-authored and vocabulary-backed;
- current source-of-truth boundaries stay unchanged;
- runtime and desktop surfaces expose the richer review without new dashboard/platform scope;
- restart recovery preserves the same review-depth interpretation;
- no full auto-detection or mentor/mobile/sync/dashboard drift is introduced.

## Non-Goals / Deferred Items

Still deferred after this slice:

- runtime candidate engine for setup families;
- chart-reading automation;
- mentor-grade semantic overlays;
- confidence or probability scoring;
- multi-session method progress analytics;
- mobile review depth;
- sync-aware methodology continuity;
- packaging/platform work.

## Risks / Boundary Protections

Main risks:

- using `review depth` as a soft label for full methodology expansion;
- quietly turning structured review facets into auto-classification verdicts;
- collapsing method facets into rule violations or behavioral flags;
- creating a second summary/caching layer instead of extending review facts cleanly.

Boundary protections:

- human-authored review remains primary;
- bounded vocabulary is preferred to free-form pseudo-automation;
- `unclear` or `not reviewed yet` remains preferable to false precision;
- trade facts stay in `DATA_SCHEMA.md`;
- journal facts stay in `JOURNAL_SCHEMA.md`;
- analytics remain derive-on-read;
- desktop remains a thin operating surface over accepted runtime contracts.

## Recommended Next Step

The next implementation step after this boundary is:

- a narrow coding slice that adds bounded `PostTradeReview` method facets, validation, persistence, derived review projection, desktop authoring support, and restart recovery.
