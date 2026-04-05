# Pending Stop Entry

Date fixed: 2026-04-05
Status: implementation boundary v1
Priority: current

## Purpose and Scope

`PENDING_STOP_ENTRY.md` fixes one bounded next frontier after Current Trade Plan Context.

The purpose of this slice is:

- strengthen the live desktop trading loop by letting the user stage one breakout-style or momentum-style entry before price reaches the trigger instead of forcing market-entry-only behavior;
- expose already accepted `BuyStop` / `SellStop` trading contracts as a real product capability inside the current one-trade local desktop workflow;
- improve the training value of replay by letting the user practice waiting for confirmation rather than only immediate market execution;
- open a new productive lane after plan recall that is stronger than any further plan-visibility extension because it changes what the user can do in the live trade loop, not just what the user can read.

This document does not change source-of-truth ownership in `03_MODULES/TRADING_ENGINE.md`, `03_MODULES/DESKTOP_WORKSPACE.md`, `04_TECH/DATA_SCHEMA.md`, or `04_TECH/JOURNAL_SCHEMA.md`.

## Why this Slice is Next

This slice is next because:

- bounded current-trade plan recall already solved the strongest note-derived continuity gap in the live loop;
- the current product still over-relies on immediate market entry even though accepted trading contracts and desktop scope already include manual stop orders as first-class v1 behavior;
- this creates a stronger user-visible gain than any continuation of plan context, protection management, or review backfill because it expands the executable trade loop itself;
- the required ownership already exists in `Order`, `TradeRecord`, `ExecutionRecord`, and desktop trading surfaces, so the product can move forward without new persistence or a hidden subsystem.

## Preconditions / Dependencies

This slice depends on already working layers:

- one active trade lifecycle;
- existing `Order` / `TradeRecord` / `ExecutionRecord` ownership and persistence;
- current desktop trading/context/result/workflow surfaces;
- bounded Initial Trade Protection already implemented;
- bounded Current Trade Plan Context already implemented.

## In-Scope Behavior

This slice includes:

- one bounded pending stop entry path for `BuyStop` and `SellStop` inside the current one-trade replay workflow;
- one active pending stop order at most, still respecting the one-active-trade constraint;
- visibility of pending stop entry state on existing desktop trading/context/result/workflow surfaces where needed;
- post-tick trigger execution when the accepted stop condition is reached;
- manual cancellation of the pending stop order only if strictly needed for the current bounded flow;
- restart recovery of the same pending stop order state or triggered trade result from existing trade/order facts.

## Explicit Out-of-Scope

This slice does not include:

- pending-order expiry policy;
- OCO groups or bracket-order orchestration;
- multiple concurrent pending orders;
- add-on or partial-close expansion;
- trailing stops, break-even automation, or richer protection edits;
- mentor advice, checklist logic, acknowledgment flow, or workflow-engine behavior;
- dashboard, mobile, sync, media, or new persistence.

## Runtime Contract

Runtime contract for this slice:

- `Order`, `TradeRecord`, and `ExecutionRecord` remain the source of truth for pending stop entry state and triggered execution;
- pending stop behavior must stay inside the already accepted trading/storage contracts;
- no new persisted summary, queue, scheduler, or orchestration state is introduced;
- execution remains post-tick and replay-driven.

## Minimum Pending Stop Contract

Minimum product-visible output may expose only what existing surfaces need, such as:

- pending stop present / absent;
- pending stop side;
- trigger price;
- optional initial stop loss / take profit if already supplied by the accepted order contract;
- pending order status;
- trigger execution result or cancellation result when applicable.

The slice must stay operational and factual. It should not become a pending-order management subsystem.

## Desktop-Facing Needs

Desktop can use this slice to:

- let the user prepare a breakout-style entry before the trigger price is reached;
- make the replay trading loop closer to the accepted trading model already fixed in `TRADING_ENGINE.md` and `DESKTOP_WORKSPACE.md`;
- keep pending entry state visible without creating a new desktop subsystem;
- improve discipline value by making the user wait for a declared trigger instead of defaulting to immediate market entry.

Desktop remains a projection consumer and command initiator only.

## Persistence Expectations

Persistence expectations remain strict:

- no new entities are introduced;
- existing order/trade/execution facts remain the only source of truth;
- restart recovery rebuilds the same pending stop state or triggered result from the same local facts;
- no separate pending-order queue, scheduler state, or orchestration history is added.

## Acceptance Scenario

1. User starts a local desktop training session.
2. User places one `BuyStop` or `SellStop` pending entry before a trade is open.
3. Existing trading/context/workflow surfaces show the pending stop state and trigger level.
4. User advances replay.
5. If price reaches the trigger post-tick, the pending order becomes an opened trade through the accepted execution contract.
6. If user cancels before trigger in the bounded supported flow, the pending state disappears cleanly.
7. User restarts the app before trigger or after trigger.
8. Runtime rebuilds the same pending stop state or triggered trade result from existing local facts.

## Acceptance Criteria

This slice is accepted if:

- the current desktop-first/local-first product supports one bounded pending stop entry path from accepted `BuyStop` / `SellStop` contracts;
- the live trade loop becomes meaningfully stronger because the user can stage a trigger-based entry instead of relying on market-entry-only flow;
- existing trading/context/result/workflow surfaces carry the pending stop state without a new subsystem;
- restart recovery restores the same pending stop state or triggered result from existing local facts only;
- no new persistence entity, queue/blocker engine, mentor layer, dashboard, mobile/sync path, or hidden architecture rewrite is introduced.

## Non-Goals / Deferred Items

Deferred for later steps:

- pending-order expiry;
- multiple pending orders;
- OCO or bracket logic;
- pending stop editing history;
- limit-order families;
- mentor commentary or trigger quality scoring.

## Risks / Boundary Protections

Main risks:

- turning pending stop entry into broader pending-order orchestration;
- bundling cancellation, expiry, and multi-order coordination into the same slice;
- reopening protection-management drift by attaching richer management behavior to pending orders;
- creating a desktop workflow-owner layer instead of a thin projection/command path.

Boundary protections:

- one bounded pending stop entry slice only;
- reuse existing `Order` / `TradeRecord` / `ExecutionRecord` ownership only;
- no new persistence;
- no expiry engine, no queue/orchestration logic, no scoring, no mentor layer;
- anything beyond one bounded stop-entry path requires a separate later slice.