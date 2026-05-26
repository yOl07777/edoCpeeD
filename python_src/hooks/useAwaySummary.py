from __future__ import annotations

from typing import Any


async def useAwaySummary(messages: list[dict[str, Any]] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    rows = list(kwargs.get("messages", messages or []))
    since = kwargs.get("since")
    recent = rows[int(since) :] if isinstance(since, int) else rows
    assistant = [item for item in recent if item.get("role") == "assistant"]
    tools = [item for item in recent if item.get("tool_calls") or item.get("toolName")]
    return {
        "provider": "deepseek",
        "messageCount": len(recent),
        "assistantCount": len(assistant),
        "toolCount": len(tools),
        "summary": f"{len(recent)} message(s), {len(tools)} tool event(s) while away.",
    }


__all__ = ["useAwaySummary"]
