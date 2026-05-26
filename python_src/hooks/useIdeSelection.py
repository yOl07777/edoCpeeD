from __future__ import annotations

from typing import Any


async def useIdeSelection(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    selection = str(kwargs.get("selection", "") or "")
    path = str(kwargs.get("path", "") or "")
    return {"provider": "deepseek", "path": path, "selection": selection, "hasSelection": bool(selection)}


__all__ = ["useIdeSelection"]
