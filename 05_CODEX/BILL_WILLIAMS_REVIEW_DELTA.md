# Bill Williams Review Delta

Date fixed: 2026-03-30
Status: next boundary candidate v1
Priority: next

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_DELTA.md` bounds the next Bill Williams review-depth step after structured review facets are already implemented.

This slice is about one narrow thing:

- making the difference between declared pre-trade intent and reviewed post-trade interpretation explicit and readable.

It is not about automation, scoring, dashboards, mentor workflow, mobile, or sync.

## Why This Slice Is Next

Structured review facets now exist inside `PostTradeReview`, but the desktop loop still needs a clearer method-specific answer to:

- what was planned;
- what was reviewed afterward;
- where the method interpretation changed.

That comparison deepens training value without pretending runtime can classify the setup automatically.

## In Scope

- derive-on-read comparison between `PreTradeNote.setupTag` and reviewed `PostTradeReview` method fields;
- compact delta labels such as `intent_confirmed`, `intent_refined`, `intent_changed`, `intent_missing`, `review_missing`;
- bounded desktop-facing exposure in current trade/session review output;
- restart-safe rebuild from persisted note/review facts.

## Out of Scope

- auto-detection;
- mentor overlays;
- dashboards;
- scoring;
- mobile/sync;
- new runtime trade logic.

## Boundary Rule

The delta layer remains:

- derive-on-read only;
- current-session only;
- explanatory, not authoritative over raw source-of-truth entities.
