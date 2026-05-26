from __future__ import annotations

from typing import Any

from importlib import import_module


async def ProgressBar(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    value = float(kwargs.get("value", kwargs.get("progress", args[0] if args else 0)) or 0)
    width = int(kwargs.get("width", 20) or 20)
    progress = shared.clamp(value)
    filled = round(progress * width)
    return shared.ui_payload(
        "progress_bar",
        value=progress,
        width=width,
        text="#" * filled + "-" * max(0, width - filled),
        percent=round(progress * 100),
    )


__all__ = ["ProgressBar"]
