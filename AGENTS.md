# Trader Trainer Codex Instructions

## Repository role

This repository is the source-of-truth operating system for Trader Trainer. Do not treat chat history as authority when repository documents are available.

## Mandatory reading order

Before changing code or project state, read:

1. `00_INDEX.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/ROADMAP.md`
5. `01_MASTER/SSOT_MAP.md`
6. `01_MASTER/PRODUCT_TRUTH_GATE.md`
7. `05_CODEX/NEXT_TASK.md`
8. The module and schema documents explicitly relevant to the active task

For a repository-wide diagnosis, also read `05_CODEX/PROJECT_DIAGNOSTIC_2026-07-10.md`.

## Active task authority

- `05_CODEX/NEXT_TASK.md` is the only active implementation packet.
- Implement one bounded task at a time.
- Historical tasks in `05_CODEX/TASKS.md` are context, not permission to revive old scope.
- Do not start the next task inside the current task.

## Core product invariants

- Replay time has one source of truth.
- The future must remain hidden in Training and Exam workflows according to the replay contract.
- Trading receives market state only through accepted replay snapshots.
- The desktop shell is a projection and command surface, not a domain owner.
- Trade, execution, session, and journal facts must remain recoverable.
- Derived review output must not become a second persisted source of truth.
- One active independent trade lifecycle remains the v1 constraint.

## Product-truth priority

After the currently approved active-trade protection slice, correctness work has priority over new feature breadth. Do not add new review labels, dashboard layers, mentor features, mobile, cloud sync, order-flow surfaces, or platform-like expansion before the gates in `01_MASTER/PRODUCT_TRUTH_GATE.md` are satisfied.

## Working rules

- Use one branch and one pull request per task.
- Prefer the smallest change that proves the task acceptance path.
- Do not edit `main` directly.
- Do not introduce a new entity, cache, persistence layer, abstraction, or UI surface unless the active packet requires it.
- Do not silently change domain meaning to make tests pass.
- Preserve public behavior unless the task explicitly changes it.
- Add or update tests for every changed invariant.
- Inspect the full diff before handoff.

## Validation commands

Use Python 3.11.

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m compileall runtime_bootstrap desktop_shell
```

GUI behavior must also be checked manually on the supported Windows/Tk path when the task changes `desktop_shell/tk_app.py` or launch behavior.

## Required completion updates

When a task is complete:

- update `05_CODEX/CODEX_WORKLOG.md`;
- update `01_MASTER/CURRENT_STATE.md`, `05_CODEX/TASKS.md`, and `05_CODEX/NEXT_TASK.md` when the active frontier changes;
- update `01_MASTER/DECISIONS.md` only when project-level meaning changes;
- use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

A task is not complete merely because tests pass. The handoff must state what changed, what did not change, validation performed, residual risks, and the recommended next step.