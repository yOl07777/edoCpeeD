from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, path_label, scalar_arg


async def ClickableImageRef(*args: Any, **kwargs: Any) -> Any:
    path = path_label(option(args, kwargs, "path", option(args, kwargs, "src", scalar_arg(args, ""))))
    return component_payload("clickable_image_ref", path=path, label=str(option(args, kwargs, "label", path)), clickable=bool(path))


__all__ = ["ClickableImageRef"]
