# Desktop MVP Acceptance Smoke Pass

Date fixed: 2026-03-30
Status: implementation boundary v1
Priority: current

## Purpose and Scope

`DESKTOP_MVP_ACCEPTANCE_SMOKE_PASS.md` fixes a bounded acceptance/smoke slice for the already usable desktop shell.

The goal of this step is to:

- verify the current desktop shell end-to-end over the accepted local-first runtime;
- confirm that the single-session desktop workflow is operationally usable, not only structurally implemented;
- tighten smoke-level verification around current replay, trading, review, summary, finalization, and recovery behavior;
- avoid new feature growth under an acceptance label.

This document does not change source-of-truth ownership or desktop shell scope boundaries.

## Why this Slice is Next

This slice is next because:

- the shell is already operationally usable after the latest polish slices;
- the right next move is to confirm the whole desktop workflow as one bounded operating path;
- acceptance now needs to cover the desktop surface itself, not only the headless runtime;
- this can be done without dashboards, multi-session shell work, or product expansion.

## Preconditions / Dependencies

This slice depends on:

- current replay/trading/journal runtime contracts;
- current desktop shell controller;
- current chart/context/authoring/history/workflow/control helper layers;
- current local persistence and restart recovery.

## In-Scope Behavior

This slice includes:

- one explicit desktop acceptance/smoke scenario;
- verification of single-session desktop workflow state transitions;
- verification that desktop helper projections remain consistent before and after restart;
- narrow fixes only if acceptance reveals inconsistency.

## Explicit Out-of-Scope

This slice does not include:

- new desktop features;
- GUI automation framework work;
- dashboard or archive shell;
- mentor, mobile, or sync work;
- desktop redesign;
- new persistence or new domain rules.

## Acceptance Contract

This slice must validate at minimum that one local user can:

1. open the desktop shell over a normalized dataset;
2. see the initial paused/review-empty state;
3. create a bounded `PreTradeNote`;
4. open one manual trade;
5. close it and see pending-review guidance;
6. create `PostTradeReview` plus optional flag/violation markers;
7. see result/history/workflow/control surfaces stay consistent;
8. finalize the session;
9. restart and recover the same accepted desktop-visible state.

## Desktop-Facing Verification Focus

Verification in this slice is limited to:

- desktop controller flow;
- desktop helper outputs;
- desktop-visible state coherence;
- recovery of the same accepted session state after restart.

## Acceptance Scenario

1. User starts the shell on the sample dataset.
2. Shell shows paused replay and no active trade.
3. User saves a `PreTradeNote`.
4. User opens one manual trade and advances replay.
5. Shell shows active trade guidance and close availability.
6. User manually closes the trade and pauses replay.
7. Shell shows pending-review guidance and force-finalize availability.
8. User saves a `PostTradeReview`, a behavioral flag, and a rule violation.
9. Shell shows reviewed result/history state and standard finalization availability.
10. User finalizes the session.
11. Shell would now show finalized guidance and no active controls.
12. App restarts and rebuilds the same accepted session state from persistence.

## Acceptance Criteria

This slice is accepted if:

- a bounded desktop MVP acceptance/smoke document exists;
- one explicit desktop smoke test covers the current single-session workflow end-to-end;
- current desktop-visible projections remain consistent before and after restart;
- no new feature surfaces are introduced;
- current implementation stays inside the accepted MVP desktop boundary.

## Non-Goals / Deferred Items

Deferred beyond this slice:

- real GUI automation;
- visual regression testing;
- multi-session acceptance packs;
- desktop archive acceptance;
- cross-device/sync acceptance.

## Risks / Boundary Protections

Main risks:

- feature growth masked as acceptance work;
- pushing desktop toward a richer platform under smoke-pass framing;
- turning smoke verification into a new persistence/testing subsystem.

Boundary protections:

- acceptance remains bounded to the current desktop MVP loop;
- fixes stay limited to issues that break that loop;
- no new storage or domain rules are introduced;
- any step beyond this smoke pass requires a separate later slice.
