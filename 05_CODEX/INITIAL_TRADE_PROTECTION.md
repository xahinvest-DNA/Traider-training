# Initial Trade Protection

Date fixed: 2026-04-04
Status: implementation boundary v1
Priority: current

## Purpose and Scope

`INITIAL_TRADE_PROTECTION.md` fixes one bounded broader frontier after the review-loop lane has been exhausted.

The purpose of this slice is:

- extend the current desktop-first/local-first product value from post-trade review into active-trade discipline;
- let the user define one bounded initial protective plan for the current trade instead of jumping straight from entry to manual close only;
- use already accepted trading/storage contracts for `stopLoss` and `takeProfit` without introducing a new owner of truth, new persistence, or workflow orchestration;
- open a new productive lane in the product that is stronger than any further review-derived micro-slice because it improves the live training loop itself.

This document does not change source-of-truth ownership in `03_MODULES/TRADING_ENGINE.md`, `03_MODULES/DESKTOP_WORKSPACE.md`, `03_MODULES/JOURNAL_ANALYTICS.md`, or `04_TECH/DATA_SCHEMA.md`.

## Why this Slice is Next

This slice is next because:

- the current review loop already has bounded diagnosis, actionability, and compact synthesis;
- further review/digest/evidence layering now mostly produces decorative or orchestration-like follow-up work;
- the biggest remaining user-visible gap inside the local desktop product is that the active trade loop still under-trains protective execution discipline by relying on `entry -> manual close` as the only practical exit path;
- initial `stopLoss` / `takeProfit` support is already accepted at contract level, so the next gain can come from making that capability product-real instead of inventing another derived review cue.

## Preconditions / Dependencies

This slice depends on already working layers:

- replay bootstrap and post-tick execution loop;
- one active trade lifecycle;
- accepted trade storage contract with `stopLoss` / `takeProfit` fields;
- current desktop trading control and context surfaces;
- local persistence and restart recovery for trade facts.

## In-Scope Behavior

This slice includes:

- one bounded initial trade-protection path for the current active trade;
- optional initial `stopLoss` and `takeProfit` values at trade entry when the current trading contract allows them;
- post-tick protective close handling through already accepted trading-engine rules;
- readable desktop visibility of active protective levels and triggered protective exit reason through existing trading/context/result surfaces only;
- restart recovery of the same protective state from existing local trade facts.

## Explicit Out-of-Scope

This slice does not include:

- trailing stops;
- complex order-editing workflows;
- pending-stop expiry orchestration;
- add-on entry flow;
- partial close flow;
- risk scoring or mentor coaching;
- queue/blocker/acknowledgment state;
- dashboard, mobile, sync, media, or new persistence.

## Runtime Contract

Runtime contract for this slice:

- `stopLoss` and `takeProfit` remain owned by existing trading/storage contracts;
- protective state stays inside the current trade lifecycle and does not become a separate subsystem;
- protective exits use already accepted post-tick and ambiguity rules from the trading contract;
- no new persisted entity, cache, or workflow state is introduced.

## Minimum Protection Contract

Minimum trade-facing protection output may expose only what existing trade surfaces already need to show and recover, such as:

- current `stopLoss`
- current `takeProfit`
- whether protection is present on the active trade
- protective close reason when a trade is closed by SL/TP

The slice should stay bounded to initial protection only. Any later editing history, trailing logic, or advanced management behavior requires a separate slice.

## Desktop-Facing Needs

Desktop can use this slice to:

- let the user open a trade with an explicit bounded protection plan;
- keep active protection visible while the trade is open;
- show when a trade closed by protective trigger instead of manual close;
- strengthen the live training loop without creating a richer UI platform.

Desktop remains a projection consumer and command initiator only.

## Persistence Expectations

Persistence expectations remain strict:

- no new entities are introduced;
- existing trade facts remain the only source of truth;
- restart recovery rebuilds protective state from the same local trade records;
- separate persisted history of SL/TP edits is out of scope for this slice.

## Acceptance Scenario

1. User starts a local desktop training session.
2. User opens one trade and optionally provides initial `stopLoss` and/or `takeProfit`.
3. Active trade surfaces show the protective plan while the position is open.
4. If market reaches a protective threshold, the trade closes through the accepted post-tick protective rule.
5. Result/context surfaces show the triggered protective exit reason.
6. User restarts the app while the protected trade is active or after it is closed.
7. Runtime restores the same protective state or protective close result from existing local trade facts.

## Acceptance Criteria

This slice is accepted if:

- the current desktop-first/local-first product can execute one active trade with optional initial `stopLoss` / `takeProfit`;
- active protective levels are visible through existing desktop trading/context/result surfaces only;
- protective closes follow the accepted trading-engine contract and remain restart-recoverable;
- no new persistence entity, workflow engine, mentor layer, dashboard, mobile/sync path, or hidden architecture rewrite is introduced.

## Non-Goals / Deferred Items

Deferred for later steps:

- SL/TP edit history;
- trailing stops;
- break-even automation;
- pending-stop expiry policy;
- add-on and partial close management;
- risk dashboards or risk scoring.

## Risks / Boundary Protections

Main risks:

- silently expanding into a broader risk engine;
- bundling add-on / partial close / pending-order complexity into the same slice;
- moving trade ownership into desktop helpers;
- reopening mentor or analytics drift under a risk label.

Boundary protections:

- one active-trade protection slice only;
- initial protection only;
- reuse existing trading/storage contracts only;
- no new persistence;
- anything beyond bounded initial SL/TP support requires a separate later slice.
