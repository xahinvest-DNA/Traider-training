from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PREFERRED_TK_PYTHON = Path(r"C:\Python311\python.exe")


def main() -> int:
    project_root = Path(__file__).resolve().parent
    interpreter = PREFERRED_TK_PYTHON if PREFERRED_TK_PYTHON.exists() else Path(sys.executable)
    command = [str(interpreter), "-m", "desktop_shell", *sys.argv[1:]]
    completed = subprocess.run(command, cwd=project_root, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
