from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, path_label, scalar_arg


async def ShowInIDEPrompt(*args: Any, **kwargs: Any) -> Any:
    path = path_label(option(args, kwargs, "path", scalar_arg(args, "")))
    ide = str(option(args, kwargs, "ide", "IDE"))
    return component_payload("show_in_ide_prompt", path=path, ide=ide, command=f"open {path}" if path else "")


__all__ = ["ShowInIDEPrompt"]
