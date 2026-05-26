"""Renderable data helpers for AgentTool UI migration."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def userFacingName(*args: Any, **kwargs: Any) -> str:
    value = args[0] if args else kwargs.get("agent") or kwargs.get("agentType") or kwargs.get("name", "agent")
    if isinstance(value, dict):
        value = value.get("name") or value.get("agentType") or value.get("type") or "agent"
    return str(value).replace("-", " ").replace("_", " ").title()


async def userFacingNameBackgroundColor(*args: Any, **kwargs: Any) -> str:
    name = (await userFacingName(*args, **kwargs)).lower()
    palette = ["blue", "green", "yellow", "magenta", "cyan", "gray"]
    return palette[sum(ord(ch) for ch in name) % len(palette)]


async def AgentPromptDisplay(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "agent-prompt", "agent": await userFacingName(data), "prompt": data.get("prompt", "")}


async def AgentResponseDisplay(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "agent-response",
        "agent": await userFacingName(data),
        "status": data.get("status", "completed"),
        "result": data.get("result") or data.get("content", ""),
    }


async def extractLastToolInfo(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    messages = list(args[0] if args else kwargs.get("messages", []) or [])
    for message in reversed(messages):
        if not isinstance(message, dict):
            continue
        name = message.get("name") or message.get("toolName") or message.get("tool_name")
        if name:
            return {"name": name, "status": message.get("status", "completed"), "message": message}
    return None


async def renderToolUseTag(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    name = data.get("name") or data.get("toolName") or "tool"
    return {"type": "tool-tag", "label": str(name), "status": data.get("status", "pending")}


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "tool-use", "tag": await renderToolUseTag(data), "input": data.get("input", {})}


async def renderToolUseProgressMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "tool-progress", "tag": await renderToolUseTag(data), "progress": data.get("progress")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "tool-result", "tag": await renderToolUseTag(data), "result": data.get("result")}


async def renderToolUseErrorMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "tool-error", "tag": await renderToolUseTag(data), "error": data.get("error") or data.get("message", "")}


async def renderToolUseRejectedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "tool-rejected", "tag": await renderToolUseTag(data), "reason": data.get("reason", "rejected")}


async def renderGroupedAgentToolUse(*args: Any, **kwargs: Any) -> dict[str, Any]:
    messages = list(args[0] if args else kwargs.get("messages", []) or [])
    rendered = []
    for message in messages:
        if isinstance(message, dict) and message.get("error"):
            rendered.append(await renderToolUseErrorMessage(message))
        elif isinstance(message, dict) and "result" in message:
            rendered.append(await renderToolResultMessage(message))
        else:
            rendered.append(await renderToolUseMessage(message if isinstance(message, dict) else {"message": message}))
    return {"type": "agent-tool-group", "count": len(rendered), "items": rendered}


__all__ = [
    "AgentPromptDisplay",
    "AgentResponseDisplay",
    "extractLastToolInfo",
    "renderGroupedAgentToolUse",
    "renderToolResultMessage",
    "renderToolUseErrorMessage",
    "renderToolUseMessage",
    "renderToolUseProgressMessage",
    "renderToolUseRejectedMessage",
    "renderToolUseTag",
    "userFacingName",
    "userFacingNameBackgroundColor",
]
