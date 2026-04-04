# Bill Williams Review Completeness

Date fixed: 2026-03-30
Status: next boundary candidate v1
Priority: next

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_COMPLETENESS.md` bounds the next Bill Williams review-depth step after declared-vs-reviewed delta is already visible.

This slice is about one narrow thing:

- making the completeness of a Bill Williams trade review explicit without turning missing fields into automated judgment.

## Why This Slice Is Next

The desktop loop now shows:

- declared intent;
- reviewed interpretation;
- delta between them.

The next useful training step is to make it obvious which method-review parts are still missing, partial, or sufficiently filled.

## In Scope

- derive-on-read `review completeness` labels from existing review fields and method facets;
- compact missing-part exposure such as `missing_entry_timing`, `missing_context_quality`, `missing_exit_quality`, `missing_review_clarity`;
- bounded current-session desktop visibility only.

## Out of Scope

- scoring;
- auto-classification;
- mentor workflow;
- dashboards;
- mobile/sync;
- new persistence entities.

## Boundary Rule

Completeness remains:

- derive-on-read only;
- advisory only;
- based on already persisted review facts.
