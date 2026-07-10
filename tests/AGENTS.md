# Test Instructions

These rules extend the root `AGENTS.md` for files under `tests/`.

## Test priority

Protect product truth before projection wording.

Priority order:

1. replay time and hidden-future invariants;
2. bar and indicator correctness;
3. execution price, volume, costs, and PnL;
4. persistence, crash safety, and recovery;
5. end-to-end workflow behavior;
6. desktop projection and wording helpers.

## Required patterns

- Use deterministic fixtures.
- Add golden tests for market bars and Bill Williams indicators.
- Prove sequential replay, seek-to-time, and restart recovery produce equivalent state.
- Include long and short behavior.
- Include incomplete bars, duplicate timestamps, gaps, day boundaries, and large-dataset cases when relevant.
- Do not treat hard-coded status labels such as `accepted` or `usable` as evidence of acceptance.
- Avoid adding multiple near-identical tests for cosmetic review aliases.

## Temporary data

All test-generated state must live under ignored temporary directories and must be cleaned or isolated per test.