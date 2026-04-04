# Session Review Summary

Дата фиксации: 2026-03-30
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`SESSION_REVIEW_SUMMARY.md` фиксирует bounded slice для compact session-level review summary поверх already working local replay/trading/journal runtime.

Цель шага:

- дать desktop компактную session-level review summary для current local `TrainingSession`;
- собрать это только из already existing derived review output и session finalization state;
- показать review completion, flags/violations, snapshot-aware context и finalization readiness в одном lightweight read model;
- не вводить dashboard layer, persisted summary cache, multi-session shell или mentor workflow.

Документ не меняет source-of-truth boundaries `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md` и `DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Этот шаг логичен сразу после session finalization, потому что:

- current runtime уже умеет закрывать/финализировать local session;
- derived review output уже дает trade-level and session-level counters;
- desktop теперь нужен compact summary entry point, чтобы не собирать session picture вручную из нескольких projections;
- это можно сделать узко и derive-on-read, без превращения summary в новый persistence layer.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- `TrainingSession` local persistence and recovery;
- existing derived review output with snapshot-aware trade results;
- existing session finalization projection;
- existing `BehavioralFlag` / `RuleViolation` persistence;
- current one-session desktop operating model from `DESKTOP_WORKSPACE.md`.

## In-Scope Behavior

В этот slice входит:

- compact session-level review summary projection for current local `TrainingSession`;
- reuse of already existing derive-on-read trade/session review output;
- reuse of already existing finalization projection for open/finalized state;
- bounded summary fields for review completion, pending review state, flags/violations and snapshot coverage;
- lightweight latest-trade review context for desktop result surface;
- rebuild of the same summary after local restart;
- desktop-facing access through existing journal projection only.

## Explicit Out-of-Scope

В этот slice не входит:

- persisted `SessionSummary` cache;
- session list or archive shell;
- dashboard widgets or BI-like cards;
- mentor workflow;
- scoring model;
- multi-session comparisons;
- analytics expansion beyond current local session;
- new storage entities.

## Runtime Contract

Runtime contract for this slice:

- session review summary remains derive-on-read only;
- summary reads from existing `TrainingSession`, derived review output and session finalization state;
- summary does not own trade, review, flag, violation or snapshot facts;
- desktop consumes summary as a compact operating projection, not as source of truth.

## Minimum Summary Contract

Minimum summary projection may expose at least:

- `sessionId`
- `derivedOnly`
- `sessionStatus`
- `finalizationStatus`
- `isSessionFinalized`
- `finalizationReason optional`
- `summaryStatus`
- `closedTradeCount`
- `reviewedTradeCount`
- `pendingReviewTradeCount`
- `pendingReviewTradeIds[]`
- `reviewCompletionRatio optional`
- `behavioralFlagCount`
- `ruleViolationCount`
- `tradesWithLinkedChartSnapshotsCount`
- `requiresForceToFinalize`
- `canFinalizeWithoutForce`
- `canFinalizeWithForce`
- `latestTradeId optional`
- `latestTradeOutcomeLabel optional`
- `latestReviewStatus optional`
- `latestSetupTag optional`
- `latestComplianceLabel optional`
- `latestLinkedChartSnapshotCount`
- `latestReviewedTradeId optional`
- `latestPendingReviewTradeId optional`

## Summary Status Semantics

This slice may derive only bounded high-level summary states such as:

- `no_closed_trades`
- `review_pending`
- `review_complete`
- `finalized_review_complete`
- `finalized_with_pending_review`

Эти labels не являются persisted workflow state machine beyond current derived summary.

## Desktop-Facing Needs

Desktop can use this summary to:

- show one compact session review block without reading multiple raw projections directly;
- highlight whether the current session is open, review-complete or finalized;
- show if pending review still blocks normal finalization;
- show basic review evidence density through flags/violations and linked snapshots;
- keep current desktop result surface lightweight and bounded.

Desktop still remains projection consumer only.

## Persistence Expectations

Persistence expectations remain strict:

- no new summary row, cache file or derived entity is introduced;
- summary is rebuilt from restored local source facts and already existing derived projections;
- any later persisted `SessionSummary` remains a separate future slice.

## Acceptance Scenario

1. User starts a local training session.
2. Creates note/review context and closes at least one trade.
3. Runtime already derives trade review output, flags/violations and snapshot-aware context.
4. Desktop reads one compact `session_review_summary` projection.
5. User sees current session review state without entering timeline or future dashboard layer.
6. User finalizes the session or leaves it open.
7. User restarts the app.
8. Runtime restores source facts and rebuilds the same compact summary.

## Acceptance Criteria

Слайс считается принятым, если:

- runtime exposes compact `session_review_summary` for current local session;
- summary reuses existing derived review output and finalization state only;
- open and finalized session state are both reflected in summary;
- summary exposes bounded review completion, flags/violations and linked snapshot coverage;
- summary is restored correctly after restart;
- no persisted summary cache, dashboard layer or multi-session shell is introduced.

## Non-Goals / Deferred Items

Отложено на later steps:

- persisted `SessionSummary` cache;
- session archive/list UI;
- dashboard counters;
- weighted discipline score;
- mentor/session digest;
- cross-session ranking or progression reporting.

## Risks / Boundary Protections

Главные риски:

- silently turning compact summary into a dashboard subsystem;
- duplicating existing finalization and review projections with separate ownership;
- introducing a hidden summary cache too early;
- overloading desktop with analytics concerns instead of bounded operating context.

Boundary protections:

- summary stays derive-on-read only;
- summary reuses existing projections instead of inventing new source facts;
- scope remains current-session only;
- anything beyond compact local session context requires a separate later slice.
