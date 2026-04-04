# Bill Williams Review Tag

Date fixed: 2026-03-31
Status: next boundary candidate v1
Priority: next

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_TAG.md` bounds the next Bill Williams review-depth step after current review chip is already visible.

This slice is about one narrow thing:

- making one compact Bill Williams review tag explicit from chip and pill state.

## In Scope

- derive-on-read tag exposure from existing chip/pill/badge state;
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

Tag guidance remains:

- advisory-only;
- derive-on-read only;
- bounded to the current one-session desktop review workflow.
