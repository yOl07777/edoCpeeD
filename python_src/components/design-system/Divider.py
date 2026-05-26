from __future__ import annotations

from typing import Any

from importlib import import_module


async def Divider(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    width = int(kwargs.get("width") or (args[0] if args else 40) or 40)
    char = str(kwargs.get("char") or "-")[:1]
    label = kwargs.get("label")
    line = char * max(0, width)
    if label:
        label_text = f" {label} "
        start = max(0, (width - len(label_text)) // 2)
        line = line[:start] + label_text + line[start + len(label_text):]
    return shared.ui_payload("divider", width=width, text=line)


__all__ = ["Divider"]
