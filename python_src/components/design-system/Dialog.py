from __future__ import annotations

from typing import Any

from importlib import import_module


async def Dialog(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    return shared.ui_payload(
        "dialog",
        title=str(kwargs.get("title") or "DeepSeek Code"),
        body=str(kwargs.get("body") or (args[0] if args else "")),
        actions=kwargs.get("actions") or ["ok"],
        open=bool(kwargs.get("open", True)),
    )


__all__ = ["Dialog"]
