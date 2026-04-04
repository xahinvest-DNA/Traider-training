# Bill Williams Review Rule Context

Date fixed: 2026-03-31
Status: next boundary candidate v1
Priority: next

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_RULE_CONTEXT.md` fixes the next bounded implementation step after the review-depth naming chain is intentionally paused at `review_streamer`.

This slice is about one narrow thing:

- exposing one compact Bill Williams review rule context that links declared setup intent, reviewed setup interpretation, compliance judgment, and discipline outcomes inside the existing local-first desktop workflow.

## Why This Slice Is Next

This slice is selected ahead of another symbolic review carrier because:

- it improves the teachability of the method layer more directly than another naming-chain surface;
- it matches the original post-MVP aim of deeper review semantics from `BILL_WILLIAMS_REVIEW_DEPTH.md`;
- it strengthens the core loop `replay -> trade -> review -> summary` instead of extending symbolic projection depth for its own sake.

## In Scope

- bounded derive-on-read rule-context exposure over existing `PreTradeNote`, `PostTradeReview`, `BehavioralFlag`, `RuleViolation`, and derived review state;
- one compact mapping between declared setup intent, reviewed setup interpretation, compliance label, and discipline outcomes;
- current-session desktop exposure only through existing context/history/workflow or adjacent current-session surfaces;
- advisory-only wording;
- no new persistence root entities.

## Out of Scope

- full signal engine behavior;
- new auto-classification logic;
- mentor coaching;
- scoring;
- dashboards;
- mobile/sync;
- multi-session analytics growth.

## Boundary Rule

Rule-context support remains:

- derive-on-read by default;
- bounded to the current one-session desktop review workflow;
- explanatory, not judgment-automation;
- anchored to already accepted trade/journal source-of-truth boundaries.
