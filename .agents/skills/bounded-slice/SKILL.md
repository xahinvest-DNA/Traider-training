---
name: trader-trainer-bounded-slice
description: Use when implementing one approved Trader Trainer task packet. It enforces one vertical slice, explicit invariants, minimal file changes, tests, and repository handoff. Do not use for broad redesign or speculative cleanup.
---

# Bounded Slice Implementation

1. Load the active packet with the project-orientation skill.
2. Translate the packet into one observable acceptance path.
3. List the minimum domain, projection, UI, persistence, and test changes required.
4. Reject adjacent improvements that are not necessary for that path.
5. Implement domain behavior before UI exposure.
6. Add tests that fail before the change and prove the accepted behavior after it.
7. Run targeted tests, then the full repository validation commands.
8. Inspect the diff for accidental scope growth, duplicate ownership, new persisted summaries, and unrelated formatting.
9. Update the required state and worklog files.
10. Return the exact handoff format from `05_CODEX/HANDOFF_TEMPLATE.md`.

A bounded slice is complete only when:

- the acceptance path works;
- affected invariants are tested;
- restart/recovery is covered when persisted state changes;
- no next-task implementation is included;
- documentation and active state remain synchronized.