"""Renderable PowerShellTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "powershell-use",
        "command": data.get("command", ""),
        "cwd": data.get("cwd"),
        "timeoutSeconds": data.get("timeout_seconds") or data.get("timeoutSeconds"),
    }


async def renderToolUseQueuedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "powershell-queued", "command": data.get("command", ""), "queuePosition": data.get("queuePosition")}


async def renderToolUseProgressMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "powershell-progress", "command": data.get("command", ""), "elapsedMs": data.get("elapsedMs")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    exit_code = data.get("exit_code", data.get("exitCode", 0))
    return {
        "type": "powershell-result",
        "exitCode": exit_code,
        "timedOut": bool(data.get("timed_out") or data.get("timedOut", False)),
        "stdout": data.get("stdout", ""),
        "stderr": data.get("stderr", ""),
    }


async def renderToolUseErrorMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "powershell-error", "command": data.get("command", ""), "error": data.get("error") or data.get("message", "")}


__all__ = [
    "renderToolResultMessage",
    "renderToolUseErrorMessage",
    "renderToolUseMessage",
    "renderToolUseProgressMessage",
    "renderToolUseQueuedMessage",
]
