# Session Timeline Projection

Дата фиксации: 2026-03-19
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`SESSION_TIMELINE_PROJECTION.md` фиксирует bounded slice для unified local session timeline / review timeline projection поверх already working replay, trading, journal, derived review output and session result metrics.

Цель шага:

- дать one-session derived timeline over persisted trade and journal facts;
- связать pre-trade note, trade open/close, execution trace, post-trade review, behavioral flags and rule violations в один local read model;
- не вводить новый persisted timeline layer, cache or dashboard platform;
- закрыть desktop need на bounded review chronology inside current local-first workflow.

Документ не меняет source-of-truth contracts `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md` и `DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Этот шаг логичен сразу после session result metrics, потому что:

- текущий runtime уже умеет показывать trade result и session totals;
- `JOURNAL_SCHEMA.md` и `DATA_SCHEMA.md` уже требуют reconstructable timeline semantics;
- desktop surface нуждается не только в counters, но и в связной хронологии review;
- timeline projection можно дать без analytics cache and without new primary persistence.

## Preconditions / Dependencies

Слайс опирается на уже working and accepted dependencies:

- `TrainingSession` как session source of truth;
- `TradeRecord` and `ExecutionRecord` как trade timeline facts;
- `PreTradeNote`, `PostTradeReview`, `BehavioralFlag`, `RuleViolation` как journal timeline facts;
- `DERIVED_REVIEW_OUTPUT.md` и `SESSION_RESULT_METRICS.md` как already working derived read layers;
- local recovery of trade and journal source facts after restart.

## In-Scope Behavior

В этот slice входит:

- unified local timeline projection for current `TrainingSession`;
- inclusion of session start event, trade open/close events, execution events, notes, reviews, behavioral flags and rule violations;
- deterministic timeline ordering by timestamp, execution tick index and stable ID tie-break where needed;
- minimum event payloads needed for bounded desktop review chronology;
- rebuild of the same timeline after local restart from persisted source facts;
- desktop-facing access to this timeline through existing journal projection.

## Explicit Out-of-Scope

В этот slice не входит:

- persisted session timeline cache;
- multi-session history shell;
- dashboards;
- mentor workflow;
- media management;
- chart snapshot projection;
- advanced analytics overlays;
- editing workflow for timeline rows;
- sync;
- mobile;
- any change to trade execution logic.

## Runtime Contract

Timeline projection reads only from already available source-of-truth entities:

- `TrainingSession`
- `TradeRecord`
- `ExecutionRecord`
- `PreTradeNote`
- `PostTradeReview`
- `BehavioralFlag`
- `RuleViolation`

Runtime contract for this slice:

- timeline remains derived-only;
- timeline is recomputable at any moment from current source facts;
- timeline is exposed through desktop-facing journal projection;
- no new stored timeline entity is created.

## Minimum Timeline Item Contract

Every derived timeline item may expose at least:

- `timelineId`
- `eventType`
- `sessionId`
- `tradeId optional`
- `executionId optional`
- `timestamp`
- `snapshotTickIndex optional`
- `title`
- bounded event payload

Supported minimum event families in this slice:

- `session_started`
- `pre_trade_note`
- `trade_opened`
- `execution`
- `trade_closed`
- `post_trade_review`
- `behavioral_flag`
- `rule_violation`

## Ordering Contract

Timeline ordering must remain deterministic:

- primary order by event timestamp;
- execution items use `snapshotTickIndex` when available;
- event-type rank resolves same-timestamp collisions for non-execution items;
- stable derived ID remains the final tie-breaker.

The goal is not to perfectly emulate a future forensic event store, but to provide one reproducible local review chronology.

## Desktop-Facing Needs

Desktop can use this slice to:

- show session chronology after one or more trades;
- navigate from pre-trade note to trade outcome and review markers;
- show bounded review flow in order without building a dashboard or audit console;
- restore the same chronology after restart.

Desktop still only reads this projection.

## Persistence Expectations

Persistence expectations remain strict:

- no timeline file, table or cache is created;
- source facts stay in trade and journal storage only;
- derived timeline rebuilds after restart from restored local facts;
- any later persisted timeline cache would require a separate slice.

## Acceptance Scenario

1. User starts a local training session.
2. Creates a `PreTradeNote`.
3. Opens and closes a trade.
4. Runtime persists `TradeRecord` / `ExecutionRecord`.
5. User creates `PostTradeReview`, `BehavioralFlag` and `RuleViolation`.
6. Desktop reads unified local session timeline.
7. User sees the chronology from note to trade to review findings.
8. User restarts the app.
9. Runtime restores source facts.
10. The same bounded session timeline is rebuilt locally.

## Acceptance Criteria

Слайс считается принятым, если:

- timeline is derived only from existing source facts;
- timeline contains at least session start, notes, trade open/close, executions, reviews, flags and violations when present;
- ordering is deterministic and stable across restart;
- desktop-facing journal projection exposes this timeline;
- no new persistence layer, cache or dashboard is introduced;
- implementation does not expand into mentor, sync, media or multi-session navigation.

## Non-Goals / Deferred Items

Отложено на later steps:

- `ChartSnapshot` timeline integration;
- timeline filters and search;
- multi-session timeline browser;
- mentor annotations;
- persisted timeline cache;
- analytics overlays on timeline;
- media preview system.

## Risks / Boundary Protections

Главные риски:

- silently turning timeline projection into a stored entity;
- over-expanding payloads until timeline becomes a dashboard/reporting layer;
- duplicating source facts instead of referencing trade/journal entities;
- mixing current local session chronology with later multi-session history.

Boundary protections:

- timeline remains one-session and derived-only;
- payloads stay bounded and reconstructable;
- source facts remain owned by `DATA_SCHEMA.md` and `JOURNAL_SCHEMA.md`;
- any persisted cache or multi-session shell requires a separate later slice.
