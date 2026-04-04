# MVP Acceptance Pass

Дата фиксации: 2026-03-30
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`MVP_ACCEPTANCE_PASS.md` фиксирует bounded acceptance/hardening slice для already implemented local-first desktop workflow.

Цель шага:

- проверить, что текущий runtime реально закрывает MVP acceptance scenario end-to-end;
- собрать acceptance вокруг уже существующего сценария `dataset -> replay -> one trade -> review -> summary -> finalization -> restart recovery`;
- усилить verification and consistency там, где это нужно для first working prototype;
- не открыть новую волну feature growth под видом hardening.

Документ не меняет source-of-truth boundaries `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md` и `DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Этот шаг логичен сейчас, потому что:

- core replay, trading, journal, Bill Williams review, summary и finalization slices уже working;
- roadmap прямо требует `Phase 5 - MVP hardening / acceptance pass` после завершения core slices;
- MVP теперь нужно подтвердить сквозным acceptance path, а не только набором отдельных unit-like slices;
- это можно сделать без dashboards, mentor, mobile, sync или новых analytics surfaces.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- normalized dataset loading and replay bootstrap;
- minimal one-trade runtime with `TradeRecord` / `ExecutionRecord` persistence;
- local-first `TrainingSession` / `PreTradeNote` / `PostTradeReview` loop;
- Bill Williams structured review hooks;
- manual `BehavioralFlag` / `RuleViolation` capture;
- derived review output, session metrics, timeline, snapshot-aware review output, session review summary and session finalization;
- restart recovery across replay/trading/journal state.

## In-Scope Behavior

В этот slice входит:

- one explicit end-to-end MVP acceptance scenario over the existing local runtime;
- verification that replay, trading, journal, review, summary and finalization projections stay mutually consistent;
- verification that restart recovery preserves the same accepted session state;
- limited runtime hardening only if acceptance uncovers a consistency issue;
- explicit acceptance alignment with `PRODUCT_SCOPE.md`, `MVP_vs_FULL.md`, `ROADMAP.md` and `DESKTOP_WORKSPACE.md`.

## Explicit Out-of-Scope

В этот slice не входит:

- new trading logic;
- dashboard layer;
- mentor workflow;
- mobile surface;
- sync semantics;
- advanced analytics;
- new persistence schema;
- desktop redesign or UI system work.

## Acceptance Contract

This slice must validate at minimum that a single local user can:

1. select or load a normalized dataset;
2. start replay without future access;
3. create a bounded `PreTradeNote`;
4. open one manual trade;
5. close it and keep deterministic trade/execution trace;
6. add bounded `PostTradeReview` with Bill Williams structured fields;
7. see derived review/session summary output;
8. finalize the session explicitly;
9. restart the app and recover the same accepted local session state.

## Verification Focus

Verification for this slice must cover only:

- replay state continuity;
- one-trade lifecycle consistency;
- note/review linkage;
- Bill Williams field persistence;
- flags/violations persistence;
- snapshot-aware review context where already supported;
- compact summary consistency;
- finalization persistence and post-restart recovery.

## Runtime Hardening Expectations

Runtime hardening in this slice is intentionally narrow:

- fix only issues that break the acceptance scenario or make it inconsistent;
- prefer verification over expansion;
- do not add new product surfaces under the label of hardening;
- do not introduce cache, archive or dashboard read models.

## Desktop-Facing Boundary

Desktop-facing implication of this slice:

- current desktop contract is treated as accepted if the existing runtime projections already support the MVP scenario;
- acceptance is proven through current replay/trading/journal projections, not through a new desktop-specific storage layer;
- summary/finalization projections remain bounded operating surfaces, not dashboards.

## Persistence Expectations

Persistence expectations remain strict:

- acceptance uses existing local persistence only;
- no new acceptance artifact is persisted as source of truth;
- restart recovery must reconstruct the same accepted session state from existing primary facts and current derived projections.

## Acceptance Scenario

1. User opens a normalized dataset in training replay mode.
2. Sees paused replay state at the correct dataset start.
3. Creates a `PreTradeNote` and optional chart snapshot context.
4. Opens one manual trade.
5. Replay advances and the entry fills on the next tick.
6. User manually closes the trade.
7. Runtime persists `TradeRecord` and `ExecutionRecord` trace.
8. User creates `PostTradeReview`, optional flags/violations and optional review snapshot context.
9. Desktop projections show derived review output and compact session review summary.
10. User finalizes the session.
11. App restarts.
12. Runtime restores replay/trading/journal facts, finalization state and the same summary/review outputs.

## Acceptance Criteria

Слайс считается принятым, если:

- one explicit e2e acceptance test covers the bounded MVP workflow;
- current runtime passes that acceptance scenario locally;
- trade facts, journal facts, summary and finalization projections remain consistent before and after restart;
- no new feature surfaces are introduced during hardening;
- current implementation stays within MVP boundary from `PRODUCT_SCOPE.md` and `MVP_vs_FULL.md`.

## Non-Goals / Deferred Items

Отложено на later steps:

- UX polish beyond current runtime projections;
- desktop GUI implementation details;
- multi-session acceptance flows;
- mentor/mobile/sync validation;
- advanced acceptance packs for later-phase analytics and dashboards.

## Risks / Boundary Protections

Главные риски:

- masquerading feature expansion as acceptance hardening;
- writing acceptance-only state into persistence;
- using Phase 5 as justification for dashboards or rich summaries;
- blurring MVP verification with later-phase product planning.

Boundary protections:

- acceptance pass verifies only the already chosen MVP scenario;
- hardening is limited to issues that break that scenario;
- no new source-of-truth or cache layer is introduced;
- any post-MVP product expansion requires a separate later slice.
