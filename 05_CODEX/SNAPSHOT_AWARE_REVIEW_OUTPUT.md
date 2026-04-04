# Snapshot-Aware Review Output

Дата фиксации: 2026-03-30
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`SNAPSHOT_AWARE_REVIEW_OUTPUT.md` фиксирует bounded slice для minimum snapshot-aware exposure inside already working derived review output.

Цель шага:

- показать linked `ChartSnapshot` context прямо внутри derived trade review result;
- сохранить review output derive-on-read поверх existing trade and journal facts;
- не дублировать timeline и не запускать gallery/media workflow;
- дать desktop minimum review context around latest note/review without introducing new primary entities.

Документ не меняет source-of-truth boundaries `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md` и `DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Этот шаг логичен сразу после snapshot timeline exposure, потому что:

- snapshot refs уже persistятся и видны в timeline;
- derived review output уже существует как bounded result surface;
- desktop нужно видеть chart context не только в chronology, но и в trade result/review summary;
- это можно сделать без new analytics cache, media preview or timeline duplication.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- `ChartSnapshot` как persisted journal entity;
- `PreTradeNote` and `PostTradeReview` with snapshot refs;
- existing derived review output over closed trades;
- existing session timeline exposure for snapshots;
- local restart recovery of trade and journal source facts.

## In-Scope Behavior

В этот slice входит:

- minimum snapshot-aware fields inside derived trade review result;
- resolution of latest linked pre-trade snapshot from latest linked `PreTradeNote`;
- resolution of linked review snapshots from latest linked `PostTradeReview`;
- bounded snapshot summary fields only where strictly needed for current trade review output;
- optional session-level count of trades that already have linked snapshot context;
- rebuild of the same snapshot-aware review output after local restart;
- desktop-facing access through existing journal/review projection only.

## Explicit Out-of-Scope

В этот slice не входит:

- image preview rendering;
- gallery UI;
- file existence validation;
- media cache or thumbnail generation;
- annotation editor;
- sync-safe media transport;
- binary/media management;
- new analytics persistence;
- dashboard expansion.

## Runtime Contract

Runtime contract for this slice:

- review output remains derived-only;
- snapshot summaries are resolved only from existing `ChartSnapshot` records by stored refs;
- latest note/review continue to own which snapshot refs are relevant;
- no new persisted review summary, snapshot index or media manifest is introduced.

## Derived Trade Result Snapshot Contract

Minimum snapshot-aware trade result may expose:

- `hasLinkedChartSnapshots`
- `linkedChartSnapshotCount`
- `linkedChartSnapshotIds[]`
- `latestPreTradeNoteSnapshot optional`
- `latestPostTradeReviewSnapshots[]`

Bounded snapshot summary may expose only:

- `snapshotId`
- `artifactType`
- `artifactRef`
- `snapshotRole`
- `timeframeContext`
- optional `tradeId`
- optional `executionId`

This slice does not expose binary content, preview metadata or filesystem checks.

## Session-Level Minimum Extension

Session-level derived output may additionally expose only:

- `tradesWithLinkedChartSnapshotsCount`

Это остается lightweight read-model counter, а не analytics subsystem.

## Desktop-Facing Needs

Desktop can use this slice to:

- show that latest reviewed trade has chart context;
- display note/review snapshot refs near the derived trade result;
- avoid forcing the user to switch into full timeline just to confirm chart evidence exists;
- restore the same snapshot-aware result summary after restart.

Desktop still reads only derived output.

## Persistence Expectations

Persistence expectations remain strict:

- `ChartSnapshot`, `PreTradeNote`, `PostTradeReview` stay the only persisted source facts involved;
- snapshot-aware review output is rebuilt from restored local state;
- no additional persisted summary layer or cache is introduced;
- any later manifest, preview cache or gallery state requires a separate slice.

## Acceptance Scenario

1. User starts a local training session.
2. Creates a pre-entry `ChartSnapshot` and links it from `PreTradeNote`.
3. Opens and closes a trade.
4. Creates a review `ChartSnapshot` and links it from `PostTradeReview`.
5. Desktop reads `derived_review_output`.
6. User sees trade result together with bounded linked snapshot summaries.
7. User restarts the app.
8. Runtime restores source facts and rebuilds the same snapshot-aware review output.

## Acceptance Criteria

Слайс считается принятым, если:

- derived review output exposes bounded linked snapshot context for reviewed trades when refs exist;
- snapshot-aware fields are resolved only from existing persisted refs;
- restart recovery rebuilds the same snapshot-aware output;
- desktop-facing journal projection returns the enriched derived output;
- no gallery, media cache, preview renderer, sync or new analytics persistence is introduced.

## Non-Goals / Deferred Items

Отложено на later steps:

- image preview UI;
- media validation and repair;
- annotation workflows;
- gallery browsing;
- snapshot filters and search;
- multi-session artifact library;
- mentor/media review workspace.

## Risks / Boundary Protections

Главные риски:

- over-expanding trade result payload into media metadata layer;
- duplicating timeline responsibilities inside review output;
- turning snapshot-aware review output into a persisted summary entity;
- dragging gallery/media concerns into a bounded review slice.

Boundary protections:

- review output remains derive-on-read only;
- snapshot summaries stay minimal and reference-oriented;
- timeline remains separate from trade result summary;
- anything beyond bounded snapshot context requires a separate later slice.
