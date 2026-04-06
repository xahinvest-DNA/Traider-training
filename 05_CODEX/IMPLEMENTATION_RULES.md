# Codex Implementation Rules

Last updated: 2026-04-06
Status: active
Purpose: define how Codex should read project context, interpret tasks, change files, and report work inside this repository.

## Core rule
Codex must treat this repository as a source-of-truth project system, not as a loose code folder and not as a continuation of chat memory.

## Mandatory reading order for implementation tasks
1. `00_INDEX.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/ROADMAP.md`
5. `01_MASTER/SSOT_MAP.md`
6. `05_CODEX/NEXT_TASK.md`
7. Relevant module/schema documents named in `NEXT_TASK.md`

## Task interpretation rules
- Implement only the task described in `05_CODEX/NEXT_TASK.md`.
- If `TASKS.md` contains historical or paused slices outside the active packet, do not revive them implicitly.
- Prefer the smallest bounded change that satisfies the task acceptance criteria.
- If a possible change conflicts with `DECISIONS.md`, do not code around it silently; re-scope the task first.

## Scope-control rules
- Do not broaden scope under labels such as polish, hardening, cleanup, or support work.
- Do not introduce new layers, abstractions, entities, caches, or surfaces unless the active task explicitly requires them.
- Do not convert derive-on-read layers into persistence.
- Do not move domain ownership from master/module/schema documents into the UI.
- Do not reopen deferred areas such as mentor, mobile, sync, dashboard, packaging, or broad platform work unless the active task explicitly selects them.

## Documentation-update rules
A Codex pass is not complete unless it updates the repository state where required.

### Always update when the task completes
- `05_CODEX/CODEX_WORKLOG.md`

### Update when the current focus or task state changes
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`

### Update when navigation or authority changes
- `00_INDEX.md`
- `01_MASTER/SSOT_MAP.md`

### Update when project-level meaning changes
- `01_MASTER/DECISIONS.md`

## File-authority rules
- Use `01_MASTER/SSOT_MAP.md` to determine which document owns each question.
- If two files overlap, preserve the primary SSOT and reduce drift in the weaker file.
- Do not redefine schema, domain, or product boundaries inside implementation documents.

## Navigation anti-drift rules
- Do not duplicate the active task, current frontier, or current packet inside navigation files.
- If such information is needed in navigation, point to the owning SSOT instead of restating it.
- `00_INDEX.md` is the navigation entry point, not the owner of live operational state.
- Current state lives in `01_MASTER/CURRENT_STATE.md`.
- Current Codex packet lives in `05_CODEX/NEXT_TASK.md`.
- If drift exists, reduce the weaker document so it points back to the stronger SSOT.
- A task is not considered state-synchronized if `CURRENT_STATE.md` and `NEXT_TASK.md` moved forward but `00_INDEX.md` still contains stale operational claims.

## Handoff rules
At the end of every completed task, respond in the structure defined by `05_CODEX/HANDOFF_TEMPLATE.md`.

## Quality bar
A good Codex pass:
- solves one bounded problem;
- leaves the repository easier to resume in a new session;
- updates state files so the next task can start from documents instead of chat memory;
- does not create hidden architectural drift.
