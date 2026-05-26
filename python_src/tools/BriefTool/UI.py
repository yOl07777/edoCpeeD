"""Renderable BriefTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    return {**(args[0] if args and isinstance(args[0], dict) else {}), **kwargs}


async def AttachmentList(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    attachments = list(data.get("attachments") or data.get("files") or [])
    return {"type": "brief-attachments", "count": len(attachments), "attachments": attachments}


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    attachments = list(data.get("attachments") or [])
    return {"type": "brief-use", "title": data.get("title") or "Brief", "attachmentCount": len(attachments)}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "brief-result",
        "ok": data.get("ok", True),
        "briefId": data.get("briefId") or data.get("id"),
        "attachmentCount": len(data.get("attachments") or []),
        "message": data.get("message", ""),
    }


__all__ = ["AttachmentList", "renderToolResultMessage", "renderToolUseMessage"]
