from __future__ import annotations

from typing import Any

from importlib import import_module


async def StatusIcon(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    status = str(kwargs.get("status") or (args[0] if args else "info"))
    glyphs = {"success": "OK", "error": "!!", "warning": "!!", "running": "..", "info": "i"}
    return shared.ui_payload("status_icon", status=status, glyph=glyphs.get(status, "i"))


__all__ = ["StatusIcon"]
