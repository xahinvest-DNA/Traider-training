# Current Trade Plan Context

Date fixed: 2026-04-04
Status: implementation boundary v1
Priority: current

## Purpose and Scope

`CURRENT_TRADE_PLAN_CONTEXT.md` fixes one bounded next frontier after Initial Trade Protection.

The purpose of this slice is:

- strengthen the live desktop trading loop by keeping the user inside the context of the already declared pre-trade plan;
- make the current trade easier to manage against the trader's own stated setup, thesis, and risk plan instead of relying on memory after entry;
- reuse existing `PreTradeNote` ownership and trade linkage without introducing a new owner of truth, new persistence, or a mentor-like interpretation layer;
- open a new productive lane after bounded initial protection that is stronger than any further protection-management extension because it improves execution discipline through plan visibility, not more orchestration.

This document does not change source-of-truth ownership in `03_MODULES/TRADING_ENGINE.md`, `03_MODULES/DESKTOP_WORKSPACE.md`, `03_MODULES/JOURNAL_ANALYTICS.md`, `04_TECH/DATA_SCHEMA.md`, or `04_TECH/JOURNAL_SCHEMA.md`.

## Why this Slice is Next

This slice is next because:

- bounded initial `stopLoss` / `takeProfit` already made the live trade loop stronger than `entry -> manual close` only;
- the strongest remaining gap in the same local desktop loop is now loss of declared context after entry: the user can create a `PreTradeNote`, but the live trade flow still does not keep the declared setup, thesis, and risk plan compactly present while the trade is active or immediately after it closes;
- extending protection management further would now mostly deepen risk behavior instead of opening a stronger product lane;
- existing `PreTradeNote` facts already provide the needed local source data, so the product can gain value without new persistence or hidden architecture change.

## Preconditions / Dependencies

This slice depends on already working layers:

- one active trade lifecycle;
- local `TrainingSession` / `PreTradeNote` persistence and restart recovery;
- stable trade-to-note linkage;
- current desktop trading/context/result/workflow surfaces;
- bounded Initial Trade Protection already implemented.

## In-Scope Behavior

This slice includes:

- one bounded derive-on-read current-trade plan context built from existing linked `PreTradeNote` facts for the current active trade or latest just-closed trade where helpful;
- compact visibility of already declared plan facts such as:
  - declared `setupTag`
  - `thesisSummary`
  - `riskPlan`
  - whether a linked pre-trade plan is present or absent
- exposure only through existing desktop context/result/workflow surfaces where the live trade loop benefits from seeing the user's own declared plan;
- restart recovery of the same plan context from existing local note and trade facts.

## Explicit Out-of-Scope

This slice does not include:

- new note types or new note persistence fields;
- mentor advice or generated coaching prose;
- semantic grading of the pre-trade plan;
- plan-to-trade scoring or compliance scoring;
- queue/blocker/acknowledgment logic;
- broader trade-protection management such as trailing stops, break-even automation, or SL/TP edit history;
- add-on, partial close, or pending-order orchestration;
- dashboard, mobile, sync, media, or new persistence.

## Runtime Contract

Runtime contract for this slice:

- `PreTradeNote` remains the source of truth for declared plan context;
- trade facts remain owned by the existing trading/storage contracts;
- the slice may derive one compact current-trade plan context from already linked note and trade facts only;
- no new persisted entity, cache, or workflow state is introduced.

## Minimum Plan Context Contract

Minimum output may expose only what existing surfaces need to show and recover, such as:

- plan presence / absence
- declared setup tag if present
- thesis summary if present
- risk plan if present
- note timestamp or note identity only if strictly needed for current-surface clarity

The slice must stay compact and factual. It should not become a prose-summary subsystem.

## Desktop-Facing Needs

Desktop can use this slice to:

- keep the active trade anchored to the user's own declared trade plan;
- reduce context switching between note authoring and live trade management;
- show the same plan context immediately after close while review begins;
- improve discipline value without building a richer trade-management UI platform.

Desktop remains a projection consumer and command initiator only.

## Persistence Expectations

Persistence expectations remain strict:

- no new entities are introduced;
- existing `PreTradeNote` and trade facts remain the only source of truth;
- restart recovery rebuilds the same current-trade plan context from the same local note and trade records;
- no separate persisted plan summary, note-state machine, or plan acknowledgment history is added.

## Acceptance Scenario

1. User starts a local desktop training session.
2. User creates a `PreTradeNote` with setup, thesis, and/or risk plan before entry.
3. User opens one trade.
4. Existing context/workflow surfaces show whether a linked pre-trade plan exists and surface the compact declared plan facts while the trade is active.
5. User closes the trade manually or protectively.
6. Existing result/context/workflow surfaces still show the same compact declared plan context where useful for immediate post-close continuity.
7. User restarts the app during the active trade or after close.
8. Runtime rebuilds the same current-trade plan context from existing local facts.

## Acceptance Criteria

This slice is accepted if:

- the current desktop-first/local-first product can surface one compact current-trade plan context from existing linked `PreTradeNote` facts;
- the live trade loop becomes more actionable because the user can see the declared setup/thesis/risk plan during current-trade handling instead of relying on memory;
- existing context/result/workflow surfaces carry the plan context without a new subsystem;
- restart recovery restores the same plan context from existing local facts only;
- no new persistence entity, workflow engine, mentor layer, dashboard, mobile/sync path, or hidden architecture rewrite is introduced.

## Non-Goals / Deferred Items

Deferred for later steps:

- plan quality scoring;
- plan-vs-execution grading;
- richer note editing workflow;
- mentor commentary over the plan;
- trade checklist engines or mandatory acknowledgments;
- broader multi-trade or session-plan dashboards.

## Risks / Boundary Protections

Main risks:

- turning declared plan context into mentor or scoring logic;
- replacing the note as source of truth with a new summary owner;
- reopening review/digest style micro-layering under a different name;
- bundling more protection-management or orchestration behavior into the same slice.

Boundary protections:

- one compact current-trade plan-context slice only;
- reuse existing `PreTradeNote` and trade linkage only;
- no new persistence;
- no grading, no coaching, no workflow engine;
- anything beyond compact factual plan recall requires a separate later slice.
