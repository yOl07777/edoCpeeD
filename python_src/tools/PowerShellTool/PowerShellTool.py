from __future__ import annotations

import asyncio
import re
from typing import Any

from python_src.tools.base import PythonTool, object_schema


BLOCKED_SLEEP_RE = re.compile(r"\b(Start-Sleep|sleep|timeout)\s+([1-9]\d{2,}|\d+[mh])\b", re.IGNORECASE)


def detectBlockedSleepPattern(command: str) -> bool:
    return bool(BLOCKED_SLEEP_RE.search(command))


async def run_powershell(
    command: str,
    *,
    cwd: str | None = None,
    timeout_seconds: int = 30,
    max_output_chars: int = 20_000,
) -> dict[str, Any]:
    if detectBlockedSleepPattern(command):
        raise ValueError("Long sleep/timeout commands are blocked.")
    proc = await asyncio.create_subprocess_exec(
        "powershell",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
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


PowerShellTool = PythonTool(
    name="run_powershell",
    description="Run a PowerShell command and return stdout, stderr, and exit code.",
    parameters=object_schema(
        {
            "command": {"type": "string"},
            "timeout_seconds": {"type": "integer", "default": 30},
        },
        required=["command"],
    ),
    handler=run_powershell,
    read_only=False,
)
