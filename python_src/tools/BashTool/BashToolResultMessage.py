"""Renderable BashTool result payloads."""

from __future__ import annotations

from typing import Any


def BashToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    result = args[0] if args and isinstance(args[0], dict) else kwargs
    exit_code = result.get("exit_code", result.get("exitCode", 0))
    timed_out = bool(result.get("timed_out", result.get("timedOut", False)))
    return {
        "type": "bash-result",
        "exitCode": exit_code,
        "timedOut": timed_out,
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "status": "timed_out" if timed_out else ("success" if exit_code == 0 else "failed"),
    }


__all__ = ["BashToolResultMessage"]
