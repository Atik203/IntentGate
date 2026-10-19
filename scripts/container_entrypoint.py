"""Verify the frozen published artifacts before executing a reproduction command."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase5.py", "--check", "--artifacts-only"],
        cwd=root,
        check=False,
    )
    if completed.returncode:
        return completed.returncode
    command = sys.argv[1:] or ["pytest", "-q"]
    os.chdir(root)
    os.execvp(command[0], command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
