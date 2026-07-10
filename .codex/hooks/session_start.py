from __future__ import annotations

import json
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def _read_excerpt(path: Path, line_limit: int) -> str:
    if not path.exists():
        return f"Missing required file: {path.name}"
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    return "\n".join(lines[:line_limit])


def main() -> None:
    root = _repo_root()
    active_task = _read_excerpt(root / "05_CODEX" / "NEXT_TASK.md", 32)
    truth_gate = _read_excerpt(root / "01_MASTER" / "PRODUCT_TRUTH_GATE.md", 18)
    context = (
        "Trader Trainer repository context loaded. Follow AGENTS.md and nested overrides.\n\n"
        "ACTIVE TASK EXCERPT:\n"
        f"{active_task}\n\n"
        "PRODUCT TRUTH GATE EXCERPT:\n"
        f"{truth_gate}\n\n"
        "Do not implement work outside the active packet."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
