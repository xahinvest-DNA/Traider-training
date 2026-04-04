# Derived Review Output

Дата фиксации: 2026-03-19
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`DERIVED_REVIEW_OUTPUT.md` фиксирует следующий bounded slice поверх working replay/trading runtime, local-first journal loop, Bill Williams review hooks и manual `BehavioralFlag` / `RuleViolation` capture.

Цель шага:

- дать minimum derived review/result projection по закрытой сделке и текущей сессии;
- собрать projection только из уже persisted source-of-truth entities;
- не вводить новый persisted analytics cache, `SessionSummary` или dashboard layer;
- закрыть desktop need на basic result surface после trade close и после restart recovery.

Этот документ не меняет source-of-truth contracts `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md` и `DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Следующий шаг логичен именно сейчас, потому что:

- replay bootstrap уже реализован;
- minimal trading runtime уже реализован;
- local-first `TrainingSession` / `PreTradeNote` / `PostTradeReview` loop уже реализован;
- Bill Williams review hooks уже реализованы как bounded vocabulary layer;
- manual `BehavioralFlag` / `RuleViolation` уже persistятся и переживают restart;
- desktop contract уже требует basic result surface, но без premature analytics expansion.

Иными словами, первичные факты уже есть. Следующим узким шагом нужно не добавлять новые факты, а дать минимальный derived read over already persisted trade and review findings.

## Preconditions / Dependencies

Слайс опирается на уже принятые и работающие зависимости:

- `04_TECH/DATA_SCHEMA.md` остается source of truth для `TradeRecord` / `ExecutionRecord`;
- `04_TECH/JOURNAL_SCHEMA.md` остается source of truth для `TrainingSession`, `PreTradeNote`, `PostTradeReview`, `BehavioralFlag`, `RuleViolation`;
- `03_MODULES/JOURNAL_ANALYTICS.md` уже закрепил derive-on-read policy;
- `03_MODULES/DESKTOP_WORKSPACE.md` уже требует basic result surface и bounded note/review surface;
- working runtime уже умеет восстанавливать local persisted trade/journal state after restart.

## In-Scope Behavior

В этот slice входит:

- derive-on-read trade-level review result projection for closed trades of current `TrainingSession`;
- derived session-level review output over current local session without creating new source entities;
- linkage to existing `TradeRecord`, `PreTradeNote`, `PostTradeReview`, `BehavioralFlag`, `RuleViolation`;
- minimum outcome view: `realisedPnL`, `totalTradeCost`, holding time, basic outcome label;
- minimum review completion view: reviewed vs pending review for closed trades;
- minimum structured review projection: `setupTag`, `complianceLabel`, `reviewTags[]` when present;
- minimum behavioral/rule projection: counts and codes linked to trade;
- desktop-facing access to this derived output inside bounded journal/result surface;
- rebuild of the same derived output after local restart from persisted source facts.

## Explicit Out-of-Scope

В этот slice не входит:

- new persisted analytics cache;
- persisted `SessionSummary`;
- advanced analytics, expectancy, drawdown, streaks, scoring or weighted severity math;
- mentor workflow;
- dashboards;
- mobile;
- sync;
- auto-detection or derived `BehavioralFlag` / `RuleViolation` production;
- Bill Williams auto-classification;
- chart/media management;
- replay redesign;
- new trading logic or new execution model.

## Runtime Contract with Working Review-Assisted Journal Loop

Derived review output reads only from already available runtime state backed by persisted source-of-truth entities:

- closed `TradeRecord` facts from trading runtime;
- linked `PreTradeNote` records;
- linked `PostTradeReview` records;
- linked `BehavioralFlag` records;
- linked `RuleViolation` records;
- current `TrainingSession` identity and bounded session context.

Runtime contract for this slice:

- derived output must be recomputable at any moment from current in-memory source facts;
- derived output must not be stored as a new primary entity;
- derived output may be exposed through desktop projection;
- restart recovery must rebuild the same derived output after source facts are restored.

## Derived Trade Review Result Minimum Contract

For every closed trade in the current local session, runtime may expose a derived trade review result with at least:

- `tradeId`
- `sessionId`
- `status`
- `openedAt`
- `closedAt`
- `closeReason`
- `side`
- `realisedPnL`
- `totalTradeCost`
- derived `holdingTimeSeconds`
- derived outcome label: `win`, `loss`, `flat` or `open`
- derived review status: `reviewed`, `pending_review` or `not_ready`
- projected `setupTag` from latest linked review, otherwise latest linked note
- projected `complianceLabel` from latest linked post-trade review when present
- projected `reviewTags[]` from latest linked post-trade review when present
- note/review presence flags and counts
- behavioral/rule counts and linked code lists
- optional latest linked note/review payload for bounded desktop display

This trade result is a read model only.

## Session-Level Derived Output Minimum Contract

Runtime may expose one bounded session-level derived review output for current `TrainingSession` with at least:

- `sessionId`
- `derivedOnly = true`
- `closedTradeCount`
- `reviewedTradeCount`
- `pendingReviewTradeCount`
- `behavioralFlagCount`
- `ruleViolationCount`
- ordered list of derived trade review results for closed trades
- `latestTradeResult optional`

Этот output нужен только для local desktop result/review surface и не является заменой optional future `SessionSummary`.

## Desktop-Facing Projection Needs

Desktop surface для этого шага должен получить minimum read-only projection, достаточный чтобы:

- после close показать базовый trade result;
- показать, оставлен ли `PostTradeReview`;
- показать latest `setupTag` / `complianceLabel` / `reviewTags[]` when present;
- показать linked behavioral/rule findings counts;
- показать pending review state, если сделка закрыта, но review еще не создан;
- после restart восстановить тот же bounded result/review view.

Desktop не становится owner этого output и не persistит его как primary fact.

## Persistence Expectations

Persistence expectations для этого slice жестко ограничены:

- persistятся только existing source-of-truth entities из trade storage и journal schema;
- derived review output не получает отдельный persisted файл, table или cache;
- derived output rebuilds from restored local `TradeRecord`, `PreTradeNote`, `PostTradeReview`, `BehavioralFlag`, `RuleViolation`, `TrainingSession`;
- если later появится persisted cache, это будет отдельный шаг и отдельный derived-only contract.

## Acceptance Scenario

1. Пользователь запускает local training session.
2. Открывает и закрывает одну сделку внутри already working replay/trading loop.
3. Runtime сохраняет `TradeRecord` / `ExecutionRecord` facts.
4. Пользователь optionally создает `PreTradeNote`.
5. После close пользователь creates `PostTradeReview` and optionally adds `BehavioralFlag` / `RuleViolation`.
6. Desktop journal/result surface читает bounded derived review output.
7. Пользователь видит result по сделке: outcome, holding time, total cost, review status and linked findings.
8. Пользователь закрывает приложение.
9. После restart runtime восстанавливает source facts.
10. Тот же derived review output снова доступен без отдельного persisted summary layer.

## Acceptance Criteria

Слайс считается принятым, если:

- derived review output строится только из existing persisted source facts;
- no new source-of-truth entity or analytics cache is introduced;
- desktop-facing journal/result projection получает минимум trade/session review output;
- closed trade without review is visible as `pending_review`;
- closed trade with review is visible as `reviewed`;
- setup/compliance/review tag hooks correctly project from linked note/review entities;
- behavioral/rule findings are visible as bounded counts and code lists;
- restart recovery rebuilds the same derived output from local persisted state;
- implementation does not expand into dashboards, mentor, scoring, sync or advanced analytics.

## Non-Goals / Deferred Items

Отложено на later steps:

- expectancy, payoff ratio, drawdown and session statistics;
- weighted discipline scoring;
- persisted `SessionSummary`;
- trade review digest beyond current bounded projection;
- series or cross-session outputs;
- mentor-facing review digest;
- mobile review surface;
- sync-safe derived cache;
- any auto-generated behavioral or Bill Williams assessment.

## Risks / Boundary Protections

Главные риски этого шага:

- silently turning read projection into new persistence layer;
- dragging analytics metrics into a slice that only needs bounded result projection;
- duplicating trade facts already owned by `TradeRecord`;
- making desktop the owner of derived output;
- mixing manual persisted findings with future derived detection logic.

Boundary protections:

- trade facts still come only from `DATA_SCHEMA.md` entities;
- journal facts still come only from `JOURNAL_SCHEMA.md` entities;
- derived output remains recomputable and disposable;
- desktop only reads this output;
- anything like `SessionSummary`, scoring, dashboards or multi-session analytics requires a separate later slice.
