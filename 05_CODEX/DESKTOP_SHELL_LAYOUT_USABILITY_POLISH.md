# Desktop Shell Layout and Usability Polish

Date fixed: 2026-03-30
Status: implementation boundary v1
Priority: current

## Purpose and Scope

`DESKTOP_SHELL_LAYOUT_USABILITY_POLISH.md` fixes a bounded desktop shell polish slice for improving day-to-day readability and control ergonomics inside the already working single-session shell.

The goal of this step is to:

- make the shell easier to scan and operate during the current local-first workflow;
- expose action availability more clearly;
- reduce avoidable invalid actions in the shell;
- preserve the shell as a thin projection-driven UI.

This document does not change replay, trading, journal, or analytics source-of-truth boundaries.

## Why this Slice is Next

This slice is next because:

- current runtime, guidance, and feedback are already in place;
- the next usability gain comes from making the shell easier to operate, not from adding more feature depth;
- projection-driven action availability can now be surfaced without adding domain logic;
- this can be done without dashboard growth, multi-session shell work, or new persistence.

## Preconditions / Dependencies

This slice depends on:

- current desktop shell controller and Tk shell;
- replay allowed-controls projection;
- current trading/journal/finalization projections;
- the workflow guidance/action feedback slice.

## In-Scope Behavior

This slice includes:

- compact control availability hints;
- desktop button enable/disable behavior driven by existing projections;
- bounded polish of current shell layout and operational readability;
- helper/model code that remains testable outside GUI runtime.

## Explicit Out-of-Scope

This slice does not include:

- new shell navigation model;
- dashboard or multi-session shell;
- command palette or shortcut system;
- persisted desktop preferences;
- new workflow engine logic;
- domain rule changes.

## Runtime Contract

This polish must consume only existing projection inputs such as:

- replay `allowed_controls` and replay status;
- trading active-trade/manual-close state;
- journal pending-review and finalization state.

The UI must not invent its own business rules.

## Desktop-Facing Minimum Contract

The shell may add only:

- compact control availability summary;
- button enabled/disabled states derived from current projections;
- layout polish that improves readability of the current single-session workflow.

## Acceptance Scenario

1. User opens the shell.
2. Shell shows which replay/trade/review/session actions are currently available.
3. Invalid actions become visually unavailable when projections say they should not be used.
4. User moves through replay, trade open, trade close, pending review, and finalization states.
5. Shell updates control availability accordingly without changing runtime logic.

## Acceptance Criteria

This slice is accepted if:

- a bounded layout/usability polish document exists;
- desktop shell surfaces control availability in a readable way;
- action buttons reflect projection-driven availability;
- helper/model logic is testable outside GUI runtime;
- no new persistence, dashboard behavior, multi-session shell, or domain rule changes are introduced.

## Non-Goals / Deferred Items

Deferred beyond this slice:

- keyboard shortcut layer;
- command palette;
- docking/layout customization;
- persisted UI preferences;
- multi-window shell;
- archive navigation.

## Risks / Boundary Protections

Main risks:

- silently moving business logic into UI availability rules;
- using polish as an excuse for wider desktop architecture growth;
- overcomplicating the shell with heavy UI state.

Boundary protections:

- all availability stays projection-driven;
- UI remains a thin consumer over accepted runtime contracts;
- layout polish remains current-session only;
- anything beyond bounded ergonomics requires a separate later slice.
