from __future__ import annotations

from typing import Any


async def nullRenderingAttachments(*args: Any, **kwargs: Any) -> Any:
    attachments = kwargs.get("attachments") or (args[0] if args else []) or []
    return {"type": "null_rendering_attachments", "provider": "deepseek", "count": len(attachments), "rendered": False}


__all__ = ["nullRenderingAttachments"]
