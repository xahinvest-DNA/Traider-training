# Desktop Shell Implementation

Дата фиксации: 2026-03-30
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`DESKTOP_SHELL_IMPLEMENTATION.md` фиксирует bounded implementation-facing boundary для первого desktop shell поверх уже accepted local-first runtime.

Цель шага:

- подключить existing replay/trading/journal projections к реальному desktop operating surface;
- сохранить desktop как projection consumer, а не новый domain owner;
- перевести accepted MVP workflow в usable desktop shell без dashboard expansion и без пересборки runtime contracts;
- определить минимальный integration path before actual UI coding begins.

Документ не меняет source-of-truth boundaries `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md`, `DESKTOP_WORKSPACE.md` и не пересматривает already accepted runtime slices.

## Why this Slice is Next

Этот шаг логичен сразу после MVP acceptance pass, потому что:

- headless runtime уже проходит bounded MVP scenario end-to-end;
- current gap теперь не в domain logic, а в отсутствии real desktop operating shell;
- `DESKTOP_WORKSPACE.md` уже определяет desktop as primary MVP surface, но implementation-facing binding к текущим projections еще не зафиксирован;
- это можно сделать узко, не начиная premature UI redesign or framework sprawl.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- accepted replay bootstrap runtime;
- accepted minimal one-trade runtime;
- accepted local-first journal/review loop;
- accepted Bill Williams review hooks, flags/violations, timeline, snapshot-aware review output, finalization and compact session review summary;
- accepted MVP e2e scenario from `MVP_ACCEPTANCE_PASS.md`;
- current desktop operating responsibilities already fixed in `DESKTOP_WORKSPACE.md`.

## In-Scope Behavior

В этот slice входит:

- binding current runtime projections into one desktop shell composition boundary;
- minimum desktop shell responsibilities for session bootstrap, replay controls, trading actions, note/review entry points and result display;
- explicit mapping between desktop surfaces and existing runtime projection methods;
- bounded action flow for the accepted MVP scenario only;
- clear ownership split between desktop shell and runtime services;
- minimum recovery/resume expectations for desktop startup.

## Explicit Out-of-Scope

В этот slice не входит:

- visual design system finalization;
- polished UI/UX layer;
- dashboard workspace;
- mentor workflow;
- mobile surface;
- sync;
- new analytics cache;
- new trading logic;
- replay redesign;
- multi-session shell.

## Runtime Ownership Boundary

Desktop shell in this slice:

- reads replay state only through `build_desktop_replay_view(...)`;
- reads trading state only through `build_desktop_trading_view(...)`;
- reads journal/review state only through `build_desktop_journal_view(...)`;
- invokes runtime actions through existing runtime objects and methods;
- does not recompute domain state independently;
- does not persist alternative copies of trade/session/review facts.

Runtime remains owner of:

- replay progression;
- trading lifecycle;
- local persistence;
- note/review linkage;
- finalization state;
- derived review/session outputs.

## Minimum Desktop Shell Composition

First desktop shell may remain a single-window bounded composition with these surfaces only:

- `Chart / Replay Surface`
- `Trading Control Surface`
- `Session / Trade Context Surface`
- `Notes / Review Surface`
- `Basic Result Surface`

No docking system, workspace presets, dashboard tabs or multi-session browser is required in this slice.

## Projection Mapping Contract

Desktop shell should bind surfaces to current runtime projections as follows:

### Chart / Replay Surface

Reads from `build_desktop_replay_view(...)` at minimum:

- `dataset_id`
- `instrument_id`
- `market_profile`
- `replay_mode`
- `active_timeframe`
- `synchronized_timeframes`
- `simulation_time`
- `time_cursor`
- `speed_multiplier`
- `is_paused`
- `is_finished`
- `allowed_controls`
- `chart_context`
- `status`

Initiates only:

- play
- pause
- speed change
- allowed seek/jump
- timeframe switch

### Trading Control Surface

Reads from `build_desktop_trading_view(...)` at minimum:

- active trade presence
- lifecycle/trade status
- current side and volume
- last execution outcome
- manual close availability
- session context

Initiates only:

- `buy_market(...)`
- `sell_market(...)`
- `manual_close(...)`
- any already accepted minimal trading action if it already exists in runtime contract

### Session / Trade Context Surface

Reads from journal and trading projections at minimum:

- `session_id`
- `session_status`
- `mode`
- `dataset_id`
- `instrument_id`
- `active_timeframe`
- `review_pending_trade_id`
- `recovered`
- `session_finalization`

This surface may expose recovery/finalization readiness but must not own session workflow rules.

### Notes / Review Surface

Reads from `build_desktop_journal_view(...)` at minimum:

- last note/review state
- counts of notes/reviews/flags/violations
- current pending review context
- timeline when needed for current session context only

Initiates only:

- `create_pre_trade_note(...)`
- `create_post_trade_review(...)`
- `create_behavioral_flag(...)`
- `create_rule_violation(...)`
- `create_chart_snapshot(...)` where already accepted by runtime

### Basic Result Surface

Reads from `build_desktop_journal_view(...)` at minimum:

- `derived_review_output`
- `session_review_summary`
- `session_finalization`

This surface is bounded to current trade/session outcome and must not become dashboard or multi-session analytics shell.

## Desktop Startup / Recovery Contract

Desktop shell startup in this slice may do only:

1. create/load replay session;
2. create/load trading runtime;
3. create/load local journal runtime over the same storage root;
4. read current projections;
5. render resumed or fresh session state.

If local state already exists, desktop may show recovered current session directly.

This slice does not introduce:

- session picker;
- archive browser;
- merge/reconciliation flow;
- cloud recovery logic.

## Accepted User Flow in Desktop Shell

Desktop shell implementation for this slice must support only the already accepted MVP path:

1. open normalized dataset;
2. see paused replay state;
3. create optional `PreTradeNote`;
4. open one manual trade;
5. manage and close it;
6. create bounded post-trade review and optional markers;
7. see compact result/review summary;
8. finalize session when ready;
9. restart and recover the same current session state.

Anything beyond this path requires a separate later slice.

## Persistence Expectations

Persistence expectations remain strict:

- desktop shell uses existing local runtime persistence only;
- desktop shell must not create separate UI-owned state files for trade/session truth;
- UI-local ephemeral state is allowed only for view concerns and must be disposable;
- all recoverable business state must still come from runtime persistence.

## Acceptance Scenario

1. User starts desktop shell.
2. Desktop creates current runtime stack over one storage root.
3. User sees replay, trading, note/review and result surfaces backed by current projections.
4. User completes the already accepted MVP workflow.
5. Desktop updates from runtime projections after each action.
6. User closes and reopens the desktop shell.
7. Desktop restores the same current local session via runtime recovery and renders the same bounded workflow state.

## Acceptance Criteria

Слайс считается принятым, если:

- a dedicated desktop shell implementation boundary document exists;
- desktop shell responsibilities are mapped to existing runtime projections explicitly;
- desktop shell is defined as projection consumer, not domain owner;
- startup/recovery flow is defined for one current local session;
- accepted MVP workflow is preserved without dashboard or multi-session expansion;
- the slice does not introduce new domain logic, new persistence ownership or UI-driven source facts.

## Non-Goals / Deferred Items

Отложено на later steps:

- framework-specific UI architecture decisions beyond what is strictly needed;
- rich chart rendering decisions;
- workspace presets and docking;
- session archive browser;
- dashboard tabs;
- mentor overlays;
- mobile companion;
- sync-aware desktop continuity.

## Risks / Boundary Protections

Главные риски:

- letting desktop shell silently become a new domain layer;
- introducing duplicated state stores in UI layer;
- treating desktop shell as excuse for dashboard expansion;
- skipping implementation boundary and jumping straight into large UI code.

Boundary protections:

- desktop shell reads current projections instead of rebuilding domain truth;
- scope stays one-session, MVP-only and runtime-backed;
- all business persistence remains in runtime layer;
- any richer desktop UX or later-phase surface requires a separate slice.
