"""Interpret bash command results without model calls."""

from __future__ import annotations

from typing import Any


async def interpretCommandResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    result = args[0] if args and isinstance(args[0], dict) else kwargs
    exit_code = int(result.get("exit_code", result.get("exitCode", 0)) or 0)
    timed_out = bool(result.get("timed_out", result.get("timedOut", False)))
    stdout = str(result.get("stdout", ""))
    stderr = str(result.get("stderr", ""))
    status = "timed_out" if timed_out else ("success" if exit_code == 0 else "failed")
    summary = stderr.strip() or stdout.strip() or ("Command timed out." if timed_out else "Command produced no output.")
    return {
        "status": status,
        "exitCode": exit_code,
        "timedOut": timed_out,
        "hasOutput": bool(stdout or stderr),
        "summary": summary.splitlines()[0] if summary else "",
    }


__all__ = ["interpretCommandResult"]
