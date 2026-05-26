from __future__ import annotations

from typing import Any


async def useSelectionBgColor(*_args: Any, **kwargs: Any) -> str:
    return str(kwargs.get("color") or ("blue" if kwargs.get("active", True) else "gray"))


async def useCopyOnSelect(selection: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    text = str(kwargs.get("selection", selection) or "")
    enabled = bool(kwargs.get("enabled", True))
    copied = bool(text and enabled and kwargs.get("copy", True))
    return {"provider": "deepseek", "selection": text, "copied": copied, "bgColor": await useSelectionBgColor(active=bool(text))}


__all__ = ["useCopyOnSelect", "useSelectionBgColor"]
