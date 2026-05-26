from __future__ import annotations

from typing import Any

from importlib import import_module


async def Ratchet(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    step = int(kwargs.get("step") or (args[0] if args else 0) or 0)
    total = int(kwargs.get("total", 4) or 4)
    return shared.ui_payload("ratchet", step=step, total=total, complete=step >= total)


__all__ = ["Ratchet"]
