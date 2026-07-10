# SSOT Map

Last updated: 2026-07-10
Status: active
Purpose: define which repository artifact owns each project question so contributors, ChatGPT, Codex, and future sessions do not create competing truth.

## Usage

1. Start from `AGENTS.md` and `00_INDEX.md`.
2. Use this map to identify the owner of the question being changed.
3. Prefer the primary SSOT over implementation notes, reports, tests, or chat context.
4. If authority changes, update this map in the same pull request.
5. If a proposed task conflicts with a master SSOT, re-scope before coding.

## Repository operating authority

### Contributor and Codex working rules

- Primary SSOT: `AGENTS.md`
- Scoped overrides: nested `AGENTS.md` files.
- Scope: reading order, invariants, validation, branch/PR rules, completion requirements.
- Supporting automation: `.agents/skills/` and `.codex/hooks.json`.
- Notes: skills and hooks assist execution; they do not override master product/domain documents.

### Navigation

- Primary SSOT: `00_INDEX.md`
- Scope: stable entry points and links only.
- Notes: it must not own live current state or duplicate the active task packet.

### Current state

- Primary SSOT: `01_MASTER/CURRENT_STATE.md`
- Scope: what exists now, current risks, active frontier, open decisions, and immediate sequence.

### Accepted decisions

- Primary SSOT: `01_MASTER/DECISIONS.md`
- Scope: fixed project decisions, rationale, and consequences.

### Direction and sequencing

- Primary SSOT: `01_MASTER/ROADMAP.md`
- Scope: high-level phases and implementation order.

### Product correctness gates

- Primary SSOT: `01_MASTER/PRODUCT_TRUTH_GATE.md`
- Scope: correctness freeze, gates, acceptance evidence, and post-T-132 order before new feature breadth.
- Notes: this document has priority over older feature-expansion momentum where the two conflict.

### Product boundary

- Primary SSOT: `01_MASTER/PRODUCT_SCOPE.md`
- Secondary SSOT: `01_MASTER/MVP_vs_FULL.md`
- Scope: MVP, later phases, and hard exclusions.

### Constraints and non-goals

- Primary SSOT: `01_MASTER/CONSTRAINTS.md`
- Scope: implementation safety rails and forbidden drift.

## Domain authority

### Replay behavior

- Primary SSOT: `03_MODULES/REPLAY_ENGINE.md`
- Scope: simulation time, event cursor, replay modes, controls, seek, and execution-facing snapshot behavior.

### Market model

- Primary SSOT: `03_MODULES/MARKET_MODEL.md`
- Scope: instrument properties, market profiles, pricing, volume, costs, and session rules.

### Data import

- Primary SSOT: `03_MODULES/DATA_IMPORT.md`
- Scope: raw input, normalization, dataset quality, and internal artifact boundary.

### Trading behavior

- Primary SSOT: `03_MODULES/TRADING_ENGINE.md`
- Scope: order, lifecycle, position, execution, risk-guard, and close behavior.

### Desktop workspace

- Primary SSOT: `03_MODULES/DESKTOP_WORKSPACE.md`
- Scope: user surfaces, commands, projection boundaries, and desktop workflow.

### Journal and analytics

- Primary SSOT: `03_MODULES/JOURNAL_ANALYTICS.md`
- Scope: source facts, derive-on-read ownership, review output, and analytics boundaries.

### Bill Williams layer

- Primary SSOT: `03_MODULES/BILL_WILLIAMS_LAYER.md`
- Research/reference SSOT: `02_RESEARCH/BILL_WILLIAMS_RULES.md`
- Scope: method vocabulary, runtime/review classification boundaries, and later automation limits.

## Technical schema authority

### Trade persistence

- Primary SSOT: `04_TECH/DATA_SCHEMA.md`
- Scope: order, position, trade, execution, IDs, mutability, trace, and recovery relationships.

### Session and journal persistence

- Primary SSOT: `04_TECH/JOURNAL_SCHEMA.md`
- Scope: TrainingSession, notes, reviews, snapshots, flags, violations, and journal recovery.

## Codex execution authority

### Active task

- Primary SSOT: `05_CODEX/NEXT_TASK.md`
- Scope: exactly one current implementation or planning packet.
- Notes: no other file activates work.

### Task history

- Primary SSOT: `05_CODEX/TASKS.md`
- Scope: completed, paused, and historical task lineage.

### Implementation process

- Primary SSOT: `05_CODEX/IMPLEMENTATION_RULES.md`
- Scope: task interpretation, scope control, Git workflow, validation, and repository updates.

### Handoff format

- Primary SSOT: `05_CODEX/HANDOFF_TEMPLATE.md`
- Scope: mandatory completion response.

### Completed work record

- Primary SSOT: `05_CODEX/CODEX_WORKLOG.md`
- Scope: completed pass details, validation, residual risks, and recommended next step.

### Diagnostic evidence

- Current repository-wide report: `05_CODEX/PROJECT_DIAGNOSTIC_2026-07-10.md`
- Scope: findings and rationale supporting the Product Truth Gate.
- Notes: a diagnostic report does not override master contracts; it proposes or explains changes recorded in master SSOTs.

## Executable evidence

- Automated tests live under `tests/`.
- Cross-platform validation workflow: `.github/workflows/ci.yml`.
- Tests prove behavior but do not own product meaning.
- Constant status labels do not constitute acceptance unless produced from executable evidence.

## Conflict resolution

1. Prefer the primary SSOT listed here.
2. Reduce the weaker artifact to an implementation note or link.
3. If the resolution changes project meaning, update `DECISIONS.md` and the relevant master document.
4. Never resolve a conflict silently inside UI code or tests.

## New-session order

1. `AGENTS.md`
2. `00_INDEX.md`
3. `01_MASTER/CURRENT_STATE.md`
4. `01_MASTER/DECISIONS.md`
5. `01_MASTER/ROADMAP.md`
6. `01_MASTER/SSOT_MAP.md`
7. `01_MASTER/PRODUCT_TRUTH_GATE.md`
8. `05_CODEX/NEXT_TASK.md` for implementation
9. Relevant domain and schema owners

Chat history is supporting context only and never overrides this chain.