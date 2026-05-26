"""Renderable SkillTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "skill-use", "action": data.get("action", "list"), "name": data.get("name"), "skillsDir": data.get("skills_dir") or data.get("skillsDir")}


async def renderToolUseProgressMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "skill-progress", "action": data.get("action", "list"), "status": data.get("status", "loading")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    skills = list(data.get("skills") or [])
    content = str(data.get("content", ""))
    return {
        "type": "skill-result",
        "action": "read" if content else "list",
        "name": data.get("name"),
        "skills": skills,
        "count": len(skills),
        "content": content,
        "truncated": bool(data.get("truncated", False)),
    }


async def renderToolUseErrorMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "skill-error", "action": data.get("action"), "name": data.get("name"), "error": data.get("error") or data.get("message", "")}


async def renderToolUseRejectedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "skill-rejected", "action": data.get("action"), "name": data.get("name"), "reason": data.get("reason", "rejected")}


__all__ = [
    "renderToolResultMessage",
    "renderToolUseErrorMessage",
    "renderToolUseMessage",
    "renderToolUseProgressMessage",
    "renderToolUseRejectedMessage",
]
