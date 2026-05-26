"""Session tag command shim."""

from __future__ import annotations

import re
from typing import Any, Callable

from python_src.bootstrap.state import getSessionId
from python_src.utils.config import getCurrentProjectConfig, saveCurrentProjectConfig

HELP = """Usage: /tag <tag-name>

Toggle a searchable tag on the current session.
Run the same command again to remove the tag.

Examples:
  /tag bugfix
  /tag feature-auth
  /tag wip"""


def _emit(onDone: Callable[..., Any] | None, message: str, options: dict[str, Any] | None = None) -> None:
    if not callable(onDone):
        return
    try:
        onDone(message, options) if options is not None else onDone(message)
    except TypeError:
        onDone(message)


def _sanitize_tag(tag: str) -> str:
    text = re.sub(r"[\x00-\x1f\x7f]", "", tag).strip()
    text = re.sub(r"\s+", "-", text)
    return text[:80]


async def getCurrentSessionTag(session_id: str | None = None) -> str | None:
    config = await getCurrentProjectConfig()
    tags = config.get("sessionTags") or {}
    return tags.get(session_id or getSessionId())


async def saveTag(session_id: str, tag: str) -> dict[str, Any]:
    config = await getCurrentProjectConfig()
    tags = dict(config.get("sessionTags") or {})
    if tag:
        tags[session_id] = tag
    else:
        tags.pop(session_id, None)
    return await saveCurrentProjectConfig({"sessionTags": tags})


async def call(onDone: Callable[..., Any] | None = None, _context: Any | None = None, args: str | None = None) -> dict[str, Any] | None:
    trimmed = (args or "").strip()
    if trimmed in {"", "-h", "--help", "help", "?"}:
        _emit(onDone, HELP, {"display": "system"})
        return {"type": "tag_help", "message": HELP}

    session_id = getSessionId()
    tag = _sanitize_tag(trimmed)
    if not session_id:
        _emit(onDone, "No active session to tag", {"display": "system"})
        return None
    if not tag:
        _emit(onDone, "Tag name cannot be empty", {"display": "system"})
        return None
    current = await getCurrentSessionTag(session_id)
    if current == tag:
        await saveTag(session_id, "")
        message = f"Removed tag #{tag}"
        action = "removed"
    else:
        await saveTag(session_id, tag)
        message = f"Tagged session with #{tag}"
        action = "added"
    _emit(onDone, message, {"display": "system"})
    return {"type": "tag", "action": action, "sessionId": session_id, "tag": tag}
