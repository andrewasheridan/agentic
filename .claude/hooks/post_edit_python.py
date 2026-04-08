#!/usr/bin/env python3
"""
Claude Code PostToolUse hook: run `task format` and `task lint` after Python file edits.

Behavior:
  - Skips silently if the edited file is not a .py file.
  - Skips silently if `task` is not found on PATH (no Taskfile in the project).
  - Runs `task format` first, then `task lint`.
  - If either command fails, reports a systemMessage so Claude sees the output
    and can decide whether to act on it.
  - Always exits 0 so Claude is never blocked by a formatting/lint failure
    (Claude should see the error, not be prevented from continuing).

Config:
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/post_edit_python.py",
            "timeout": 60
          }
        ]
      }
    ]
  }
}

Executable:
    chmod +x ~/.claude/hooks/post_edit_python.py
"""

import json
import os
import shutil
import subprocess
import sys


def run(cmd: list[str], cwd: str) -> tuple[int, str]:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Only act on Write / Edit / MultiEdit tool calls
    tool_name = data.get("tool_name", "")
    if tool_name not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)

    # Resolve the edited file path
    tool_input = data.get("tool_input", {})
    file_path: str = tool_input.get("file_path", tool_input.get("path", ""))
    if not file_path.endswith(".py"):
        sys.exit(0)

    # Work from the project root (Claude Code sets this env var)
    cwd = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    # Bail out gracefully if `task` isn't available
    if shutil.which("task") is None:
        sys.exit(0)

    messages: list[str] = []
    failed = False

    for step in ("format", "lint"):
        code, output = run(["task", step], cwd=cwd)
        if code != 0:
            failed = True
            snippet = output[:800] + ("…" if len(output) > 800 else "")
            messages.append(f"`task {step}` failed (exit {code}):\n{snippet}")

    if failed:
        combined = "\n\n".join(messages)
        print(json.dumps({"systemMessage": combined}))

    sys.exit(0)


if __name__ == "__main__":
    main()
