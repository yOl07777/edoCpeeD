from __future__ import annotations

from typing import Any

from importlib import import_module


async def LoadingState(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    return shared.ui_payload("loading_state", message=str(kwargs.get("message") or (args[0] if args else "Loading")), active=bool(kwargs.get("active", True)))


__all__ = ["LoadingState"]
