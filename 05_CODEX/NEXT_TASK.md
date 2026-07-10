# NEXT TASK

Last updated: 2026-07-10
Status: ready
Task ID: T-132
Task type: coding

## Goal

Implement one bounded `Active Trade Protection Adjustment` slice so the accepted desktop trainer workspace can update visible stop-loss and take-profit protection on an already active trade without reopening workspace reset, startup, chart-boundary, review-flow, or broader risk-engine scope.

## Why this is next

`T-131` selected active-trade protection adjustment as the final approved product-facing slice before the Product Truth Gate sequence. It improves the live `trade -> manage -> close` stage inside the existing trader rail.

The repository engineering baseline and `01_MASTER/PRODUCT_TRUTH_GATE.md` are now authoritative. After T-132, new feature breadth is frozen until market/bar, indicator, execution-math, persistence, and realistic-data correctness gates are addressed.

## Mandatory reading

1. `AGENTS.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/SSOT_MAP.md`
5. `01_MASTER/PRODUCT_TRUTH_GATE.md`
6. `03_MODULES/TRADING_ENGINE.md`
7. `03_MODULES/DESKTOP_WORKSPACE.md`
8. `04_TECH/DATA_SCHEMA.md`
9. `05_CODEX/IMPLEMENTATION_RULES.md`
10. `05_CODEX/HANDOFF_TEMPLATE.md`
11. This packet

Use the repository skills `trader-trainer-project-orientation`, `trader-trainer-bounded-slice`, and `trader-trainer-regression-pass`.

## What should change

1. Add one domain-owned command for adjusting current `stop_loss` and/or `take_profit` on the existing active position.
2. Validate long and short protection levels against the current accepted execution snapshot.
3. Allow the user to set, replace, or clear optional protection values while an active position exists.
4. Keep `PositionRecord` and the active `TradeRecord` current protection snapshots consistent.
5. Persist and recover the adjusted current protection state through the existing local recovery path.
6. Expose current protection facts and adjustment availability through existing trading projections and controller paths.
7. Add compact desktop controls and action feedback inside the accepted trader rail; do not redesign the workspace.
8. Add focused runtime, desktop, and restart-recovery tests.

## Required behavior

- adjustment is allowed only for an active open or partially closed position;
- adjustment is rejected in Review Replay mode and terminal replay state;
- buy stop loss remains below the current executable close-side price and buy take profit above it;
- sell stop loss remains above the current executable close-side price and sell take profit below it;
- invalid adjustments do not mutate position or trade state;
- an adjusted value survives restart recovery;
- the next replay tick uses the adjusted values for protective-close evaluation.

## What must stay unchanged

- no trailing-stop automation;
- no break-even automation;
- no protection-history subsystem or new persisted ledger;
- no multiple protection profiles;
- no broader risk sizing or account engine;
- no chart/startup/review-form redesign;
- no broker-terminal, dashboard, mentor, mobile, sync, order-flow, or platform expansion;
- no replay/trading/journal ownership rewrite;
- no new review cue, badge, token, marker, glyph, or synonym layer.

## Recommended validation

```bash
python -m pytest
python -m ruff check .
python -m compileall runtime_bootstrap desktop_shell
```

Required focused scenarios:

- adjust SL/TP on active long;
- adjust SL/TP on active short;
- clear one protection level;
- reject invalid side/price relationships without mutation;
- retain adjusted state after restart;
- trigger protective close from the adjusted value;
- preserve partial-close state and remaining volume;
- desktop control availability and feedback.

A manual Windows/Tk smoke check is required because the trader rail changes.

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

## After this task

Do not start another feature slice. Return the repository for review. The next packet will be selected from `01_MASTER/PRODUCT_TRUTH_GATE.md`, with Canonical Market and Bar Engine as the expected next frontier unless the T-132 review reveals a blocking defect.