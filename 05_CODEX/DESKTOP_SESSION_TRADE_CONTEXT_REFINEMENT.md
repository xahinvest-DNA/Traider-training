# Desktop Session Trade Context Refinement

Дата фиксации: 2026-03-30
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`DESKTOP_SESSION_TRADE_CONTEXT_REFINEMENT.md` фиксирует bounded slice для улучшения читаемости current session/trade context and basic result surface внутри already working desktop shell.

Цель шага:

- сделать current session state, trade state, review summary and finalization readiness easier to scan;
- сохранить result/context surface bounded and operational instead of turning it into dashboard UI;
- reuse only existing desktop journal/trading projections;
- improve desktop readability without introducing new persistence, analytics cache or domain logic.

Документ не меняет source-of-truth boundaries `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md`, `DESKTOP_WORKSPACE.md` и already accepted desktop shell slices.

## Why this Slice is Next

Этот шаг логичен сейчас, потому что:

- desktop shell and chart/replay surface already exist;
- current context/result area still relies heavily on raw JSON for scanning state;
- next best usability gain comes from summarizing current session/trade/review readiness in compact form;
- это можно сделать узко поверх existing projections without dashboard expansion.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- current desktop shell controller and Tk shell;
- current trading desktop projection;
- current journal desktop projection;
- existing `session_review_summary` and `session_finalization` outputs;
- existing accepted MVP flow and recovery behavior.

## In-Scope Behavior

В этот slice входит:

- bounded readability refinement of `Session / Trade Context Surface` and `Basic Result Surface` only;
- lightweight summary cards/sections for current session state, active trade state, review summary and finalization readiness;
- helper/model code that derives presentational context from existing projections only;
- keeping raw JSON/detail tabs available as secondary diagnostic views;
- reuse of the same current-session scope only.

## Explicit Out-of-Scope

В этот slice не входит:

- dashboard widgets;
- multi-session summaries;
- trend charts or analytics cards;
- new persistence;
- new domain events or calculations;
- mentor overlays;
- mobile layout;
- richer desktop architecture.

## Projection Consumption Boundary

This refinement must consume only existing projection inputs such as:

- trading desktop projection fields
- journal desktop projection fields
- `session_review_summary`
- `session_finalization`
- bounded latest trade result context already present in `derived_review_output`

It must not recalculate trade or session truth independently.

## Minimum Readability Contract

Refined context/result surface may expose only:

- compact current session block;
- compact active/current trade block;
- compact review summary block;
- compact finalization readiness block;
- optional latest result highlights for current local session.

These remain operational summaries, not analytics dashboard cards.

## Testability Contract

Any new summary formatting or card-building logic introduced in this slice should stay in helper/model functions that can be tested without GUI runtime.

GUI should remain thin.

## Acceptance Scenario

1. User starts current desktop shell.
2. Desktop shows current session identity and status in compact form.
3. User opens or closes a trade.
4. Desktop updates compact trade context and current result highlights.
5. User adds review and reaches review/finalization readiness.
6. Desktop shows review summary and finalization state in compact readable form.
7. User restarts the app.
8. Desktop restores the same session and context/result readability over recovered projections.

## Acceptance Criteria

Слайс считается принятым, если:

- a bounded context/result refinement document exists;
- current desktop shell shows compact readable session/trade/review/finalization context beyond raw JSON alone;
- helper/model logic is testable outside GUI runtime;
- only existing projections are consumed;
- no dashboard expansion, new persistence or domain logic change is introduced.

## Non-Goals / Deferred Items

Отложено на later steps:

- dashboard metrics board;
- multi-session result center;
- advanced trade history viewer;
- mentor review dashboard;
- scoring/ranking display;
- polished visual design system.

## Risks / Boundary Protections

Главные риски:

- accidentally turning readability improvements into dashboard subsystem;
- duplicating analytics logic in desktop layer;
- coupling UI formatting too tightly with domain internals;
- letting shell readability work sprawl into full redesign.

Boundary protections:

- context/result summaries remain current-session and projection-driven;
- helper layer stays presentation-only;
- raw JSON/detail views remain secondary diagnostics;
- anything beyond bounded readability requires a separate later slice.
