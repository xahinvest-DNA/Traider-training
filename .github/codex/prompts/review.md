# Trader Trainer Pull Request Review

Review this pull request as a strict read-only reviewer.

First read:

- `AGENTS.md` and relevant nested overrides;
- `01_MASTER/CURRENT_STATE.md`;
- `01_MASTER/SSOT_MAP.md`;
- `01_MASTER/PRODUCT_TRUTH_GATE.md`;
- `05_CODEX/NEXT_TASK.md`;
- `05_CODEX/IMPLEMENTATION_RULES.md`.

Then inspect the full pull request diff.

Report only actionable findings, ordered by severity. Check:

1. whether the diff implements exactly one active task;
2. domain ownership and SSOT conflicts;
3. replay future leakage, time/cursor errors, and seek/recovery divergence;
4. execution, volume, protection, cost, and PnL errors;
5. persistence corruption or backward-recovery risks;
6. desktop code taking ownership of domain calculations;
7. missing or circular tests;
8. new feature breadth forbidden by the active packet or Product Truth Gate;
9. undocumented behavior or missing Project Brain updates.

Do not praise the pull request. Do not propose unrelated refactors. If no blocking findings exist, say so and list residual validation that still requires a human or Windows/Tk check.