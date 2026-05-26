"""Renderable ExitPlanModeTool payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    return {**(args[0] if args and isinstance(args[0], dict) else {}), **kwargs}


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"type": "exit-plan-use"}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "exit-plan-result", "active": data.get("active", False), "goal": data.get("goal", "")}


async def renderToolUseRejectedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "exit-plan-rejected", "reason": data.get("reason", "rejected")}


__all__ = ["renderToolResultMessage", "renderToolUseMessage", "renderToolUseRejectedMessage"]
