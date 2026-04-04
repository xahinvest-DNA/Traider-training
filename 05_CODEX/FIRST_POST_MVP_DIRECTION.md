# First Post-MVP Direction

Date fixed: 2026-03-30
Status: direction-selection boundary v1
Priority: current

## Purpose and Scope

`FIRST_POST_MVP_DIRECTION.md` fixes the first bounded direction after the frozen desktop MVP.

The goal of this step is to:

- explicitly choose the first post-MVP track instead of letting scope drift choose it implicitly;
- keep the accepted desktop MVP unchanged while selecting the next direction;
- make the first post-MVP move consistent with product vision, MVP boundaries, and the replay-centered architecture.

This document does not implement the chosen direction yet. It only selects and bounds it.

## Decision Summary

The first post-MVP direction is:

- `Bill Williams Method Depth`, starting from a bounded review/methodology expansion track.

It is chosen ahead of:

- mentor workflow;
- mobile review layer;
- sync/cloud continuity;
- dashboard/analytics expansion;
- packaging/platform work.

## Why This Direction Is First

This direction is first because:

- the product vision is explicitly centered on training manual decision-making in Bill Williams logic;
- the current MVP already proves replay + manual trading + journal loop, so the strongest next learning-value gain is deeper method support;
- method depth strengthens the product core instead of pulling the team sideways into delivery/platform surfaces;
- mentor/mobile/sync/dashboard work all become stronger later if the method layer is deeper first.

## What This Choice Means

The first post-MVP track should continue to reinforce:

- replay-centered trading training;
- methodological review quality;
- clearer mapping between trade facts, review facts, and Bill Williams judgment;
- bounded rule-assisted support without pretending a full signal engine already exists.

## What Is Explicitly Not Chosen First

### Not chosen first: Mentor workflow

Reason:

- mentor value is real, but it is secondary until the single-user method layer is deeper and more teachable.

### Not chosen first: Mobile review layer

Reason:

- mobile remains later review/view support, but it should consume a stronger method layer rather than outrun it.

### Not chosen first: Sync/cloud continuity

Reason:

- sync improves continuity and collaboration, but it does not deepen the product's core training value before method depth is extended.

### Not chosen first: Dashboard/analytics expansion

Reason:

- dashboards would broaden presentation before improving the actual Bill Williams training loop.

### Not chosen first: Packaging/platform work

Reason:

- the MVP is already launchable locally; packaging is operational polish, not the strongest product move.

## Chosen Direction Boundary

The chosen direction is bounded as follows:

- it must remain desktop-first initially;
- it must remain local-first initially;
- it must build on existing replay/trading/journal source-of-truth boundaries;
- it must not silently become full Bill Williams auto-detection;
- it must not silently become dashboards, sync, mentor, or mobile under a method label.

## Recommended First Slice Inside This Direction

The recommended first slice inside `Bill Williams Method Depth` is:

- a bounded `Bill Williams Review Depth` slice.

That slice should likely focus on:

- richer structured review semantics;
- clearer mapping between setup/compliance/review outcomes and method-specific rule context;
- stronger review-time method support before any auto-detection expansion.

## Deferred Later-Phase Directions

Still deferred after this selection:

- mentor workflow;
- mobile review/view layer;
- sync/cloud continuity;
- dashboard/analytics growth;
- packaging/distribution work.

## Acceptance Criteria

This direction-selection slice is accepted if:

- one explicit first post-MVP direction is chosen;
- the choice is aligned with product vision and MVP boundaries;
- non-chosen directions remain explicitly deferred;
- the next implementation-facing step can now be bounded without ambiguity.

## Risks / Boundary Protections

Main risks:

- using ?method depth? as a vague label for many unrelated features;
- smuggling in full signal-engine ambitions too early;
- reopening MVP freeze indirectly.

Boundary protections:

- the next step must still be a narrow bounded slice;
- it must remain review/method-depth-first, not platform-first;
- any mentor/mobile/sync/dashboard move still requires a separate later decision.
