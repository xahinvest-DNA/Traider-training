# SSOT Map

Last updated: 2026-04-04
Status: active
Purpose: define which document is the source of truth for each project question so ChatGPT, Codex, and future sessions do not drift across duplicated context.

## How to use this file

1. Start from `00_INDEX.md` for navigation.
2. Use this file to determine which document has authority for the specific question.
3. If two documents overlap, prefer the one listed here as the primary source of truth.
4. If a document is changed in a way that affects its authority, update this map in the same task.

## Primary project-entry documents

### Project entry and navigation
- Primary SSOT: `00_INDEX.md`
- Scope: main entry point, navigation, reading order, key links.
- Notes: this is the first file for new sessions.

### Current project state
- Primary SSOT: `01_MASTER/CURRENT_STATE.md`
- Scope: what is implemented now, accepted current focus, open items, next step.
- Notes: this is the first operational file to read after `00_INDEX.md`.

### Accepted architectural and product decisions
- Primary SSOT: `01_MASTER/DECISIONS.md`
- Scope: fixed decisions, rationale, consequences, boundaries.
- Notes: if a proposed task conflicts with this file, the task must be re-scoped before coding.

### High-level direction and sequencing
- Primary SSOT: `01_MASTER/ROADMAP.md`
- Scope: implementation order, phases, direction of travel.
- Notes: use to validate whether the next step fits the intended sequence.

### Product boundary
- Primary SSOT: `01_MASTER/PRODUCT_SCOPE.md`
- Secondary SSOT: `01_MASTER/MVP_vs_FULL.md`
- Scope: MVP boundary, later-phase separation, scope creep control.
- Notes: use before proposing any new surface, platform, or expansion slice.

### Constraints and non-goals
- Primary SSOT: `01_MASTER/CONSTRAINTS.md`
- Scope: what must not be done, avoided drift, implementation boundaries.
- Notes: use together with `DECISIONS.md` for safety rails.

## Domain source-of-truth documents

### Replay runtime behavior
- Primary SSOT: `03_MODULES/REPLAY_ENGINE.md`
- Scope: replay semantics, cursor/time behavior, control rules, execution-facing replay model.

### Trading behavior
- Primary SSOT: `03_MODULES/TRADING_ENGINE.md`
- Scope: trading lifecycle, position model, execution policy, trade-side rules.

### Desktop operating surface
- Primary SSOT: `03_MODULES/DESKTOP_WORKSPACE.md`
- Scope: desktop responsibilities, interaction boundaries, MVP operating surface.

### Journal and analytics behavior
- Primary SSOT: `03_MODULES/JOURNAL_ANALYTICS.md`
- Scope: derive-on-read analytics ownership, review outputs, summary boundaries.

### Bill Williams classification layer
- Primary SSOT: `03_MODULES/BILL_WILLIAMS_LAYER.md`
- Scope: Bill Williams runtime/review classification boundaries and methodology layer.

### Market model
- Primary SSOT: `03_MODULES/MARKET_MODEL.md`
- Scope: instrument/market profile assumptions and execution-facing market rules.

### Data import behavior
- Primary SSOT: `03_MODULES/DATA_IMPORT.md`
- Scope: raw import boundary, normalized dataset assumptions, quality-policy role.

## Technical schema source-of-truth documents

### Trade persistence
- Primary SSOT: `04_TECH/DATA_SCHEMA.md`
- Scope: trade storage entities, IDs, cardinality, mutable/immutable policy, recovery links.

### Session and journal persistence
- Primary SSOT: `04_TECH/JOURNAL_SCHEMA.md`
- Scope: `TrainingSession`, notes, reviews, snapshots, flags, violations, session-bound persistence rules.

## Codex execution source-of-truth documents

### Backlog and task history
- Primary SSOT: `05_CODEX/TASKS.md`
- Scope: task registry, completed slices, paused slices, historical task lineage.
- Notes: remains the long-form task ledger.

### Current active task packet
- Primary SSOT: `05_CODEX/NEXT_TASK.md`
- Scope: exactly one current task for Codex, with boundaries, allowed files, forbidden changes, and acceptance criteria.
- Notes: this file should be updated before each new implementation pass.

### Codex handoff and session log
- Primary SSOT: `05_CODEX/CODEX_WORKLOG.md`
- Scope: what Codex changed, what remains incomplete, risks, and recommended next step.
- Notes: every completed Codex pass should append one entry here.

### Codex implementation rules
- Primary SSOT: `05_CODEX/IMPLEMENTATION_RULES.md`
- Scope: rules for how Codex must interpret tasks and update documentation.

### Codex response format
- Primary SSOT: `05_CODEX/HANDOFF_TEMPLATE.md`
- Scope: mandatory handoff structure after each task.

## Conflict-resolution rule

If two documents seem to overlap:
1. Prefer the document listed here as primary SSOT.
2. If overlap remains unresolved, update the weaker document so it points back to the primary one.
3. If the conflict changes project meaning, record the resolution in `01_MASTER/DECISIONS.md`.

## Working rule for new chats

A new chat should begin with:
1. `00_INDEX.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/ROADMAP.md`
5. This file: `01_MASTER/SSOT_MAP.md`
6. `05_CODEX/NEXT_TASK.md` if the purpose is implementation
7. The relevant module/schema documents for the active slice
