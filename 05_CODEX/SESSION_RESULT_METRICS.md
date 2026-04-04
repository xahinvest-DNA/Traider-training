# Session Result Metrics

Дата фиксации: 2026-03-19
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`SESSION_RESULT_METRICS.md` фиксирует следующий bounded slice поверх working derived review output: minimum session-level result metrics for current local `TrainingSession`.

Цель шага:

- дать bounded session-level result counters and totals для desktop basic result surface;
- считать их только derive-on-read из already persisted trade and journal facts;
- не вводить persisted `SessionSummary`, analytics cache, dashboard platform или scoring layer;
- замкнуть первый local `trade result -> session result` loop inside current runtime.

Документ не меняет source-of-truth boundaries `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md` и `DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Этот шаг логичен сразу после `DERIVED_REVIEW_OUTPUT.md`, потому что:

- closed-trade review result projection уже работает;
- desktop contract уже требует basic result surface не только по одной сделке, но и по bounded session context;
- session-level counters можно получить без нового persistence слоя;
- advanced analytics все еще можно не трогать.

Иными словами, trade-level derived output уже появился. Следующий узкий шаг - дать minimum session-level totals over the same source facts.

## Preconditions / Dependencies

Слайс опирается на уже принятые и working dependencies:

- `TradeRecord` остается source of truth для realised PnL and total trade cost;
- `TrainingSession` остается source of truth для session identity;
- `PostTradeReview`, `BehavioralFlag`, `RuleViolation` остаются source facts for review completion and discipline findings;
- `DERIVED_REVIEW_OUTPUT.md` already provides derived trade result projection;
- `JOURNAL_ANALYTICS.md` already allows derive-on-read metrics and forbids turning summaries into source of truth.

## In-Scope Behavior

В этот slice входит:

- minimum session-level derived totals for current `TrainingSession`;
- counts of closed, reviewed and pending-review trades;
- minimum result totals: session net realised PnL and session total trade cost;
- minimum outcome counts: wins, losses, flats;
- minimum time summary: total and average holding time over closed trades;
- minimum review completion ratio over closed trades;
- exposing these metrics through existing desktop-facing derived review output;
- rebuilding the same metrics after local restart from persisted source facts.

## Explicit Out-of-Scope

В этот slice не входит:

- expectancy;
- payoff ratio;
- drawdown;
- streak metrics;
- weighted severity scoring;
- persisted `SessionSummary`;
- dashboards;
- mentor workflow;
- mobile;
- sync;
- multi-session analytics;
- caching layer;
- any rewrite of trade or journal source entities.

## Runtime Contract with Existing Derived Review Output

Runtime contract for this slice:

- session metrics are derived from already available closed-trade review results and/or the same underlying source entities;
- no separate persisted session metrics artifact appears;
- desktop reads them from the same bounded `derived_review_output` payload;
- restart recovery rebuilds them after trade and journal facts are restored.

## Minimum Session Metrics Contract

Current local session may expose at least:

- `closedTradeCount`
- `reviewedTradeCount`
- `pendingReviewTradeCount`
- `sessionNetRealisedPnL`
- `sessionTotalTradeCost`
- `winTradeCount`
- `lossTradeCount`
- `flatTradeCount`
- `totalHoldingTimeSeconds`
- `averageHoldingTimeSeconds`
- `reviewCompletionRatio`
- `behavioralFlagCount`
- `ruleViolationCount`

These metrics remain derived-only and recomputable.

## Desktop-Facing Needs

Desktop basic result surface for this slice should be able to show:

- how many trades were closed in current session;
- how many were already reviewed vs still pending review;
- session net result;
- total trade cost for current session;
- basic win/loss/flat breakdown;
- bounded holding-time summary.

Desktop still does not become owner of any metric.

## Persistence Expectations

Persistence expectations remain strict:

- persisted data stays limited to existing trade and journal source entities;
- no session metrics file, table, cache or summary row is created;
- all session metrics are rebuilt from restored local facts after restart;
- any future persisted summary requires a separate later decision and slice.

## Acceptance Scenario

1. User opens a local training session.
2. Closes one or more trades in the existing trading loop.
3. Adds post-trade review for some trades and leaves others without review.
4. Desktop reads bounded derived review output.
5. User sees session-level totals: number of closed trades, reviewed/pending count, net PnL, total cost and win/loss breakdown.
6. User restarts the app.
7. Runtime restores source facts and exposes the same session-level metrics again.

## Acceptance Criteria

Слайс считается принятым, если:

- session metrics are derive-on-read only;
- session net PnL and total trade cost come from persisted closed `TradeRecord` facts;
- reviewed/pending counts reconcile with persisted `PostTradeReview` links;
- win/loss/flat counts reconcile with closed-trade outcomes;
- total/average holding time reconcile with trade open/close timestamps;
- metrics are exposed via bounded desktop-facing derived output;
- restart recovery reproduces the same session metrics;
- no analytics cache, dashboard or `SessionSummary` is introduced.

## Non-Goals / Deferred Items

Отложено на later steps:

- expectancy and payoff ratio;
- drawdown and streaks;
- weighted discipline score;
- session ranking or grading;
- series analytics;
- dashboard cards beyond current bounded output;
- persisted `SessionSummary`;
- mentor-facing result summaries.

## Risks / Boundary Protections

Главные риски:

- silently expanding basic session totals into full analytics;
- introducing a summary cache too early;
- duplicating trade-level facts instead of reading them from `TradeRecord`;
- making desktop the owner of metrics.

Boundary protections:

- metrics remain derived-only;
- only current local session is in scope;
- source facts still come from trade and journal schemas;
- anything beyond basic totals and counts requires a separate later slice.
