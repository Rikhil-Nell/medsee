#!/usr/bin/env python3
"""Block shell commands that appear to embed secrets."""

import json
import re
import sys

SECRET_PATTERNS = [
    re.compile(r"OPENAI_API_KEY\s*=\s*['\"]?\S+", re.IGNORECASE),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"cat\s+\.env\b"),
    re.compile(r"type\s+\.env\b", re.IGNORECASE),
    re.compile(r"Get-Content\s+\.env\b", re.IGNORECASE),
]


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"permission": "allow"}))
        sys.exit(0)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"permission": "allow"}))
        sys.exit(0)

    command = payload.get("command", "")
    for pattern in SECRET_PATTERNS:
        if pattern.search(command):
            print(
                json.dumps(
                    {
                        "permission": "deny",
                        "user_message": "This command may expose secrets. Use .env instead.",
                        "agent_message": (
                            "Hook blocked a command that may embed or print secrets. "
                            "Refer to .env.example for required variables."
                        ),
                    }
                )
            )
            sys.exit(0)

    print(json.dumps({"permission": "allow"}))
    sys.exit(0)


if __name__ == "__main__":
    main()
