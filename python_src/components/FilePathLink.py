from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, path_label, scalar_arg


async def FilePathLink(*args: Any, **kwargs: Any) -> Any:
    path = path_label(option(args, kwargs, "path", scalar_arg(args, "")))
    line = option(args, kwargs, "line", None)
    target = f"{path}:{line}" if line else path
    return component_payload("file_path_link", path=path, line=line, target=target, label=str(option(args, kwargs, "label", target)))


__all__ = ["FilePathLink"]
