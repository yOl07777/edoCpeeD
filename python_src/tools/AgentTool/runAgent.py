"""Run AgentTool helpers for migrated Python modules."""

from __future__ import annotations

from typing import Any

from ._registry import run_agent


async def filterIncompleteToolCalls(*args: Any, **kwargs: Any) -> list[Any]:
    messages = list(args[0] if args else kwargs.get("messages", []) or [])
    filtered: list[Any] = []
    for message in messages:
        if not isinstance(message, dict):
            filtered.append(message)
            continue
        if message.get("type") == "tool_use" and not message.get("result") and not message.get("completed", False):
            continue
        filtered.append(message)
    return filtered


async def runAgent(*args: Any, **kwargs: Any) -> dict[str, Any]:
    agent_type = str(kwargs.get("agentType") or kwargs.get("agent_type") or (args[0] if args else "general-purpose"))
    prompt = str(kwargs.get("prompt") or (args[1] if len(args) > 1 else ""))
    messages = await filterIncompleteToolCalls(kwargs.get("messages", []))
    return run_agent(agent_type, prompt, messages=messages, status=kwargs.get("status", "completed"))


__all__ = ["filterIncompleteToolCalls", "runAgent"]
