from __future__ import annotations

from typing import Any


async def useAssistantHistory(messages: list[dict[str, Any]] | None = None, *_args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    rows = list(kwargs.get("messages", messages or []))
    return [message for message in rows if message.get("role") == "assistant"]


__all__ = ["useAssistantHistory"]
