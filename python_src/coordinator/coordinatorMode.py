from __future__ import annotations

from typing import Any


COORDINATOR_MODE_NAMES = {"coordinator", "team", "swarm", "multi-agent"}


async def matchSessionMode(mode: Any = None, *_args: Any, **kwargs: Any) -> str:
    value = str(kwargs.get("mode") or mode or kwargs.get("sessionMode") or "").strip().lower()
    if value in COORDINATOR_MODE_NAMES:
        return "coordinator"
    if value in {"default", "chat", "code", ""}:
        return "default"
    return value


async def isCoordinatorMode(mode: Any = None, *_args: Any, **kwargs: Any) -> bool:
    return await matchSessionMode(mode, **kwargs) == "coordinator"


async def getCoordinatorSystemPrompt(*_args: Any, **kwargs: Any) -> str:
    model = str(kwargs.get("model") or "deepseek-chat")
    return (
        "You are DeepSeek Code running in coordinator mode. Break the user's goal into "
        "safe, independently verifiable tasks, assign work clearly, preserve repository "
        f"state, and integrate results before final response. Active model: {model}."
    )


async def getCoordinatorUserContext(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    return {
        "provider": "deepseek",
        "mode": "coordinator",
        "cwd": kwargs.get("cwd", ""),
        "goal": kwargs.get("goal", ""),
        "agents": list(kwargs.get("agents", []) or []),
        "tools": list(kwargs.get("tools", []) or []),
    }


__all__ = [
    "COORDINATOR_MODE_NAMES",
    "getCoordinatorSystemPrompt",
    "getCoordinatorUserContext",
    "isCoordinatorMode",
    "matchSessionMode",
]
