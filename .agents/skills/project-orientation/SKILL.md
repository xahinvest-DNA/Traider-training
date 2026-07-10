---
name: trader-trainer-project-orientation
description: Use at the start of any Trader Trainer implementation, diagnosis, review, or planning task to load the active repository state and identify the authoritative documents. Do not use it as permission to implement work outside NEXT_TASK.md.
---

# Project Orientation

1. Read `AGENTS.md` and any nested `AGENTS.md` that applies to the working directory.
2. Read the mandatory SSOT sequence listed in the root instructions.
3. State the active task ID, task type, allowed scope, forbidden scope, and required validation.
4. Inspect the current branch and working tree before editing.
5. Identify the exact source-of-truth documents for every domain concept touched by the task.
6. If repository state conflicts, stop implementation and report the conflict instead of choosing a convenient interpretation.
7. Do not use chat memory to override repository facts.

Output a compact orientation note before implementation:

- Active packet
- Relevant owners of truth
- Files expected to change
- Invariants at risk
- Validation plan