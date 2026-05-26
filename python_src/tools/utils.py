from __future__ import annotations

from copy import deepcopy
from typing import Any


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _with(obj: Any, **updates: Any) -> Any:
    if isinstance(obj, dict):
        result = dict(obj)
        result.update(updates)
        return result
    result = deepcopy(obj)
    for key, value in updates.items():
        setattr(result, key, value)
    return result


def tagMessagesWithToolUseID(messages: list[Any], toolUseID: str | None) -> list[Any]:
    """Tag user messages with their source tool-use id."""

    if not toolUseID:
        return messages
    tagged: list[Any] = []
    for message in messages:
        tagged.append(_with(message, sourceToolUseID=toolUseID) if _get(message, "type") == "user" else message)
    return tagged


def getToolUseIDFromParentMessage(parentMessage: Any, toolName: str) -> str | None:
    """Extract a Claude-style tool_use id from a parent assistant message."""

    message = _get(parentMessage, "message", {})
    content = _get(message, "content", [])
    for block in content or []:
        if _get(block, "type") == "tool_use" and _get(block, "name") == toolName:
            tool_id = _get(block, "id")
            return str(tool_id) if tool_id is not None else None
    return None


__all__ = ["getToolUseIDFromParentMessage", "tagMessagesWithToolUseID"]
