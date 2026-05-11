from __future__ import annotations

import asyncio
import re
from typing import Any

from python_src.tools.base import PythonTool, object_schema


BLOCKED_SLEEP_RE = re.compile(r"\b(sleep|timeout)\s+([1-9]\d{2,}|\d+[mh])\b", re.IGNORECASE)
SEARCH_READ_RE = re.compile(r"^\s*(cat|type|head|tail|ls|dir|find|rg|grep|wc)\b", re.IGNORECASE)


def detectBlockedSleepPattern(command: str) -> bool:
    return bool(BLOCKED_SLEEP_RE.search(command))


def isSearchOrReadBashCommand(command: str) -> dict[str, bool]:
    matched = bool(SEARCH_READ_RE.search(command))
    return {
        "isSearch": bool(re.search(r"^\s*(find|rg|grep)\b", command, re.IGNORECASE)),
        "isRead": bool(re.search(r"^\s*(cat|type|head|tail|wc)\b", command, re.IGNORECASE)),
        "isList": bool(re.search(r"^\s*(ls|dir)\b", command, re.IGNORECASE)),
        "matched": matched,
    }


async def run_bash(
    command: str,
    *,
    cwd: str | None = None,
    timeout_seconds: int = 30,
    max_output_chars: int = 20_000,
) -> dict[str, Any]:
    if detectBlockedSleepPattern(command):
        raise ValueError("Long sleep/timeout commands are blocked.")

    proc = await asyncio.create_subprocess_shell(
        command,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        proc.kill()
        stdout, stderr = await proc.communicate()
        return {
            "exit_code": proc.returncode,
            "timed_out": True,
            "stdout": stdout.decode(errors="replace")[:max_output_chars],
            "stderr": stderr.decode(errors="replace")[:max_output_chars],
        }
    return {
        "exit_code": proc.returncode,
        "timed_out": False,
        "stdout": stdout.decode(errors="replace")[:max_output_chars],
        "stderr": stderr.decode(errors="replace")[:max_output_chars],
    }


BashTool = PythonTool(
    name="run_shell",
    description="Run a shell command in the current workspace and return stdout, stderr, and exit code.",
    parameters=object_schema(
        {
            "command": {"type": "string", "description": "Shell command to execute."},
            "timeout_seconds": {"type": "integer", "description": "Timeout in seconds.", "default": 30},
        },
        required=["command"],
    ),
    handler=run_bash,
    read_only=False,
)
