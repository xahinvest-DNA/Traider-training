# Partial Close

Date fixed: 2026-04-05
Status: implementation boundary v1
Priority: current

## Purpose and Scope

`PARTIAL_CLOSE.md` fixes one bounded next frontier after Pending Stop Entry.

The purpose of this slice is:

- strengthen the live desktop trading loop by letting the user realize part of an open position instead of forcing only full manual close after entry;
- expose already accepted partial-close behavior from the trading contract as a real product capability inside the current one-trade local desktop workflow;
- improve training value by making trade management more realistic without expanding into a broader order-management or risk-engine subsystem;
- open a new productive lane after pending stop entry because it changes what the user can do while the trade is active, not just how the trade is staged before entry.

This document does not change source-of-truth ownership in `03_MODULES/TRADING_ENGINE.md`, `03_MODULES/DESKTOP_WORKSPACE.md`, `04_TECH/DATA_SCHEMA.md`, or `04_TECH/JOURNAL_SCHEMA.md`.

## Why this Slice is Next

This slice is next because:

- bounded pending stop entry already solved the strongest trigger-based entry gap in the live loop;
- the current product still collapses active-trade management to hold-until-full-close behavior even though accepted trading contracts already include partial close semantics;
- this creates a stronger user-visible gain than more pending-order handling because it expands how the user can manage an already opened trade;
- the required ownership already exists in `Order`, `Position`, `TradeRecord`, `ExecutionRecord`, and desktop trading surfaces, so the product can move forward without new persistence or a hidden subsystem.

## Preconditions / Dependencies

This slice depends on already working layers:

- one active trade lifecycle;
- existing `Order` / `Position` / `TradeRecord` / `ExecutionRecord` ownership and persistence;
- current desktop trading/context/result/workflow surfaces;
- bounded Initial Trade Protection already implemented;
- bounded Current Trade Plan Context already implemented;
- bounded Pending Stop Entry already implemented.

## In-Scope Behavior

This slice includes:

- one bounded manual partial-close path for the current open trade;
- reduction of `currentOpenVolume` without creating a second independent trade;
- visible partial-close result on existing trading/context/result/workflow surfaces where needed;
- correct realized-vs-remaining position state through the accepted execution contract;
- restart recovery of the same partially closed active trade state or later final trade result from existing trade/order/execution facts.

## Explicit Out-of-Scope

This slice does not include:

- add-on expansion;
- advanced scale-out ladders;
- partial-close templates or presets;
- trailing stops, break-even automation, or richer protection edits;
- pending-order expiry, OCO, bracket logic, or multiple concurrent pending orders;
- mentor advice, checklist logic, acknowledgment flow, or workflow-engine behavior;
- dashboard, mobile, sync, media, or new persistence.

## Runtime Contract

Runtime contract for this slice:

- `Order`, `Position`, `TradeRecord`, and `ExecutionRecord` remain the source of truth for partial-close intent and execution;
- partial close must stay inside the already accepted trading/storage contracts;
- no new persisted summary, queue, scheduler, or orchestration state is introduced;
- execution remains post-tick and replay-driven if the accepted manual-close contract still uses the next available snapshot.

## Minimum Partial-Close Contract

Minimum product-visible output may expose only what existing surfaces need, such as:

- partial close available / unavailable;
- requested close volume;
- remaining open volume;
- execution result for the partial close;
- updated realized PnL and remaining active-trade state where already supported by existing surfaces.

The slice must stay operational and factual. It should not become a broader position-management subsystem.

## Desktop-Facing Needs

Desktop can use this slice to:

- let the user reduce an open position without forcing a full close;
- make the replay trading loop closer to the accepted trading model already fixed in `TRADING_ENGINE.md` and `DESKTOP_WORKSPACE.md`;
- keep partial-close state visible without creating a new desktop subsystem;
- improve live trade management value without reopening mentor logic or analytics drift.

Desktop remains a projection consumer and command initiator only.

## Persistence Expectations

Persistence expectations remain strict:

- no new entities are introduced;
- existing order/position/trade/execution facts remain the only source of truth;
- restart recovery rebuilds the same partial-close state or later final result from the same local facts;
- no separate scale-out history subsystem or orchestration state is added beyond already accepted trace entities.

## Acceptance Scenario

1. User starts a local desktop training session.
2. User opens one trade.
3. User requests one bounded partial close of part of the open volume.
4. Existing trading/context/result/workflow surfaces show the updated remaining open volume and partial-close result.
5. Replay continues.
6. User can still manage the remaining position within the accepted one-trade lifecycle.
7. User restarts the app during the partially closed active trade or after the later full close.
8. Runtime rebuilds the same partial-close state or later final trade result from existing local facts.

## Acceptance Criteria

This slice is accepted if:

- the current desktop-first/local-first product supports one bounded partial-close path inside the accepted one-trade lifecycle;
- the live trade loop becomes meaningfully stronger because the user can manage an open trade beyond all-or-nothing close behavior;
- existing trading/context/result/workflow surfaces carry the partial-close state without a new subsystem;
- restart recovery restores the same partially closed active-trade state or later final result from existing local facts only;
- no new persistence entity, queue/orchestration engine, mentor layer, dashboard, mobile/sync path, or hidden architecture rewrite is introduced.

## Non-Goals / Deferred Items

Deferred for later steps:

- add-on entry;
- multi-step scale-out ladders;
- preset close fractions;
- auto-protection adjustments after partial close;
- advanced trade-management coaching or scoring.

## Risks / Boundary Protections

Main risks:

- turning partial close into a broader position-management subsystem;
- coupling partial close with add-on, protection automation, or preset ladders in the same slice;
- creating a desktop workflow-owner layer instead of a thin projection/command path.

Boundary protections:

- one bounded partial-close slice only;
- reuse existing `Order` / `Position` / `TradeRecord` / `ExecutionRecord` ownership only;
- no new persistence;
- no scale-out ladders, no add-on coupling, no automation, no mentor layer;
- anything beyond one bounded manual partial-close path requires a separate later slice.
