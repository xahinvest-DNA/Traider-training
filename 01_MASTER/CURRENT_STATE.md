# Current State

Last updated: 2026-07-10
Current stage: operational prototype accepted as a coherent local workflow; repository engineering baseline and Product Truth Gate are established
Active task: `T-132 Active Trade Protection Adjustment`
Active question: how to complete one bounded live protection-adjustment slice and then move from feature growth to market, execution, and recovery correctness

## Current product position

Trader Trainer is a desktop-first manual trading trainer on historical data with Bill Williams methodology as the primary learning framework.

The current local workflow is:

`dataset -> replay -> trade -> manage -> close -> review -> finalization -> restart recovery`

The repository contains working foundations for:

- raw CSV/TSV/JSON import into a normalized internal dataset;
- tick-driven replay with Training, Exam, and Review modes;
- one canonical replay cursor and post-tick execution snapshots;
- BuyMarket, SellMarket, BuyStop, and SellStop;
- initial optional stop loss and take profit;
- partial close and manual close;
- local TrainingSession, PreTradeNote, PostTradeReview, BehavioralFlag, and RuleViolation facts;
- local persistence and restart recovery;
- Bill Williams review vocabulary and derive-on-read review output;
- a Tk desktop shell over replay, trading, and journal projections;
- a chart-first workspace with prototype bar, Alligator, fractal, and AO rendering.

## What is now explicitly understood

The repository is an operational prototype, not yet a fully validated market-accurate trainer.

The strongest remaining risks are:

- chart bars are currently built from adjacent ticks or fixed tick groups rather than canonical timeframe buckets;
- Alligator and other indicator calculations are prototype-level and not independently validated against golden fixtures;
- seek moves the cursor but does not yet prove complete deterministic bar/indicator state reconstruction without future leakage;
- replay speed is tick-count based rather than a complete historical-time scheduler;
- PnL and costs are not yet instrument-aware monetary calculations;
- prices, volumes, and money still use ad hoc binary floats;
- persistence is one rewritten JSON state file rather than a transactional local store;
- realistic long datasets, performance, day/week boundaries, and crash recovery are not sufficiently proven;
- the test suite protects many review/projection aliases more strongly than the underlying market truth;
- constant status strings must not be treated as executable product acceptance evidence.

The full evidence and recommendations are recorded in `05_CODEX/PROJECT_DIAGNOSTIC_2026-07-10.md`.

## Engineering baseline now established

The repository now defines:

- root and nested `AGENTS.md` instructions;
- repo-scoped Codex skills under `.agents/skills/`;
- project Codex hooks under `.codex/`;
- Python 3.11 project metadata and dev dependencies in `pyproject.toml`;
- ignored local runtime/test artifacts in `.gitignore`;
- Windows and Linux GitHub Actions CI;
- one-task pull request template;
- an expanded root README;
- the master `01_MASTER/PRODUCT_TRUTH_GATE.md` boundary;
- an updated T-132 task packet aligned with the correctness sequence.

## Active task

`T-132 Active Trade Protection Adjustment` remains the next coding packet.

It must add bounded adjustment of current SL/TP on an active position, including validation, persistence/recovery, projection, compact desktop controls, tests, and manual Windows/Tk smoke verification.

It must not add:

- trailing stop;
- break-even automation;
- a protection-history subsystem;
- a broader risk/account engine;
- workspace redesign;
- review-layer expansion;
- mentor, mobile, sync, dashboard, broker, portfolio, or order-flow scope.

The authoritative packet is `05_CODEX/NEXT_TASK.md`.

## Post-T-132 movement

After T-132, feature breadth is frozen until the Product Truth Gate is addressed in this order:

1. Canonical Market and Bar Engine.
2. Canonical Bill Williams Indicators.
3. Instrument and Execution Math.
4. Durable Local Storage.
5. Real Dataset and Performance Gate.
6. ATAS-inspired chart interaction and workflow refinement.
7. Review simplification through one coaching-summary facade.

The authoritative boundary and acceptance gates are in `01_MASTER/PRODUCT_TRUTH_GATE.md`.

## ATAS reference boundary

Trader Trainer may adopt ATAS-like:

- chart-first workspace;
- chart-based order and protection interaction;
- replay controls, stepping, and hotkeys;
- workspace/training templates;
- execution markers;
- MAE/MFE, R-multiple, costs, and linked replay review.

It must not implement footprint, Smart Tape, DOM, heatmap, aggressor-side, or Level II analysis without corresponding source data. The current dataset model contains bid/ask ticks only.

## Operating workflow

The normal development cycle is now fixed:

1. ChatGPT prepares or refines exactly one bounded `NEXT_TASK.md` packet.
2. Codex implements that packet in one task branch and one pull request.
3. Codex runs repository validation and returns the exact handoff template.
4. ChatGPT reviews the diff, tests, architecture, recovery, and residual risks.
5. Only after review does ChatGPT select the next packet.

Task count is not the success metric. Increased trust in market truth, execution truth, recovery, and user learning value is the success metric.

## Open technical decisions

These remain open until their corresponding Product Truth Gate packet is prepared:

- exact canonical timestamp representation;
- integer ticks versus Decimal for prices and money;
- exact bar boundary/session calendar rules;
- independent reference implementation for Bill Williams golden fixtures;
- SQLite schema and migration policy;
- selected long-history storage format and indexing strategy;
- accepted v1 performance budgets;
- whether Tk remains sufficient after market-correct chart interaction is implemented.

## What must not be lost

- replay and manual decision practice remain the product core;
- one global market time remains authoritative;
- future data must stay hidden;
- the desktop shell remains a thin projection/command surface;
- source facts remain separate from derived review output;
- one active independent trade lifecycle remains the v1 constraint;
- local-first recovery remains mandatory;
- Bill Williams remains the method foundation;
- correctness now has priority over feature breadth.