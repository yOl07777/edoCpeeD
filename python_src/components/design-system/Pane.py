from __future__ import annotations

from typing import Any

from importlib import import_module


async def Pane(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    return shared.ui_payload("pane", title=kwargs.get("title"), content=kwargs.get("content") or (args[0] if args else None), bordered=bool(kwargs.get("bordered", True)))


__all__ = ["Pane"]
