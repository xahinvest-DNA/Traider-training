# Bill Williams Review Evidence Status

Дата фиксации: 2026-04-04
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_EVIDENCE_STATUS.md` фиксирует bounded slice для одного компактного evidence-status layer поверх уже работающего Bill Williams review и local `ChartSnapshot` flow.

Цель шага:

- показать, имеет ли текущая reviewed Bill Williams interpretation явную linked chart evidence;
- сделать это derive-on-read поверх уже существующих `PostTradeReview`, snapshot refs и current review output;
- вернуть snapshot authoring в реальную учебную ценность, а не в isolated reference feature;
- не превращать review flow в media workspace, mentor workflow, scoring model, dashboard layer или новую persistence subsystem.

Документ не меняет source-of-truth boundaries `04_TECH/JOURNAL_SCHEMA.md`, `03_MODULES/JOURNAL_ANALYTICS.md`, `03_MODULES/BILL_WILLIAMS_LAYER.md` и `03_MODULES/DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Этот шаг логичен сразу после desktop chart snapshot authoring, потому что:

- snapshot refs уже persistятся, восстанавливаются и доступны из desktop shell;
- review output уже умеет показывать linked snapshot context, но пока не связывает его с качеством Bill Williams review;
- текущий пользовательский friction point не в отсутствии еще одной snapshot surface, а в том, что reviewed method interpretation может выглядеть завершенной без явного evidence signal;
- это можно закрыть узко, без gallery/media scope, без новых entities и без продолжения symbolic label chains.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- structured `PostTradeReview` Bill Williams method facets;
- current derived review output and session review summary;
- local `ChartSnapshot` persistence and desktop authoring flow;
- snapshot-aware trade review output;
- current desktop result/history/context/workflow surfaces.

## In-Scope Behavior

В этот slice входит:

- one compact derive-on-read `bill_williams_review_evidence_status` for reviewed trades;
- evidence-status derivation only from already persisted review facts plus linked snapshot refs;
- bounded status text for latest/current trade review output;
- bounded current-session summary exposure showing how many reviewed trades already have linked chart evidence and how many do not;
- desktop-facing visibility through existing result/history/context/workflow summary surfaces only;
- rebuild of the same evidence status after local restart.

## Explicit Out-of-Scope

В этот slice не входит:

- screenshot automation;
- image preview rendering;
- gallery or media browser;
- file existence validation;
- annotation editing;
- mentor coaching logic;
- weighted review score;
- new persistence entities;
- multi-session evidence analytics;
- sync/mobile/dashboard expansion.

## Runtime Contract

Runtime contract for this slice:

- evidence status remains derive-on-read only;
- evidence status is computed from existing reviewed Bill Williams fields and linked snapshot refs only;
- linked snapshots remain context references, not proof of method correctness;
- absence of evidence is exposed as review-context incompleteness, not as execution-rule verdict or mentor score.

## Minimum Evidence Status Contract

Minimum trade-level evidence status may expose:

- `bill_williams_review_evidence_status`
- `bill_williams_review_evidence_text`
- `has_bill_williams_review_evidence`

Recommended bounded status values in this slice:

- `not_applicable`
- `linked_evidence_present`
- `linked_evidence_missing`
- `linked_evidence_partial`

Derivation rule for this slice:

- `not_applicable` when no meaningful Bill Williams reviewed interpretation exists yet;
- `linked_evidence_present` when reviewed Bill Williams interpretation exists and linked chart snapshot context is present;
- `linked_evidence_missing` when reviewed Bill Williams interpretation exists but no linked chart snapshot context exists;
- `linked_evidence_partial` when reviewed Bill Williams interpretation exists but only part of the expected note/review context is linked.

Session-level minimum extension may expose only:

- `reviewed_trades_with_bw_evidence_count`
- `reviewed_trades_missing_bw_evidence_count`

These remain lightweight current-session counters, not a scoring subsystem.

## Desktop-Facing Needs

Desktop can use this slice to:

- show when a reviewed Bill Williams interpretation is already backed by chart context;
- show when review is methodologically filled in but still missing linked chart evidence;
- make snapshot authoring feel productively connected to review quality instead of optional side metadata;
- keep the signal visible in current result/history/context/workflow surfaces without opening a media workspace.

Desktop still remains a projection consumer only.

## Persistence Expectations

Persistence expectations remain strict:

- no new source entities are introduced;
- no evidence cache or manifest is introduced;
- source facts remain `PostTradeReview`, `ChartSnapshot`, and existing snapshot refs;
- evidence status is rebuilt from restored local source facts after restart.

## Acceptance Scenario

1. User starts a local desktop training session.
2. Creates and links a `PreTradeNote` and/or `PostTradeReview` with Bill Williams review interpretation.
3. Trade is closed and current derived review output is available.
4. If linked chart snapshots exist, desktop review/result surfaces show reviewed interpretation as evidence-backed.
5. If Bill Williams review exists but linked chart evidence is absent, desktop review/result surfaces show that evidence is still missing.
6. User restarts the app.
7. Runtime restores source facts and rebuilds the same evidence-status output.

## Acceptance Criteria

Слайс считается принятым, если:

- current trade review output exposes one bounded Bill Williams review evidence status when review interpretation exists;
- current session summary exposes only lightweight evidence-present vs evidence-missing counts for reviewed trades;
- desktop surfaces can show the new evidence signal without new UI subsystems;
- restart recovery rebuilds the same evidence status from existing local facts;
- no gallery/media workflow, mentor logic, scoring, dashboard layer, sync/mobile continuity, or new persistence entity is introduced.

## Non-Goals / Deferred Items

Отложено на later steps:

- actual image preview;
- annotation workflows;
- filesystem validation and repair;
- evidence scoring or confidence ranking;
- mentor evidence review;
- multi-session evidence progress analytics;
- media library/search.

## Risks / Boundary Protections

Главные риски:

- silently turning evidence status into proof-of-correctness or mentor grading;
- over-expanding snapshot context into media-management scope;
- adding too many evidence-derived labels instead of one useful signal;
- drifting into multi-session evidence dashboards.

Boundary protections:

- one compact evidence-status layer only;
- derive-on-read only;
- current-session scope only;
- snapshot refs remain optional context, not method-validation authority;
- anything beyond bounded evidence visibility requires a separate later slice.
