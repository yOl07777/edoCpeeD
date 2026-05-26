from __future__ import annotations

from typing import Any


async def useIdeAtMentioned(text: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    value = str(kwargs.get("text", text) or "")
    mentioned = "@ide" in value.lower() or "@editor" in value.lower()
    return {"provider": "deepseek", "mentioned": mentioned, "text": value}


__all__ = ["useIdeAtMentioned"]
