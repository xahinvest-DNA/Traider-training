# Bill Williams Review Discipline Reason

Date fixed: 2026-04-01
Status: next boundary candidate v1
Priority: next

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_DISCIPLINE_REASON.md` fixes the next bounded implementation step after the review-discipline naming chain is intentionally paused at `review_discipline_emblem`.

This slice is about one narrow thing:

- exposing one compact Bill Williams review discipline reason that explains why the current discipline emblem landed where it did.

## In Scope

- derive-on-read discipline-reason exposure from existing review-rule-context, review-discipline-cue, review-discipline-badge, and review-discipline-emblem state;
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

Discipline-reason guidance remains:

- advisory-only;
- derive-on-read only;
- bounded to the current one-session desktop review workflow.
