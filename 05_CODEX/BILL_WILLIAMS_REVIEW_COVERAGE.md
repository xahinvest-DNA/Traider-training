# Bill Williams Review Coverage

Date fixed: 2026-03-30
Status: next boundary candidate v1
Priority: next

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_COVERAGE.md` bounds the next Bill Williams review-depth step after review prompts are already visible.

This slice is about one narrow thing:

- making method-review field coverage explicit at the current-session level so the user can see how consistently Bill Williams reviews are being filled across closed trades.

## In Scope

- derive-on-read current-session coverage counters over existing review fields;
- compact desktop exposure only;
- no new persistence entities.

## Out of Scope

- scoring;
- mentor analytics;
- dashboards;
- auto-classification;
- mobile/sync.

## Boundary Rule

Coverage remains:

- descriptive only;
- derive-on-read only;
- based on already persisted note/review facts.
