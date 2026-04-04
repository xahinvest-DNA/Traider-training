# Desktop Launch Path

Date fixed: 2026-03-30
Status: implementation boundary v1
Priority: current

## Purpose and Scope

`DESKTOP_LAUNCH_PATH.md` fixes a bounded launch-path slice for the already accepted desktop shell.

The goal of this step is to:

- make the current desktop shell easier to start in local development;
- provide a predictable launch path over the accepted shell/runtime contracts;
- keep launch behavior explicit and testable;
- avoid moving into packaging, installers, or broader platform engineering.

This document does not change desktop shell scope, runtime boundaries, or source-of-truth ownership.

## Why this Slice is Next

This slice is next because:

- the shell is already acceptance-backed as an MVP operating surface;
- the next practical gain is making it easier to start and hand off in local development;
- launch-path cleanup can be done without feature growth;
- this gives a cleaner operational entry into the current accepted shell.

## Preconditions / Dependencies

This slice depends on:

- current desktop shell controller and Tk shell;
- accepted desktop MVP smoke pass;
- current runtime fixture/default dataset path;
- existing local storage behavior.

## In-Scope Behavior

This slice includes:

- a bounded launch config/helper layer;
- a predictable `python -m desktop_shell` entrypoint;
- a predictable top-level script entrypoint for local development;
- launch-path tests around argument parsing and entrypoint availability.

## Explicit Out-of-Scope

This slice does not include:

- application packaging;
- installers;
- desktop auto-update;
- OS integration;
- release engineering;
- multi-environment deployment matrix.

## Launch Contract

The launch path may define only:

- default dataset fixture path;
- default local storage path;
- replay mode argument handling;
- controller bootstrap from parsed config.

It must not add new business logic.

## Acceptance Scenario

1. Developer starts the shell through `python -m desktop_shell --help`.
2. Developer starts the shell through `python run_desktop_shell.py --help`.
3. Launch helpers expose predictable defaults and parsed overrides.
4. Launch config builds a controller that boots the accepted desktop workspace.

## Acceptance Criteria

This slice is accepted if:

- a bounded launch-path document exists;
- local development has at least two predictable entrypoints;
- launch helpers are testable without GUI runtime;
- no packaging or platform-engineering work is introduced.

## Non-Goals / Deferred Items

Deferred beyond this slice:

- installers;
- binary packaging;
- signed app bundles;
- OS-specific launch integration;
- release pipeline work.

## Risks / Boundary Protections

Main risks:

- turning launch cleanup into packaging work;
- mixing controller bootstrap with new business logic;
- growing local development entrypoints into platform complexity.

Boundary protections:

- launch path stays local-development-only;
- launch helpers remain thin;
- controller bootstrap stays unchanged;
- any packaging or distribution work requires a separate later slice.
