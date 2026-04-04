# Chart Snapshot References

Дата фиксации: 2026-03-19
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`CHART_SNAPSHOT_REFERENCES.md` фиксирует bounded slice для minimum local `ChartSnapshot` references in note/review context.

Цель шага:

- дать minimal persisted `ChartSnapshot` entity support where strictly needed for review context;
- позволить ссылаться на local artifact reference from `PreTradeNote` and `PostTradeReview`;
- не вводить heavy media management, gallery workflow, binary storage pipeline or sync layer;
- сохранить `ChartSnapshot` как context reference, а не как новый source of trade truth.

Документ не меняет existing source-of-truth boundaries `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md` и `DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Этот шаг логичен после session timeline projection, потому что:

- note/review loop уже работает end-to-end;
- session chronology уже есть, но ей не хватает minimum artifact references;
- `JOURNAL_SCHEMA.md` already includes `ChartSnapshot` as primary journal entity;
- можно закрыть это узко, не превращая slice в media subsystem.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- `TrainingSession` as session owner;
- `PreTradeNote` and `PostTradeReview` as existing note/review entities;
- local persistence and restart recovery already working in journal runtime;
- existing timeline and desktop projection layers already capable of reading bounded derived/journal state.

## In-Scope Behavior

В этот slice входит:

- local persisted `ChartSnapshot` reference entity in runtime;
- minimum fields: `snapshotId`, `sessionId`, `capturedAt`, `artifactType`, `artifactRef` and bounded optional context refs;
- creation of `ChartSnapshot` with optional `tradeId`, `executionId`, `simulationTime`, `timeframeContext`, `snapshotRole`;
- linking one `chartSnapshotRef` from `PreTradeNote`;
- linking bounded `chartSnapshotRefs[]` from `PostTradeReview`;
- desktop-facing visibility of chart snapshot presence/count and latest snapshot reference;
- local restart recovery of `ChartSnapshot` records and their links.

## Explicit Out-of-Scope

В этот slice не входит:

- binary image storage;
- screenshot capture automation;
- media gallery;
- editing/annotation system;
- cloud media sync;
- thumbnail generation;
- chart snapshot timeline rendering;
- mentor/media review workspace;
- validation of actual file existence on disk.

## Runtime Contract

Runtime contract for this slice:

- `ChartSnapshot` remains a local-first reference entity only;
- `artifactRef` is treated as a bounded local artifact reference string;
- note/review entities may reference snapshots by stable IDs;
- runtime persists and restores those references, but does not manage media assets themselves.

## Minimum ChartSnapshot Contract

Minimum runtime contract includes:

- `snapshotId`
- `sessionId`
- `capturedAt`
- `artifactType`
- `artifactRef`
- optional `tradeId`
- optional `executionId`
- optional `simulationTime`
- optional `timeframeContext`
- optional `instrumentId`
- optional `snapshotRole`
- optional `annotationRef`
- optional `createdAt`

Recommended bounded values in this slice:

- `artifactType = image_path` by default
- `snapshotRole = pre_entry_context | review_context`

## Note / Review Link Contract

In this slice:

- `PreTradeNote` may store one optional `chartSnapshotRef`;
- `PostTradeReview` may store bounded `chartSnapshotRefs[]`;
- these links are references only and do not duplicate trade facts or review text;
- linked snapshots remain valid without requiring any additional analytics layer.

## Desktop-Facing Needs

Desktop-facing journal projection may expose at minimum:

- `chartSnapshotCount`
- `hasChartSnapshots`
- `lastChartSnapshot`
- chart snapshot refs already linked from note/review entities

Desktop still does not manage files, preview generation or gallery UX in this slice.

## Persistence Expectations

Persistence expectations remain strict:

- `ChartSnapshot` persists as primary journal entity according to journal schema;
- no separate media manifest or cache layer is introduced;
- artifact refs are stored as bounded strings only;
- restart recovery must restore `ChartSnapshot` rows and note/review links.

## Acceptance Scenario

1. User starts a local training session.
2. Creates a `ChartSnapshot` reference for pre-entry context.
3. Links that snapshot to `PreTradeNote`.
4. Opens and closes a trade.
5. Creates another `ChartSnapshot` reference for review context.
6. Links it from `PostTradeReview`.
7. Desktop journal projection shows snapshot count and latest snapshot reference.
8. User restarts the app.
9. Runtime restores snapshots and their note/review links locally.

## Acceptance Criteria

Слайс считается принятым, если:

- `ChartSnapshot` persists locally as a bounded journal entity;
- `PreTradeNote` can reference one snapshot;
- `PostTradeReview` can reference one or more snapshot IDs;
- desktop-facing journal projection exposes snapshot presence/count;
- restart recovery restores snapshots and note/review links;
- implementation does not expand into screenshot automation, gallery, sync or media management.

## Non-Goals / Deferred Items

Отложено на later steps:

- actual screenshot capture;
- annotation editor;
- media manifest schema;
- file existence validation and repair;
- timeline integration of snapshots;
- gallery browsing;
- sync-safe asset transport.

## Risks / Boundary Protections

Главные риски:

- turning snapshot refs into a media subsystem too early;
- mixing snapshot references with trade source facts;
- requiring real files as a blocker for the local journal loop;
- introducing gallery UX or sync semantics prematurely.

Boundary protections:

- `artifactRef` stays a bounded string reference;
- no binary/media pipeline is introduced;
- snapshot links remain optional context only;
- anything beyond references requires a separate later slice.
