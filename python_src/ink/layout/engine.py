from __future__ import annotations

from typing import Any

async def createLayoutNode(*args: Any, **kwargs: Any) -> Any:
    style = dict(args[0] if args and isinstance(args[0], dict) else kwargs.get("style", {}) or {})
    children = list(kwargs.get("children", []))
    width = int(style.get("width", kwargs.get("width", 0)) or 0)
    height = int(style.get("height", kwargs.get("height", 0)) or 0)
    node = {
        "provider": "deepseek",
        "type": "layout_node",
        "style": style,
        "children": children,
        "layout": {"x": int(style.get("x", 0) or 0), "y": int(style.get("y", 0) or 0), "width": width, "height": height},
    }
    return node
