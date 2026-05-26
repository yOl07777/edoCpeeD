"""Utility helpers for migrated AgentTool runtime shims."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ._registry import AGENT_RUNS, get_definition, register_definition, run_agent

agentToolResultSchema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "agentType": {"type": "string"},
        "status": {"type": "string"},
        "result": {"type": "string"},
    },
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _messages(args: tuple[Any, ...], kwargs: dict[str, Any]) -> list[Any]:
    value = kwargs.get("messages")
    if value is None and args:
        value = args[0]
    return list(value) if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)) else []


def _tool_name(message: Any) -> str | None:
    item = _as_dict(message)
    for key in ("name", "toolName", "tool_name"):
        if item.get(key):
            return str(item[key])
    content = item.get("content")
    if isinstance(content, list):
        for block in content:
            name = _tool_name(block)
            if name:
                return name
    return None


async def classifyHandoffIfNeeded(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Classify a handoff request without calling a model."""

    prompt = str(kwargs.get("prompt") or (args[0] if args else ""))
    agent_type = kwargs.get("agentType") or kwargs.get("agent_type")
    if not agent_type:
        lowered = prompt.lower()
        agent_type = "verification" if "verify" in lowered or "test" in lowered else "general-purpose"
    definition = get_definition(str(agent_type)) or register_definition(str(agent_type), source="ad-hoc")
    return {"handoff": bool(prompt or kwargs), "agentType": definition["agentType"], "confidence": 1.0}


async def countToolUses(*args: Any, **kwargs: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for message in _messages(args, kwargs):
        name = _tool_name(message)
        if name:
            counts[name] = counts.get(name, 0) + 1
    return counts


async def emitTaskProgress(*args: Any, **kwargs: Any) -> dict[str, Any]:
    run_id = str(kwargs.get("runId") or kwargs.get("taskId") or (args[0] if args else ""))
    progress = kwargs.get("progress", args[1] if len(args) > 1 else None)
    if run_id in AGENT_RUNS:
        AGENT_RUNS[run_id]["progress"] = progress
    return {"runId": run_id, "progress": progress, "emitted": bool(run_id)}


async def extractPartialResult(*args: Any, **kwargs: Any) -> str:
    messages = _messages(args, kwargs)
    if not messages and args:
        value = args[0]
        if isinstance(value, str):
            return value
    parts: list[str] = []
    for message in messages:
        item = _as_dict(message)
        text = item.get("text") or item.get("result") or item.get("content")
        if isinstance(text, str):
            parts.append(text)
    return "\n".join(parts).strip()


async def filterToolsForAgent(*args: Any, **kwargs: Any) -> list[Any]:
    tools = kwargs.get("tools", args[0] if args else [])
    agent = _as_dict(kwargs.get("agent") or (args[1] if len(args) > 1 else {}))
    allowed = set(agent.get("tools") or kwargs.get("allowedTools") or [])
    if not allowed:
        return list(tools or [])
    result = []
    for tool in tools or []:
        name = tool.get("name") if isinstance(tool, dict) else str(tool)
        if name in allowed:
            result.append(tool)
    return result


async def finalizeAgentTool(*args: Any, **kwargs: Any) -> dict[str, Any]:
    run_id = str(kwargs.get("runId") or (args[0] if args else ""))
    result = kwargs.get("result", args[1] if len(args) > 1 else "")
    run = AGENT_RUNS.get(run_id)
    if run is None:
        run = run_agent(kwargs.get("agentType", "general-purpose"), str(result))
        if run_id:
            AGENT_RUNS.pop(run["runId"], None)
            run["id"] = run_id
            run["runId"] = run_id
            AGENT_RUNS[run_id] = run
    run["status"] = kwargs.get("status", "completed")
    run["result"] = result
    return run


async def getLastToolUseName(*args: Any, **kwargs: Any) -> str | None:
    for message in reversed(_messages(args, kwargs)):
        name = _tool_name(message)
        if name:
            return name
    return None


async def resolveAgentTools(*args: Any, **kwargs: Any) -> list[Any]:
    agent = _as_dict(kwargs.get("agent") or (args[0] if args else {}))
    tools = kwargs.get("tools", args[1] if len(args) > 1 else [])
    return await filterToolsForAgent(tools, agent)


async def runAsyncAgentLifecycle(*args: Any, **kwargs: Any) -> dict[str, Any]:
    agent_type = str(kwargs.get("agentType") or kwargs.get("agent_type") or (args[0] if args else "general-purpose"))
    prompt = str(kwargs.get("prompt") or (args[1] if len(args) > 1 else ""))
    return run_agent(agent_type, prompt, status=kwargs.get("status", "completed"))


__all__ = [
    "agentToolResultSchema",
    "classifyHandoffIfNeeded",
    "countToolUses",
    "emitTaskProgress",
    "extractPartialResult",
    "filterToolsForAgent",
    "finalizeAgentTool",
    "getLastToolUseName",
    "resolveAgentTools",
    "runAsyncAgentLifecycle",
]
