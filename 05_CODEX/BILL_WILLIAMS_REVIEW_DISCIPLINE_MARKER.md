# Bill Williams Review Discipline Marker

Date fixed: 2026-03-31
Status: next boundary candidate v1
Priority: next

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_DISCIPLINE_MARKER.md` fixes the next bounded implementation step after current review discipline token is already visible.

This slice is about one narrow thing:

- exposing one compact Bill Williams review discipline marker distilled from the new discipline token.

## In Scope

- derive-on-read discipline-marker exposure from existing review-discipline-token state;
- current-session desktop exposure only;
- advisory-only wording;
- no new persistence entities.

## Out of Scope

- mentor coaching;
- scoring;
- dashboards;
- auto-classification;
- mobile/sync.

## Boundary Rule

Discipline-marker guidance remains:

- advisory-only;
- derive-on-read only;
- bounded to the current one-session desktop review workflow.
