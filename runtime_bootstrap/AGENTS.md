# Runtime Bootstrap Instructions

These rules extend the root `AGENTS.md` for files under `runtime_bootstrap/`.

## Domain boundaries

- Runtime code owns replay, execution, persistence facts, and deterministic projections.
- It must not depend on Tk or desktop widgets.
- Replay must not read raw provider data directly; it consumes normalized internal artifacts.
- Trading must not read the tick dataset around the replay contract.
- Journal and review projections must not mutate trade facts.

## Correctness rules

- Preserve deterministic results for the same dataset and command sequence.
- Treat seek, restart, and recovery as state reconstruction, not cursor-only movement.
- Never introduce future leakage through cached ticks, bars, indicators, or projections.
- New market and indicator calculations must define incomplete-bar and warm-up behavior.
- Financial calculations must use the accepted instrument and cost contracts; do not add more ad hoc `float` formulas.
- Execution and recovery changes require long, short, edge-case, and restart tests.

## Persistence rules

- Source facts and trace records must remain auditable.
- Never convert derive-on-read review output into persisted truth.
- A write path must not leave a partially written state accepted as valid.
- Schema evolution must be explicit and backward recovery must be tested.

## Scope warning

The existing review projection stack is frozen for feature expansion. Do not add another cue, badge, token, marker, glyph, summary layer, or synonym unless the active task explicitly selects it.