from __future__ import annotations

from typing import Any


def _count_chars(messages: list[dict[str, Any]]) -> int:
    return sum(len(str(message.get("content", ""))) for message in messages)


async def collectContextData(
    messages: list[dict[str, Any]] | None = None,
    *,
    tools: list[dict[str, Any]] | None = None,
    model: str = "deepseek-chat",
) -> dict[str, Any]:
    payload = messages or []
    return {
        "model": model,
        "message_count": len(payload),
        "char_count": _count_chars(payload),
        "estimated_tokens": max(1, _count_chars(payload) // 4) if payload else 0,
        "tool_count": len(tools or []),
    }


async def call(messages: list[dict[str, Any]] | None = None, **kwargs: Any) -> dict[str, Any]:
    return await collectContextData(messages, **kwargs)
