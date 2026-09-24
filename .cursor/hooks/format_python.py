#!/usr/bin/env python3
"""Run ruff format on edited Python files."""

import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit(0)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    file_path = payload.get("file_path", "")
    if not file_path.endswith(".py"):
        sys.exit(0)

    path = Path(file_path)
    if not path.is_file():
        sys.exit(0)

    try:
        subprocess.run(
            ["uv", "run", "ruff", "format", str(path)],
            check=False,
            capture_output=True,
        )
    except FileNotFoundError:
        subprocess.run(
            ["ruff", "format", str(path)],
            check=False,
            capture_output=True,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
