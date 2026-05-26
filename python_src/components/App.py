from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def App(*args: Any, **kwargs: Any) -> Any:
    children = normalize_items(option(args, kwargs, "children", scalar_arg(args)))
    return component_payload(
        "app",
        title=str(option(args, kwargs, "title", "DeepSeek Code")),
        children=children,
        childCount=len(children),
        interactive=bool(option(args, kwargs, "interactive", True)),
    )


__all__ = ["App"]
