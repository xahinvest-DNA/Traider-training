# Product Truth Gate

Date fixed: 2026-07-10
Status: approved master boundary
Priority: highest after the currently active T-132 slice

## 1. Purpose

This document defines the correctness gates that Trader Trainer must pass before broader product expansion.

The project already has a coherent local workflow, but workflow completeness is not the same as market, execution, and recovery correctness. The next stage must increase trust in the trainer rather than increase the number of visible features.

## 2. Current accepted position

The repository is accepted as an operational desktop-first prototype of:

`dataset -> replay -> trade -> manage -> close -> review -> recovery`

It is not yet accepted as a fully validated market-accurate training environment.

The following current capabilities remain valid foundations:

- one canonical replay cursor;
- normalized internal dataset boundary;
- one active independent trade lifecycle;
- post-tick execution contract;
- local journal and review facts;
- desktop shell as a projection and command surface;
- local recovery;
- bounded Bill Williams vocabulary.

## 3. Freeze boundary

After T-132 Active Trade Protection Adjustment, do not start new feature-breadth work until the gates below are addressed in order.

Frozen areas include:

- new review cue/badge/token/marker/glyph or synonym layers;
- dashboards and broad multi-session analytics;
- mentor workflows;
- mobile;
- cloud sync;
- broker integration;
- multi-instrument portfolio behavior;
- order-flow, DOM, footprint, tape, heatmap, or volume-profile surfaces;
- broad UI redesign not required by a correctness gate.

Bug fixes and changes required to satisfy the gates remain allowed.

## 4. Gate A - Canonical market time and bars

Required:

- parsed canonical timestamps;
- deterministic event ordering;
- timestamp-bucket aggregation for M5 through D1;
- explicit complete/incomplete bar state;
- synchronized timeframe projections from one market cursor;
- deterministic state rebuild after seek and restart;
- playback scheduling that supports fractional and accelerated speed without dropping market events;
- step-tick and step-bar semantics.

Acceptance:

Sequential replay to time T, seek/rebuild to T, and restart recovery at T produce equivalent market state.

## 5. Gate B - Canonical Bill Williams indicators

Required:

- validated Alligator smoothing, periods, and shifts;
- AO 5/34 over canonical bar median prices;
- AC;
- confirmed fractals with future-confirmation timing respected;
- explicit warm-up behavior;
- explicit incomplete-bar policy;
- golden fixtures verified against an independent calculation.

Acceptance:

Indicator results match approved golden values and remain identical across sequential replay, seek, and recovery.

## 6. Gate C - Instrument and execution math

Required:

- instrument specification used by runtime;
- price and volume precision model that avoids ad hoc binary-float money calculations;
- lot step, contract size, tick/pip value, and account currency treatment;
- monetary gross and net PnL;
- spread, commission, swap, and accepted fixed-slippage policy;
- long, short, partial-close, SL, TP, and pending-entry cases.

Acceptance:

Trade and execution results match independent reference calculations for a representative FX/CFD matrix.

## 7. Gate D - Durable local persistence

Required:

- atomic or transactional writes;
- explicit schema version and migrations;
- append-only execution facts;
- durable session/trade/note/review recovery;
- multiple completed local sessions;
- corruption and interrupted-write tests;
- portable session export.

Target direction: SQLite unless a later accepted decision selects an equivalent transactional local store.

Acceptance:

An interruption at any tested lifecycle transition does not silently produce an accepted but inconsistent session.

## 8. Gate E - Realistic datasets and performance

Required fixtures:

- dense intraday ticks;
- sparse data and gaps;
- duplicate timestamps;
- day/week boundaries;
- weekend and session breaks;
- DST boundary where relevant;
- at least one large stress dataset.

Required measurements:

- import time;
- startup time;
- seek latency;
- replay throughput;
- recovery time;
- peak memory;
- storage size.

Acceptance:

The selected v1 dataset profile is usable without loading an impractical full history representation into memory or blocking the desktop workflow.

## 9. Gate F - Product acceptance

Product acceptance must be derived from executable checks and a real user path. It must not be produced by constant strings such as `mvp_status = accepted`.

Required:

- automated end-to-end acceptance script;
- CI on Windows and Linux;
- manual Windows/Tk smoke result for GUI changes;
- no debug panel required to complete the primary workflow;
- one clear coaching result after review:
  1. factual outcome;
  2. method assessment;
  3. primary gap;
  4. next training action.

## 10. Approved implementation order

1. Complete T-132 Active Trade Protection Adjustment.
2. Canonical Market and Bar Engine.
3. Canonical Bill Williams Indicators.
4. Instrument and Execution Math.
5. Durable Local Storage.
6. Real Dataset and Performance Gate.
7. ATAS-inspired chart interaction and workflow refinement.
8. Review simplification through one coaching-summary facade.

Task IDs after T-132 are assigned when each bounded packet is opened. The order is authoritative; exact task wording may be refined by the preceding audit.

## 11. ATAS boundary

Trader Trainer may adopt from ATAS:

- chart-first workspace;
- chart-based entry/protection interaction;
- replay controls and hotkeys;
- workspace/training templates;
- visible execution markers;
- MAE/MFE, R-multiple, costs, and session statistics;
- linked journal and replay review.

Trader Trainer must not imitate ATAS order-flow features without corresponding source data. The current tick model contains bid/ask only and cannot truthfully support footprint, Smart Tape, DOM, heatmap, aggressor-side, or Level II analysis.

The product distinction remains:

ATAS explains and executes market activity. Trader Trainer trains the quality of the user's decision, method compliance, and behavior.