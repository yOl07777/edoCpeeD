from __future__ import annotations

from typing import Any

from importlib import import_module


async def ThemedBox(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    theme_name = kwargs.get("theme", "dark")
    return shared.ui_payload(
        "themed_box",
        theme=theme_name,
        tokens=shared.theme(theme_name),
        content=kwargs.get("content") or (args[0] if args else None),
        padding=int(kwargs.get("padding", 0) or 0),
    )


__all__ = ["ThemedBox"]
