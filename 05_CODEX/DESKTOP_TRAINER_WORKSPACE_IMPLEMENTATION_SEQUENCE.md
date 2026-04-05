# Desktop Trainer Workspace Implementation Sequence

Last updated: 2026-04-05
Status: accepted planning draft
Task ID: T-123
Task type: bounded planning / implementation sequencing pass

## Purpose

This document defines the minimum realistic sequence of implementation slices needed to move the current `desktop_shell/` from an engineering/debug shell to the first usable chart-first trader workspace fixed in `05_CODEX/DESKTOP_TRAINER_WORKSPACE_V1.md`.

This sequencing pass is needed because:

- `T-122` fixed the product-facing boundary, not the coding order;
- `T-106` remains the active coding frontier and must not be silently replaced;
- the desktop reset must avoid architectural rewrite, ownership drift, and broad UI expansion;
- the repository needs one controlled path from the current shell to the new workspace instead of ad hoc desktop polish.

This document does not activate a new coding packet by itself. It prepares the desktop-reset lane for a later explicit implementation switch.

## Current implementation problem

The current `desktop_shell/` is technically working and already sits on accepted replay/trading/journal contracts, but its main surface still reads as shell-centric:

- the primary screen is still too text/status-heavy;
- the chart does not yet own the workspace as the clear center of trading work;
- startup is technically possible but still product-ambiguous;
- trading and review actions are present, but not yet arranged as one coherent trader workspace.

The repository therefore now has:

- a working desktop shell;
- an accepted chart-first product boundary in `DESKTOP_TRAINER_WORKSPACE_V1.md`;
- no bounded implementation sequence yet for how to move from one to the other.

## Sequencing principles

The sequence below must preserve these rules:

- no replay/trading/journal rewrite;
- no change of source-of-truth ownership;
- no mentor/mobile/sync/dashboard/platform expansion;
- no broad charting-platform build-out;
- no UI-owned business state;
- no destruction of existing debug visibility, only relocation behind secondary/debug surfaces;
- each slice must create one concrete usability gain visible to the user.

## Contract alignment decision

### Decision

A separate mandatory alignment pass for `03_MODULES/DESKTOP_WORKSPACE.md` is not required before sequencing or before the first future desktop-reset coding slice.

### Managerial answer

`05_CODEX/DESKTOP_TRAINER_WORKSPACE_V1.md` is already sufficient as the implementation-facing product boundary for planning the desktop-reset lane.

`03_MODULES/DESKTOP_WORKSPACE.md` still remains valid for:

- desktop responsibilities;
- source-of-truth boundaries;
- replay/trading/journal ownership separation;
- MVP-level operating-surface scope limits.

What `T-122` adds is not a new domain contract, but a stronger product-facing priority:

- chart-first main surface;
- primary vs secondary vs debug separation;
- mandatory `bar chart only + Alligator + Fractals + AO` boundary;
- a trader-workspace reading of the screen instead of a shell/status-console reading.

### Minimal alignment trigger

A narrow alignment pass for `03_MODULES/DESKTOP_WORKSPACE.md` should happen only if the first desktop-reset coding packet finds a direct contradiction that blocks implementation.

Until such a contradiction appears, pre-aligning the module doc first would create unnecessary documentation churn and risks reopening the desktop contract too broadly.

## Recommended slice order

## Slice 1. Desktop Trainer Main Screen Reset

### Goal

Replace the current text/status-heavy shell composition with the minimum product-facing workspace skeleton:

- top replay/session bar;
- large chart-first main area;
- dedicated trading panel zone;
- compact context zone;
- review-entry zone;
- explicit secondary/debug zones.

### Why this slice belongs here

This slice creates the destination surface for every later desktop-reset step. Without the workspace skeleton, later work on start flow, chart boundary, text reduction, and trader controls risks getting bolted onto the old shell layout.

### What changes

- layout hierarchy;
- zone priority;
- default landing composition inside the existing desktop shell;
- explicit separation between primary, secondary, and debug surfaces.

### What must stay unchanged

- replay/trading/journal contracts;
- runtime ownership;
- persistence schemas;
- current debug facts themselves.

### New usability gain

The desktop stops reading like an internal console and starts reading like a trader workspace even before the full chart boundary is complete.

### Scope drift to block

- docking/layout system work;
- multi-window architecture;
- UI-platform rewrite;
- dashboard redesign disguised as layout work.

## Slice 2. Desktop Trainer Start Flow Clarification

### Goal

Make startup and entry into the workspace user-credible and unambiguous for the four accepted paths:

- prepared dataset;
- raw import;
- new session;
- restore previous session.

### Why this slice belongs here

Once the new workspace skeleton exists, startup can route the user into a clear destination instead of the old shell. This makes the start flow meaningful without mixing it into packaging or platform engineering.

### What changes

- desktop launch/start choices;
- landing-path wording and routing;
- compact startup decisions before entering the main workspace.

### What must stay unchanged

- import architecture;
- replay bootstrap ownership;
- packaging/install concerns;
- non-GUI readiness/reporting contracts.

### New usability gain

The user can understand how to begin work without parsing technical startup state.

### Scope drift to block

- installer/packaging work;
- platform-specific launcher expansion;
- provider-management UI;
- broad import-management console behavior.

## Slice 3. Desktop Trainer Mandatory Chart Boundary

### Goal

Implement the minimum usable chart surface required by `T-122`:

- `bar chart only`;
- `Alligator` overlay;
- `Fractals` overlay;
- separate lower `AO` pane.

### Why this slice belongs here

The chart boundary should be implemented only after the main screen reserves a stable central chart area. Otherwise chart work will get entangled with layout churn.

### What changes

- main chart rendering contract inside the desktop shell;
- chart composition around the existing replay state;
- mandatory lower indicator pane for `AO`.

### What must stay unchanged

- replay remains tick-driven and bar-fed from replay state;
- UI does not become a market-truth owner;
- no broad indicator engine;
- no candlestick mode.

### New usability gain

This is the first slice where the workspace becomes visually credible as a Bill Williams trader surface instead of a generic shell chart.

### Scope drift to block

- broad charting platform;
- indicator library expansion;
- drawing toolkit build-out;
- multi-chart presets.

## Slice 4. Main-Surface Text Reduction and Secondary/Debug Separation

### Goal

Move shell-style prose and long status chains out of the primary surface while preserving them in secondary or debug surfaces.

Primary targets for removal from the main surface:

- readiness prose;
- recovery prose;
- finalization prose;
- long derived status chains;
- repetitive lifecycle explanations.

### Why this slice belongs here

Once the chart area exists, it must be protected from regression by relocating text-heavy shell surfaces away from the primary workspace.

### What changes

- placement and prominence of long-form status blocks;
- visibility defaults for secondary and debug information;
- main-surface density and hierarchy.

### What must stay unchanged

- the diagnostic information itself;
- existing runtime facts and derived projections;
- engineering access to debug visibility.

### New usability gain

The user can stay in market/trade flow without reading internal state prose, while engineers still retain access to diagnostics when needed.

### Scope drift to block

- deleting needed debug visibility;
- hiding blockers that still matter to user action;
- turning cleanup into a dashboard-style summary redesign.

## Slice 5. Trader Panel and Compact Context Surface

### Goal

Convert the current trading interaction area into a compact trader panel plus factual context block centered on the accepted trade loop.

Required trading actions in scope:

- `Buy Market`
- `Sell Market`
- `Buy Stop`
- `Sell Stop`
- `Cancel Entry`
- `Partial Close`
- `Close`
- optional `SL / TP`
- visible volume entry

Required compact facts in scope:

- active trade yes/no;
- side;
- entry;
- volume;
- `SL / TP`;
- pending entry;
- remaining open volume;
- compact review-needed state.

### Why this slice belongs here

The trader panel should be attached only after the main workspace, chart, and surface hierarchy are stable enough that trade controls can be presented as one coherent panel instead of another status block.

### What changes

- button grouping and placement;
- compact trade facts shown near the chart;
- contextual affordances around active/pending trade state.

### What must stay unchanged

- trading engine order semantics;
- one-active-trade rule;
- trade source-of-truth ownership;
- existing replay/trade contract boundaries.

### New usability gain

The user can understand and act on the trade state from one compact panel rather than scanning multiple shell blocks.

### Scope drift to block

- broker-terminal complexity;
- portfolio-like flows;
- independent UI trade lifecycle ownership;
- rich ticketing subsystem work.

## Slice 6. Review Entry Path and Post-Close Flow

### Goal

Make the transition from closed trade to review explicit and usable without turning the main screen into a review text dump.

### Why this slice belongs here

Review entry depends on a stable main workspace, coherent trade panel/context, and post-close state visibility. It should close the loop after the active trading surface is already understandable.

### What changes

- explicit `Open review` or equivalent post-close action path;
- compact review-needed / review-available indicators;
- bounded routing from current trade result/context into review authoring.

### What must stay unchanged

- `JOURNAL_SCHEMA` ownership;
- `PreTradeNote` / `PostTradeReview` contracts;
- Bill Williams review vocabulary boundaries;
- no review workflow engine or mentor layer.

### New usability gain

The user can move from trade completion into review as one clear action, preserving the replay -> trade -> review training loop.

### Scope drift to block

- review dashboard expansion;
- heavy review authoring subsystem;
- mentor coaching flow;
- multi-session archive/review redesign.

## Area coverage map

The required product areas map to slices as follows:

- A. Start / launch flow -> Slice 2
- B. Main screen reset -> Slice 1
- C. Chart surface -> Slice 3
- D. Main-surface text reduction -> Slice 4
- E. Trading interaction surface -> Slice 5
- F. Compact context surface -> Slice 5
- G. Review entry point -> Slice 6

## Why this order is minimal and realistic

This order is intentionally not a broad redesign. It follows the smallest stable dependency chain:

1. create the new workspace skeleton;
2. route startup into that workspace cleanly;
3. make the chart truly product-facing;
4. protect the primary surface from shell-text regression;
5. consolidate trader actions and compact facts;
6. close the loop with explicit review entry.

This avoids two common failure modes:

- bolting chart/trade polish onto the old shell composition;
- starting a large visual rewrite before a bounded order is agreed.

## Risks and controls

### Accidental desktop rewrite

Risk:

The workspace reset could sprawl into a broad desktop redesign.

Control:

Keep each slice tied to one visible usability gain and forbid new architecture, UI platform work, and ownership changes.

### Chart slice drifting into broad charting platform

Risk:

The mandatory chart boundary could sprawl into indicators, tools, modes, and presets.

Control:

Hard-stop the chart slice at `bar chart only + Alligator + Fractals + AO`.

### Launch-flow work drifting into packaging/platform engineering

Risk:

Startup clarification could become installer, launcher, or platform work.

Control:

Keep the slice inside existing launch/import/session routing only.

### Main-surface cleanup destroying needed debug visibility

Risk:

Text reduction could hide engineering diagnostics that are still needed.

Control:

Relocate diagnostics to secondary/debug surfaces rather than deleting them.

### Workspace reset drifting into dashboard redesign

Risk:

Secondary surfaces could mutate into a summary/dashboard project.

Control:

Keep them secondary, action-supporting, and current-workflow-scoped.

### Silent contradiction between old and new desktop docs

Risk:

`DESKTOP_WORKSPACE.md` and `DESKTOP_TRAINER_WORKSPACE_V1.md` may eventually diverge in wording.

Control:

Do not rewrite module docs preemptively. Trigger one narrow alignment pass only if the first desktop-reset coding packet hits a direct contradiction.

## Strongest next implementation slice

### Selection

The strongest next desktop-reset implementation slice is:

`Desktop Trainer Main Screen Reset`

### Why this is the strongest next desktop slice

It is the smallest slice that:

- changes the reading of the product from shell to workspace;
- establishes the containers needed by all later desktop-reset work;
- creates immediate visible product progress without chart-platform drift;
- does not require prior module-doc rewrite;
- keeps the rest of the reset sequence bounded.

### Important managerial note

This selection does not automatically replace the active coding packet `T-106`.

It means:

- when the repository is ready to open the desktop-reset lane explicitly;
- and when a new desktop coding packet is intentionally chosen;
- the first recommended implementation target should be `Desktop Trainer Main Screen Reset`, not immediate chart-platform work and not another shell-text refinement.
