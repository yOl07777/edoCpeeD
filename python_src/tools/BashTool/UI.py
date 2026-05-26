"""Renderable BashTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    return {**(args[0] if args and isinstance(args[0], dict) else {}), **kwargs}


async def BackgroundHint(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "bash-background-hint", "command": data.get("command", ""), "visible": data.get("visible", True)}


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "bash-use", "command": data.get("command", ""), "cwd": data.get("cwd")}


async def renderToolUseQueuedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "bash-queued", "command": data.get("command", ""), "queuePosition": data.get("queuePosition")}


async def renderToolUseProgressMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "bash-progress", "command": data.get("command", ""), "elapsedMs": data.get("elapsedMs")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    exit_code = data.get("exit_code", data.get("exitCode", 0))
    return {"type": "bash-result", "exitCode": exit_code, "stdout": data.get("stdout", ""), "stderr": data.get("stderr", "")}


async def renderToolUseErrorMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "bash-error", "command": data.get("command", ""), "error": data.get("error") or data.get("message", "")}


__all__ = [
    "BackgroundHint",
    "renderToolResultMessage",
    "renderToolUseErrorMessage",
    "renderToolUseMessage",
    "renderToolUseProgressMessage",
    "renderToolUseQueuedMessage",
]
