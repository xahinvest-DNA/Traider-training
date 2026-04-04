# Desktop Chart Replay Surface Refinement

Дата фиксации: 2026-03-30
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`DESKTOP_CHART_REPLAY_REFINEMENT.md` фиксирует bounded slice для улучшения current desktop chart/replay surface поверх уже working desktop shell.

Цель шага:

- сделать current chart/replay surface заметно более usable than raw JSON/text output;
- сохранить shell on the same replay projections and runtime contracts;
- дать minimum visual market trace and replay state cues without introducing heavy chart stack;
- не превратить refinement в charting platform, dashboard layer или replay redesign.

Документ не меняет source-of-truth boundaries `REPLAY_ENGINE.md`, `DESKTOP_WORKSPACE.md`, `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md` и already accepted desktop shell boundary.

## Why this Slice is Next

Этот шаг логичен сейчас, потому что:

- first desktop shell already exists and exercises the MVP workflow;
- current replay/chart area is still mostly raw text and JSON;
- fastest usability gain now comes from improving the replay surface, not from adding new domains or later-phase features;
- это можно сделать local-first и lightweight на standard library UI stack.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- accepted replay bootstrap runtime;
- accepted desktop shell controller;
- `build_desktop_replay_view(...)` and its `chart_context` payload;
- accepted desktop shell implementation boundary;
- current MVP workflow and restart recovery.

## In-Scope Behavior

В этот slice входит:

- bounded refinement of the current `Chart / Replay Surface` only;
- lightweight visual chart representation derived from `chart_context.recent_points`;
- replay header/status cues such as instrument, timeframe, simulation time and replay state;
- explicit mapping of current point history to a simple local chart canvas or equivalent lightweight surface;
- helper/model code for chart rendering that stays testable outside GUI runtime.

## Explicit Out-of-Scope

В этот slice не входит:

- candlestick engine;
- indicator overlays;
- zoom/pan subsystem;
- multi-timeframe chart workspace;
- chart annotation tools;
- external charting dependencies;
- dashboard widgets;
- replay contract changes;
- market calculations outside replay projection.

## Replay Projection Boundary

Refinement in this slice must consume only existing replay projection fields such as:

- `instrument_id`
- `active_timeframe`
- `simulation_time`
- `status`
- `allowed_controls`
- `chart_context.current_tick`
- `chart_context.recent_points`

This slice must not read raw dataset files directly and must not derive alternative replay truth.

## Minimum Visual Contract

Improved chart/replay surface may expose only:

- compact replay header with instrument/timeframe/mode/status;
- simple plotted line over recent mid-price points;
- optional current price marker;
- compact recent tick table or current tick summary;
- no more than what is strictly needed for MVP usability.

## Testability Contract

Any chart transformation logic introduced in this slice should be kept in lightweight helper/model functions that can be tested without GUI event loop.

This allows the slice to remain verifiable while keeping UI code thin.

## Desktop Boundary Protections

This refinement must not:

- create UI-owned business persistence;
- duplicate replay state machine logic;
- become a new analytics surface;
- force framework migration;
- drag the project into polished design work before MVP shell remains stable.

## Acceptance Scenario

1. User starts current desktop shell.
2. Replay/chart surface shows instrument, timeframe, simulation time and replay status.
3. User advances replay or plays it forward.
4. Chart surface visibly updates recent market trace from replay projection.
5. User continues the same MVP workflow without any change in domain behavior.
6. User restarts the app.
7. Desktop shell restores current session and the replay/chart surface renders recovered replay state again.

## Acceptance Criteria

Слайс считается принятым, если:

- a bounded refinement document exists for chart/replay surface only;
- current desktop shell shows a more usable replay/chart view than raw text alone;
- rendering uses only existing replay projections;
- helper/model logic is testable outside GUI runtime;
- no external chart stack, dashboard layer or replay contract change is introduced.

## Non-Goals / Deferred Items

Отложено на later steps:

- candlesticks and OHLC aggregation;
- indicator overlays;
- chart drawing tools;
- chart templates and layouts;
- multi-timeframe chart board;
- advanced chart UX and styling;
- chart snapshot authoring workspace.

## Risks / Boundary Protections

Главные риски:

- overbuilding chart UI too early;
- leaking replay calculations into desktop layer;
- introducing dependency or design sprawl for a bounded refinement;
- hiding MVP progress behind cosmetic work.

Boundary protections:

- only current replay surface is refined;
- chart stays projection-driven and lightweight;
- runtime and replay contracts remain unchanged;
- anything beyond minimum visual usability requires a separate later slice.
