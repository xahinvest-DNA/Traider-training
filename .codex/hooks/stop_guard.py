from __future__ import annotations

import json
import subprocess


def _changed_paths() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        raw_path = line[3:].strip()
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1]
        paths.append(raw_path.replace("\\", "/"))
    return paths


def main() -> None:
    changed = _changed_paths()
    if not changed:
        print(json.dumps({"continue": True}))
        return

    messages: list[str] = []
    code_changed = any(
        path.startswith(("runtime_bootstrap/", "desktop_shell/"))
        or path.endswith(".py")
        for path in changed
    )
    tests_changed = any(path.startswith("tests/") and path.endswith(".py") for path in changed)
    worklog_changed = "05_CODEX/CODEX_WORKLOG.md" in changed

    if code_changed and not tests_changed:
        messages.append("Code changed without an accompanying test change; confirm existing coverage is sufficient or add tests.")
    if not worklog_changed:
        messages.append("Before task handoff, update 05_CODEX/CODEX_WORKLOG.md as required by repository rules.")

    payload: dict[str, object] = {"continue": True}
    if messages:
        payload["systemMessage"] = " ".join(messages)
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
