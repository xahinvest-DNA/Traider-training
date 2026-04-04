# Desktop Current Session History Result Refinement

Дата фиксации: 2026-03-30
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`DESKTOP_CURRENT_SESSION_HISTORY_RESULT_REFINEMENT.md` фиксирует bounded slice для улучшения readability current-session history and latest result access inside already working desktop shell.

Цель шага:

- сделать latest trade review result and current-session timeline easier to inspect in the shell;
- сохранить current-session scope only;
- использовать only existing `derived_review_output` and `session_timeline` projections;
- не превращать shell в dashboard, archive browser или multi-session analytics center.

Документ не меняет source-of-truth boundaries `DERIVED_REVIEW_OUTPUT.md`, `SESSION_TIMELINE_PROJECTION.md`, `DESKTOP_WORKSPACE.md` и already accepted desktop shell slices.

## Why this Slice is Next

Этот шаг логичен сейчас, потому что:

- latest result and session timeline already exist as derived outputs;
- shell already has replay, context and authoring refinements;
- next usability gain comes from making current-session result/history easier to inspect than raw JSON alone;
- это можно сделать узко и projection-driven without new persistence.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- current desktop shell controller and Tk shell;
- current journal desktop projection;
- existing `derived_review_output`;
- existing `session_timeline`;
- current accepted one-session local-first workflow and recovery behavior.

## In-Scope Behavior

В этот slice входит:

- bounded readability refinement for current-session history/result only;
- compact latest trade result highlights from `derived_review_output.latestTradeResult`;
- compact current-session timeline preview from `session_timeline.timelineItems`;
- helper/model code for presentational mapping that remains testable outside GUI runtime;
- preserving raw JSON/detail views as secondary diagnostics.

## Explicit Out-of-Scope

В этот slice не входит:

- multi-session history;
- archive browser;
- dashboard metrics board;
- filters/search over full timeline;
- result scoring system;
- analytics expansion;
- new persistence or cache.

## Projection Boundary

This refinement must consume only existing projection inputs such as:

- `derived_review_output.latest_trade_result`
- `derived_review_output.trade_results`
- `session_timeline.timeline_items`
- bounded summary fields already exposed by journal projection

It must not rebuild trade or review facts independently.

## Minimum Readability Contract

Refined history/result surface may expose only:

- compact latest result block;
- compact timeline preview of current session;
- optional counts/status lines for current session history readiness;
- no more than what is needed for one current local session.

## Testability Contract

Any new history/result formatting logic introduced in this slice should stay in helper/model functions that can be tested without GUI runtime.

GUI remains thin.

## Acceptance Scenario

1. User starts current desktop shell.
2. Opens and closes a trade and creates review context.
3. Shell shows latest result in compact readable form.
4. Shell shows a compact preview of current session chronology.
5. User restarts the app.
6. The same current-session result/history view is rebuilt from recovered projections.

## Acceptance Criteria

Слайс считается принятым, если:

- a bounded history/result refinement document exists;
- current desktop shell shows latest result and current-session timeline in more readable form than raw JSON alone;
- only existing derived projections are consumed;
- helper/model logic is testable outside GUI runtime;
- no dashboard expansion, archive browsing, multi-session history or new persistence is introduced.

## Non-Goals / Deferred Items

Отложено на later steps:

- archive browser;
- timeline filters and search;
- result scoring board;
- multi-session comparison;
- dashboard widgets;
- timeline editing tools.

## Risks / Boundary Protections

Главные риски:

- silently turning current-session history into archive shell;
- overloading shell with analytics presentation;
- duplicating derived logic in UI;
- using result readability as excuse for dashboard growth.

Boundary protections:

- scope stays current-session only;
- history/result remains projection-driven and lightweight;
- raw diagnostics stay available separately;
- anything beyond bounded readability requires a separate later slice.
