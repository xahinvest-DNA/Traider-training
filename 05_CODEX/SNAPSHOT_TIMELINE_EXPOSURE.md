# Snapshot Timeline Exposure

Дата фиксации: 2026-03-19
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`SNAPSHOT_TIMELINE_EXPOSURE.md` фиксирует bounded slice для minimum timeline exposure of linked `ChartSnapshot` references inside already working local session timeline.

Цель шага:

- вывести snapshot references в existing one-session timeline без запуска gallery or media workspace;
- дать desktop minimum visibility of chart context around `PreTradeNote` and `PostTradeReview`;
- сохранить timeline as derive-on-read layer over already persisted journal entities;
- не превращать snapshot refs в новый media subsystem, annotation engine or transport layer.

Документ не меняет source-of-truth boundaries `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md` и `DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Этот шаг логичен сразу после minimum `ChartSnapshot` references, потому что:

- snapshot refs уже persist and recover locally;
- desktop session timeline уже существует как bounded chronology;
- note/review flow теперь нуждается в minimum visibility of linked chart context;
- это можно закрыть через derived projection без нового persistence or media UX layer.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- `TrainingSession` as current local session owner;
- `ChartSnapshot` as persisted journal entity;
- `PreTradeNote` and `PostTradeReview` with bounded snapshot refs;
- existing session timeline projection;
- local restart recovery of journal and trade facts.

## In-Scope Behavior

В этот slice входит:

- inclusion of `chart_snapshot` events in current session timeline when snapshots exist;
- exposure of bounded snapshot summaries inside linked `PreTradeNote` timeline items;
- exposure of bounded snapshot summaries inside linked `PostTradeReview` timeline items;
- deterministic ordering of snapshot timeline items alongside existing session chronology;
- rebuild of the same snapshot-aware timeline after local restart;
- desktop-facing access through existing journal projection only.

## Explicit Out-of-Scope

В этот slice не входит:

- image preview rendering;
- gallery browser;
- annotation editor;
- screenshot automation;
- binary/media file management;
- file existence validation;
- sync-safe media transport;
- multi-session media history;
- mentor/media workflow.

## Runtime Contract

Runtime contract for this slice:

- timeline remains derived-only and one-session scoped;
- snapshot data in timeline is always read from existing `ChartSnapshot` records;
- note/review timeline payloads expose bounded linked snapshot summaries only;
- no new persisted timeline entity, media cache or manifest is introduced.

## Minimum Timeline Exposure Contract

Minimum `chart_snapshot` timeline item may expose:

- `timelineId`
- `eventType = chart_snapshot`
- `sessionId`
- optional `tradeId`
- optional `executionId`
- `timestamp`
- bounded payload with `snapshotId`, `artifactType`, `artifactRef`, `snapshotRole`, `timeframeContext`

Minimum note/review linked exposure may expose:

- original snapshot ref IDs already stored on the source entity;
- bounded linked snapshot summaries resolved by snapshot ID;
- boolean/count fields showing linked snapshot presence.

## Ordering Contract

Ordering remains bounded and deterministic:

- primary order by timestamp;
- existing `snapshotTickIndex` ordering for executions remains unchanged;
- `chart_snapshot` gets its own event rank for same-timestamp collisions;
- stable timeline IDs remain final tie-breaker.

This step is about readable chronology, not forensic media event sourcing.

## Desktop-Facing Needs

Desktop can use this slice to:

- show that chart context existed at note/review time;
- display artifact refs in session chronology without opening a gallery subsystem;
- keep note/review interpretation tied to the same local timeline;
- restore the same snapshot-aware timeline after restart.

Desktop still reads only the derived projection.

## Persistence Expectations

Persistence expectations remain strict:

- `ChartSnapshot` persistence stays owned by journal schema/runtime;
- timeline exposure adds no new stored data;
- restart recovery restores source facts first, then rebuilds timeline;
- any later manifest, preview cache or gallery index requires a separate slice.

## Acceptance Scenario

1. User starts a local training session.
2. Creates a `ChartSnapshot` before trade entry.
3. Links it from `PreTradeNote`.
4. Opens and closes a trade.
5. Creates another `ChartSnapshot` for review context.
6. Links it from `PostTradeReview`.
7. Desktop reads session timeline.
8. User sees snapshot events and linked snapshot refs in note/review timeline rows.
9. User restarts the app.
10. Runtime rebuilds the same snapshot-aware timeline from persisted journal facts.

## Acceptance Criteria

Слайс считается принятым, если:

- session timeline contains `chart_snapshot` items when snapshots exist;
- linked note/review timeline payloads expose bounded snapshot summaries by reference;
- ordering remains deterministic across restart;
- desktop-facing journal projection returns the snapshot-aware timeline;
- no gallery, preview renderer, sync or media cache is introduced.

## Non-Goals / Deferred Items

Отложено на later steps:

- image preview UI;
- snapshot gallery and filters;
- annotation workflows;
- file integrity checks;
- media sync and transport;
- multi-session artifact library;
- screenshot automation.

## Risks / Boundary Protections

Главные риски:

- silently turning timeline exposure into a media review workspace;
- over-expanding timeline payloads until they duplicate media metadata layers;
- introducing a hidden media cache or gallery index;
- mixing snapshot refs with trade/journal source ownership.

Boundary protections:

- timeline remains derive-on-read only;
- snapshot payloads stay bounded and reference-oriented;
- `ChartSnapshot` ownership remains in journal schema/runtime;
- anything beyond minimal timeline exposure requires a separate later slice.
