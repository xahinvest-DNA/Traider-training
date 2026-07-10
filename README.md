# Trader Trainer

Desktop-first trainer for manual trading on historical data, centered on Bill Williams methodology, replay integrity, execution trace, journal facts, and behavioral review.

## Current product boundary

The repository contains a working local prototype of:

- normalized historical dataset import;
- tick-driven replay with Training, Exam, and Review modes;
- market and pending stop entries;
- initial SL/TP, partial close, manual close, and recovery;
- local session, notes, post-trade review, flags, and violations;
- a Tk desktop shell over runtime projections.

The product is not a broker terminal, portfolio platform, order-flow platform, cloud service, or universal strategy tester.

## Important accuracy status

The current repository is an operational prototype, not yet a fully validated market-accurate trainer. Before broader product expansion, the project must pass the gates in `01_MASTER/PRODUCT_TRUTH_GATE.md`, including canonical timeframe bars, Bill Williams indicator validation, monetary execution math, durable persistence, and realistic dataset/performance tests.

See `05_CODEX/PROJECT_DIAGNOSTIC_2026-07-10.md` for the detailed diagnosis.

## Requirements

- Python 3.11
- Windows for the supported Tk GUI path
- Linux or Windows for headless tests

## Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Validation

```bash
python -m pytest
python -m ruff check .
python -m compileall runtime_bootstrap desktop_shell
```

## Launch

```bash
python -m desktop_shell --help
python run_desktop_shell.py --help
python run_desktop_shell_gui.py --help
```

The repository previously required a separate Tk-capable Python 3.11 runtime on the original Windows workstation. That is an environment workaround, not a portable dependency contract.

## Codex workflow

1. Start from `AGENTS.md`.
2. Read the active packet in `05_CODEX/NEXT_TASK.md`.
3. Use one branch and one pull request per task.
4. Implement only the bounded acceptance path.
5. Run the repository validation commands.
6. Update the Project Brain state and worklog.
7. Return the handoff defined in `05_CODEX/HANDOFF_TEMPLATE.md`.

Repository-scoped Codex skills are under `.agents/skills/`. Project hooks are under `.codex/` and must be explicitly reviewed and trusted in Codex before they run.

## Project navigation

- Project entry point: `00_INDEX.md`
- Current state: `01_MASTER/CURRENT_STATE.md`
- Decisions: `01_MASTER/DECISIONS.md`
- Product truth gate: `01_MASTER/PRODUCT_TRUTH_GATE.md`
- Active Codex task: `05_CODEX/NEXT_TASK.md`
- Implementation rules: `05_CODEX/IMPLEMENTATION_RULES.md`
- Full diagnosis: `05_CODEX/PROJECT_DIAGNOSTIC_2026-07-10.md`

## Pull request policy

A pull request must contain one task, tests for changed invariants, a complete handoff, and no unrelated cleanup. CI must pass before review. GUI-affecting changes also require a manual Windows/Tk smoke result in the PR description.