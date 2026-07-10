# Trader Trainer Project Diagnostic

Date: 2026-07-10
Scope: repository `xahinvest-DNA/Traider-training`, default branch state at commit `f07473b189b71ea230b3445d3196ab20dd08ad11`
Status: repository-wide diagnostic baseline

## Executive conclusion

Trader Trainer has a strong product concept, unusually explicit scope boundaries, and a real end-to-end local prototype. The main risk is no longer absence of workflow features. The main risk is that market representation, indicators, execution math, persistence, and acceptance evidence are less mature than the review and projection layers built on top of them.

The project must now move from "working interface prototype" to "trainer whose market and execution results can be trusted".

## What is already strong

- Clear core: historical replay, manual trading, journal, behavioral review, Bill Williams method.
- Desktop-first boundary and local-first recovery.
- Replay, trading, journal, and desktop responsibilities are mostly separated.
- One active trade lifecycle significantly limits early complexity.
- Project Brain, SSOT map, active task packet, handoff template, and anti-scope rules provide strong continuity.
- A complete local path exists from dataset selection through replay, trading, review, finalization, and recovery.
- Raw CSV/TSV/JSON import and quality-warning propagation are implemented.
- Market orders, pending stop entries, initial protection, partial close, manual close, and protective close are present.
- Automated tests cover many workflow and projection paths.

## Critical findings

### 1. Displayed bars are not canonical timeframe bars

`desktop_shell/chart_surface.py` currently creates bars from adjacent tick points or fixed tick-count groups. It does not aggregate by actual M5, M15, H1, H4, or D1 timestamp buckets.

Impact:

- the visible timeframe label can disagree with actual market aggregation;
- fractals and indicators are calculated on synthetic bars;
- the user may train on price structure that did not exist in the selected timeframe.

Priority: P0.

### 2. Bill Williams indicator calculations are prototype-level

The current Alligator helper uses a shifted simple moving average and clamps shifted values at the right edge. Canonical smoothing, warm-up, incomplete-bar behavior, and confirmation timing are not independently validated. AO is also calculated over the prototype bars, and AC is not part of the mandatory rendered set.

Priority: P0.

### 3. Seek does not rebuild complete market state

Replay seek moves the cursor and appends the target tick to recent cached ticks. It does not prove that bars, indicators, and all derived market state are rebuilt without future leakage.

Required invariant:

`sequential replay to T == seek/rebuild to T == restart recovery at T`.

Priority: P0.

### 4. Playback speed is not a real historical-time scheduler

`advance_frame` converts speed to an integer number of ticks. Fractional speeds therefore behave like 1x at the event-consumption level, while actual pacing depends on the UI loop.

Priority: P0.

### 5. PnL is price delta multiplied by volume

The runtime does not yet apply contract size, pip/tick value, account currency conversion, lot steps, commission, swap, or accepted slippage to produce broker-comparable monetary results. Spread is stored as an absolute price difference rather than a volume-aware monetary cost.

Priority: P0.

### 6. Prices and money use unrestricted binary floats

Price, volume, PnL, spread, and costs are represented as `float`, which weakens deterministic accounting and cross-run equality.

Priority: P0 within the execution-math gate.

### 7. Local persistence is one rewritten JSON file

The complete runtime state is rewritten to `local_runtime_state.json` and manually reconstructed. This lacks transactions, migrations, multiple-session storage, and robust interrupted-write behavior.

Priority: P0/P1 depending on whether the active task changes persistence.

### 8. Dataset loading does not scale to realistic tick histories

Import loads all raw rows, sorts them in memory, writes one large JSON array, and replay loads the full array into memory. This is acceptable for fixtures but not for long tick histories.

Priority: P1 after correctness contracts are fixed.

### 9. Gap classification is not session-aware

A fixed 60-second threshold will classify legitimate weekends, exchange breaks, and CFD session pauses as unexpected gaps.

Priority: P1.

### 10. Test evidence is imbalanced

The suite strongly covers projection text and many derive-on-read review aliases, but the core market-truth matrix is comparatively weak. The primary fixture contains six ticks over seven seconds and cannot validate real timeframe aggregation, long replay, performance, day/week boundaries, or indicator correctness.

Priority: P0 test strategy correction.

### 11. Acceptance can be circular

The MVP pause-point snapshot writes values such as `accepted` and `usable` as constants, and tests verify those constants. That validates report shape, not product readiness.

Priority: P1, addressed by Product Truth Gate F.

### 12. Review derivation has excessive semantic layering

Review output contains long chains such as cue -> badge -> token -> marker -> glyph -> sigil -> seal -> crest -> emblem, plus parallel progress/momentum/floor/ceiling/band layers. These create maintenance and test cost without proportional user value.

Decision:

- freeze new review aliases;
- preserve current behavior during correctness work;
- later expose one coaching-summary facade with factual result, method assessment, primary gap, and next action.

## Repository engineering findings

Before this baseline branch, the repository did not expose a reproducible root Python project configuration, root Codex instructions, repository-scoped skills, active hooks, or GitHub Actions status checks.

The engineering baseline adds:

- root and nested `AGENTS.md` instructions;
- repo-scoped skills in `.agents/skills`;
- trusted-review Codex lifecycle hooks in `.codex`;
- `pyproject.toml` for Python 3.11 and dev tools;
- `.gitignore` for runtime/test artifacts;
- cross-platform GitHub Actions CI;
- pull request template;
- product-truth master boundary;
- expanded README and active-task references.

## ATAS lessons

Adopt:

- chart-first workspace;
- chart-based order and protection interaction;
- hotkeys and replay stepping;
- training/workspace templates;
- entry, exit, partial-close, and protection markers;
- MAE, MFE, R-multiple, costs, and linked replay review.

Do not adopt yet:

- footprint and cluster charts;
- Smart Tape;
- DOM and heatmap;
- aggressor-side and order-flow imbalance;
- broad broker-terminal and portfolio scope.

Reason: the current normalized dataset contains bid/ask ticks only. Order-flow features require corresponding trade-volume and Level II data.

## Approved movement

1. Complete active T-132 without broadening it.
2. Freeze new feature breadth.
3. Implement canonical market time and bars.
4. Validate Bill Williams indicators with golden fixtures.
5. Implement instrument-aware monetary execution math.
6. replace fragile persistence with a transactional local store.
7. prove operation on realistic datasets and performance constraints.
8. then improve ATAS-inspired chart interaction.
9. simplify review output behind one coaching summary.

The authoritative gate and order are in `01_MASTER/PRODUCT_TRUTH_GATE.md`.

## Operational rule for future cycles

The normal cycle is:

1. ChatGPT opens or refines exactly one bounded `NEXT_TASK.md` packet.
2. Codex implements it in a task branch and returns the repository handoff.
3. ChatGPT reviews the diff, tests, architecture, and residual risks.
4. Only after review is the next packet selected.

Task count is not a success metric. Increasing confidence in market truth, execution truth, recovery, and user learning value is the success metric.