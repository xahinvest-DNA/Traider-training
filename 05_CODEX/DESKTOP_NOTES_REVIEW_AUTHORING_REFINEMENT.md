# Desktop Notes Review Authoring Refinement

Дата фиксации: 2026-03-30
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`DESKTOP_NOTES_REVIEW_AUTHORING_REFINEMENT.md` фиксирует bounded slice для улучшения notes/review authoring usability внутри already working desktop shell.

Цель шага:

- сделать ввод `PreTradeNote` и `PostTradeReview` более понятным и менее сырым;
- сохранить authoring flow bounded and local-first over current runtime actions;
- использовать existing journal contracts and BW vocabularies without building rich authoring system;
- не превращать notes/review surface в mentor workspace, dashboard UI или long-form editor platform.

Документ не меняет source-of-truth boundaries `JOURNAL_SCHEMA.md`, `DESKTOP_WORKSPACE.md`, `JOURNAL_REVIEW_LOOP.md`, `SESSION_REVIEW_SUMMARY.md` и already accepted desktop shell slices.

## Why this Slice is Next

Этот шаг логичен сейчас, потому что:

- desktop shell already exposes note/review actions end-to-end;
- chart/replay and session/trade context readability are already improved;
- next best usability gain now comes from making note/review entry clearer and less raw;
- это можно сделать узко без изменения journal runtime contracts.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- accepted local-first journal runtime;
- accepted Bill Williams vocabularies and validation rules;
- current desktop shell controller actions for note/review/flag/violation creation;
- current journal projection including counts, pending review state and latest note/review context.

## In-Scope Behavior

В этот slice входит:

- bounded refinement of `Notes / Review Surface` only;
- clearer grouping of note and review authoring inputs;
- lightweight use of current BW vocabulary options in UI controls where helpful;
- compact authoring status/hints derived from current journal projection;
- better handling of multi-line note/review content entry;
- helper/model code for authoring hints that stays testable outside GUI runtime.

## Explicit Out-of-Scope

В этот slice не входит:

- rich text editing;
- markdown authoring;
- mentor comments;
- threaded review;
- media gallery authoring;
- multi-step review wizard;
- autosave draft persistence outside current runtime facts;
- dashboard-style review analytics.

## Journal Contract Boundary

This refinement must continue to invoke only existing runtime actions such as:

- `create_pre_trade_note(...)`
- `create_post_trade_review(...)`
- `create_behavioral_flag(...)`
- `create_rule_violation(...)`

It must not create alternative journal entities, draft stores or UI-owned business persistence.

## Minimum Authoring Refinement Contract

Refined note/review surface may include only:

- labeled note and review sections;
- multi-line content boxes for note/review body;
- bounded setup/compliance selectors using existing BW vocabularies where helpful;
- compact authoring status such as current pending review state and existing note/review counts;
- simple clear/reset behavior after successful submission.

## Testability Contract

Any new authoring hint, options or presentational mapping logic introduced in this slice should stay in helper/model functions that can be tested without GUI runtime.

GUI remains thin.

## Acceptance Scenario

1. User starts current desktop shell.
2. Notes/review surface shows compact authoring status for current session.
3. User enters a multi-line pre-trade note and saves it.
4. User closes a trade.
5. Surface now clearly indicates pending review context.
6. User enters a multi-line post-trade review and optional flag/violation using bounded vocabulary controls.
7. Desktop refreshes and shows updated current-session state.
8. User restarts the app and current journal state remains recoverable via existing runtime persistence.

## Acceptance Criteria

Слайс считается принятым, если:

- a bounded notes/review authoring refinement document exists;
- current desktop shell offers clearer note/review entry than raw single-line inputs alone;
- authoring still uses existing journal runtime actions only;
- helper/model logic for authoring hints or vocabulary options is testable outside GUI runtime;
- no rich authoring system, mentor workflow, dashboard layer or new persistence is introduced.

## Non-Goals / Deferred Items

Отложено на later steps:

- markdown/rich text editor;
- review templates library;
- mentor comment threads;
- media attachment workflow beyond current bounded hooks;
- draft autosave layer;
- structured coaching overlays.

## Risks / Boundary Protections

Главные риски:

- silently growing notes/review surface into a rich authoring subsystem;
- introducing UI-owned draft persistence;
- coupling desktop too tightly to BW taxonomy internals;
- mixing authoring refinement with mentor or dashboard concerns.

Boundary protections:

- authoring remains thin over existing runtime actions;
- only bounded current-session hints are shown;
- BW vocabularies remain optional assistive controls, not new source facts;
- anything beyond basic local authoring usability requires a separate later slice.
