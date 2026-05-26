from __future__ import annotations

from typing import Any


async def optimize(*args: Any, **kwargs: Any) -> Any:
    node = args[0] if args else kwargs.get("node")
    if isinstance(node, dict) and "children" in node:
        children = []
        for child in node.get("children", []) or []:
            optimized = await optimize(child)
            if optimized is not None:
                children.append(optimized)
        node["children"] = children
    return node
