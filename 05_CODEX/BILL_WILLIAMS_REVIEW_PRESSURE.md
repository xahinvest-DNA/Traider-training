# Bill Williams Review Pressure

Date fixed: 2026-03-30
Status: next boundary candidate v1
Priority: next

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_PRESSURE.md` bounds the next Bill Williams review-depth step after recent review headroom is already visible.

This slice is about one narrow thing:

- making it explicit whether current Bill Williams review pressure is on raising the floor, tightening the band, or pushing the ceiling.

## In Scope

- derive-on-read pressure exposure from existing floor/band/headroom state;
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

Pressure guidance remains:

- advisory-only;
- derive-on-read only;
- bounded to the current one-session desktop review workflow.
