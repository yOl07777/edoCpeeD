from __future__ import annotations

from typing import Any

from importlib import import_module


async def ListItem(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    label = kwargs.get("label") or (args[0] if args else "")
    return shared.ui_payload("list_item", label=str(label), selected=bool(kwargs.get("selected", False)), disabled=bool(kwargs.get("disabled", False)))


__all__ = ["ListItem"]
