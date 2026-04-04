# Desktop Workflow Guidance and Action Feedback

Date fixed: 2026-03-30
Status: implementation boundary v1
Priority: current

## Purpose and Scope

`DESKTOP_WORKFLOW_GUIDANCE_ACTION_FEEDBACK.md` fixes a bounded desktop shell slice for improving workflow guidance, action feedback, and finalization blocker visibility inside the already working local-first shell.

The goal of this step is to:

- make the current next step clearer during the active local workflow;
- surface pending review and finalization blockers in an operational way;
- expose bounded recent action feedback without creating a new UI-owned business state layer;
- keep the shell thin and projection-driven.

This document does not change replay, trading, journal, or analytics source-of-truth boundaries.

## Why this Slice is Next

This slice is next because:

- current runtime and desktop shell already expose enough projection data for guidance and blockers;
- the next usability gain comes from showing the user what to do now, not from adding more data;
- finalization force-vs-standard behavior already exists in runtime and needs a clearer bounded surface;
- this can be implemented without dashboard growth, new persistence, or domain redesign.

## Preconditions / Dependencies

This slice depends on:

- the current desktop shell controller and Tk shell;
- current replay, trading, journal, history, and review projections;
- session finalization and review summary projections;
- accepted local-first recovery behavior.

## In-Scope Behavior

This slice includes:

- compact workflow guidance based on current replay/trade/review/finalization state;
- compact finalization blocker visibility;
- bounded recent action feedback inside the shell;
- explicit desktop access to `force finalize` over the already accepted runtime contract;
- helper/model code that remains testable outside GUI runtime.

## Explicit Out-of-Scope

This slice does not include:

- workflow engine or wizard state;
- dashboard cards or multi-session operating shell;
- persisted UI notifications;
- mentor prompts or recommendations;
- automation of review completion;
- changes to finalization domain rules.

## Runtime Contract

This refinement must consume only existing runtime contracts such as:

- replay status from desktop replay projection;
- active trade state from desktop trading projection;
- pending review and summary state from `session_review_summary`;
- blocker and force-finalization state from `session_finalization`.

The UI must not re-derive or override domain decisions.

## Desktop-Facing Minimum Contract

The shell may surface only:

- one compact workflow guidance block;
- one compact blocker block;
- one compact recent action feedback block;
- explicit `Force Finalize` access that calls the existing runtime method.

## Acceptance Scenario

1. User opens the desktop shell.
2. Shell shows a bounded next-step guidance message for the empty current session.
3. User opens and closes a trade without review.
4. Shell shows pending review guidance and finalization blockers.
5. User can see that force finalization exists but is exceptional.
6. User adds review or force-finalizes, and the shell updates action feedback accordingly.
7. After restart, runtime state is recovered and guidance is rebuilt from projections.

## Acceptance Criteria

This slice is accepted if:

- a bounded workflow guidance/action feedback document exists;
- desktop shell shows readable workflow guidance, blocker visibility, and recent action feedback;
- shell exposes `Force Finalize` through the already accepted runtime contract only;
- helper/model logic is testable outside GUI runtime;
- no new persistence, dashboard behavior, or UI-owned workflow engine is introduced.

## Non-Goals / Deferred Items

Deferred beyond this slice:

- guided onboarding flow;
- persisted notifications;
- workflow macros or shortcuts;
- mentor recommendations;
- dashboard-style action center;
- multi-session workflow orchestration.

## Risks / Boundary Protections

Main risks:

- turning workflow hints into a thick workflow engine;
- duplicating domain decisions in UI;
- using feedback UI as a path toward notification infrastructure or dashboard growth.

Boundary protections:

- guidance remains derived from existing projections only;
- action feedback stays ephemeral and local to the shell session;
- force finalization remains an explicit existing runtime action, not a new UI rule;
- anything beyond bounded hints and blockers requires a separate later slice.
