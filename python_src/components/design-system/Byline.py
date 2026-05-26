from __future__ import annotations

from typing import Any

from importlib import import_module


async def Byline(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    items = kwargs.get("items") or list(args) or []
    return shared.ui_payload("byline", items=[str(item) for item in items], text=" · ".join(str(item) for item in items))


__all__ = ["Byline"]
