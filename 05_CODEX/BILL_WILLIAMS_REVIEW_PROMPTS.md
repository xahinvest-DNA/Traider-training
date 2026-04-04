# Bill Williams Review Prompts

Date fixed: 2026-03-30
Status: next boundary candidate v1
Priority: next

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_PROMPTS.md` bounds the next Bill Williams review-depth step after review completeness is already visible.

This slice is about one narrow thing:

- deriving compact review guidance prompts from existing note/review facts so the user sees what to fill next inside the current local-first desktop workflow.

## In Scope

- derive-on-read prompt hints from `intent_delta` and `review_completeness`;
- compact current-session desktop visibility only;
- no new persistence entities.

## Out of Scope

- mentor coaching system;
- auto-classification;
- scoring;
- dashboards;
- mobile/sync.

## Boundary Rule

Prompts remain:

- advisory only;
- derived from already persisted facts;
- bounded to the current one-session review workflow.
