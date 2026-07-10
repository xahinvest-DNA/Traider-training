---
name: trader-trainer-regression-pass
description: Use before handing off any Trader Trainer code change or reviewing a Codex pull request. It validates tests, scope, persistence recovery, documentation sync, and product-truth risks.
---

# Regression Pass

1. Read the active task acceptance path.
2. Review every changed file and classify it as required, supporting, or unrelated.
3. Run:

```bash
python -m pytest
python -m ruff check .
python -m compileall runtime_bootstrap desktop_shell
```

4. Run focused recovery tests when persistence or lifecycle state changed.
5. Run focused replay equivalence tests when time, seek, bars, indicators, or snapshots changed.
6. Confirm the desktop shell does not own new domain calculations.
7. Confirm no new persisted derived-review truth was introduced.
8. Confirm no unrelated review alias, dashboard, mentor, mobile, sync, or platform scope entered the diff.
9. Check `CODEX_WORKLOG.md` and active state synchronization.
10. Report:

- commands and results;
- acceptance path result;
- regression risks inspected;
- residual limitations;
- whether the PR is ready, conditionally ready, or not ready.

Do not mark a PR ready when tests were not run. Do not infer GUI success from headless tests alone.