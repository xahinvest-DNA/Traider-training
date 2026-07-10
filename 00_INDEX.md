# Trader Trainer Project Brain

## Purpose

This file is the stable navigation entry point for Trader Trainer. It does not own current state, the active task, domain contracts, or date-sensitive claims.

## Start here

1. [AGENTS.md](AGENTS.md) — repository working rules for Codex and contributors.
2. [01_MASTER/CURRENT_STATE.md](01_MASTER/CURRENT_STATE.md) — current product and engineering position.
3. [01_MASTER/DECISIONS.md](01_MASTER/DECISIONS.md) — accepted project decisions.
4. [01_MASTER/ROADMAP.md](01_MASTER/ROADMAP.md) — implementation sequence.
5. [01_MASTER/SSOT_MAP.md](01_MASTER/SSOT_MAP.md) — authority map.
6. [01_MASTER/PRODUCT_TRUTH_GATE.md](01_MASTER/PRODUCT_TRUTH_GATE.md) — correctness gates before feature expansion.
7. [05_CODEX/NEXT_TASK.md](05_CODEX/NEXT_TASK.md) — the only active implementation packet.

## Core product documents

- [01_MASTER/VISION.md](01_MASTER/VISION.md)
- [01_MASTER/ARCHITECTURE.md](01_MASTER/ARCHITECTURE.md)
- [01_MASTER/CONSTRAINTS.md](01_MASTER/CONSTRAINTS.md)
- [01_MASTER/PRODUCT_SCOPE.md](01_MASTER/PRODUCT_SCOPE.md)
- [01_MASTER/MVP_vs_FULL.md](01_MASTER/MVP_vs_FULL.md)
- [01_MASTER/ROADMAP.md](01_MASTER/ROADMAP.md)
- [01_MASTER/CURRENT_STATE.md](01_MASTER/CURRENT_STATE.md)
- [01_MASTER/SSOT_MAP.md](01_MASTER/SSOT_MAP.md)
- [01_MASTER/PRODUCT_TRUTH_GATE.md](01_MASTER/PRODUCT_TRUTH_GATE.md)

## Domain and module contracts

- [03_MODULES/REPLAY_ENGINE.md](03_MODULES/REPLAY_ENGINE.md)
- [03_MODULES/MARKET_MODEL.md](03_MODULES/MARKET_MODEL.md)
- [03_MODULES/DATA_IMPORT.md](03_MODULES/DATA_IMPORT.md)
- [03_MODULES/TRADING_ENGINE.md](03_MODULES/TRADING_ENGINE.md)
- [03_MODULES/JOURNAL_ANALYTICS.md](03_MODULES/JOURNAL_ANALYTICS.md)
- [03_MODULES/BILL_WILLIAMS_LAYER.md](03_MODULES/BILL_WILLIAMS_LAYER.md)
- [03_MODULES/DESKTOP_WORKSPACE.md](03_MODULES/DESKTOP_WORKSPACE.md)

## Technical schemas

- [04_TECH/DATA_SCHEMA.md](04_TECH/DATA_SCHEMA.md)
- [04_TECH/JOURNAL_SCHEMA.md](04_TECH/JOURNAL_SCHEMA.md)

## Codex operating layer

- [05_CODEX/NEXT_TASK.md](05_CODEX/NEXT_TASK.md)
- [05_CODEX/IMPLEMENTATION_RULES.md](05_CODEX/IMPLEMENTATION_RULES.md)
- [05_CODEX/HANDOFF_TEMPLATE.md](05_CODEX/HANDOFF_TEMPLATE.md)
- [05_CODEX/CODEX_WORKLOG.md](05_CODEX/CODEX_WORKLOG.md)
- [05_CODEX/TASKS.md](05_CODEX/TASKS.md)
- [05_CODEX/PROJECT_DIAGNOSTIC_2026-07-10.md](05_CODEX/PROJECT_DIAGNOSTIC_2026-07-10.md)

Historical implementation packets remain under `05_CODEX/`; use `TASKS.md` and repository search to locate them. They are not active unless `NEXT_TASK.md` explicitly selects them.

## Working code

- `runtime_bootstrap/` — replay, trading, import, journal, persistence, review projections, and runtime fixtures.
- `desktop_shell/` — controller, projections, launch paths, Tk shell, and chart/trader surfaces.
- `tests/` — runtime and desktop-shell test suites.

## Codex automation

- `.agents/skills/` — repository-scoped Codex skills.
- `.codex/hooks.json` and `.codex/hooks/` — project lifecycle hooks; review and trust them in Codex before use.
- `.github/workflows/ci.yml` — Windows and Linux CI.
- `.github/pull_request_template.md` — one-task PR handoff checklist.

## Research

- [02_RESEARCH/BILL_WILLIAMS_RULES.md](02_RESEARCH/BILL_WILLIAMS_RULES.md)
- `deep-research-report (1).md`
- source Bill Williams books and research materials stored in the repository.

## Working rule

A new implementation session starts from `AGENTS.md` and the Start here sequence. Chat history never overrides repository authority.