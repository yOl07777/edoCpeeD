from __future__ import annotations

from typing import Any


def _contains(node: dict[str, Any], col: int, row: int) -> bool:
    layout = node.get("layout", {})
    x = int(layout.get("left", layout.get("x", 0)))
    y = int(layout.get("top", layout.get("y", 0)))
    width = int(layout.get("width", 0))
    height = int(layout.get("height", 0))
    return x <= col < x + width and y <= row < y + height


async def hitTest(*args: Any, **kwargs: Any) -> Any:
    root = args[0] if args else kwargs.get("root")
    col = int(args[1] if len(args) > 1 else kwargs.get("col", 0))
    row = int(args[2] if len(args) > 2 else kwargs.get("row", 0))
    if not isinstance(root, dict) or not _contains(root, col, row):
        return None
    for child in reversed(root.get("children", []) or []):
        hit = await hitTest(child, col, row)
        if hit is not None:
            return hit
    return root


async def dispatchClick(*args: Any, **kwargs: Any) -> Any:
    root = args[0] if args else kwargs.get("root")
    col = int(args[1] if len(args) > 1 else kwargs.get("col", 0))
    row = int(args[2] if len(args) > 2 else kwargs.get("row", 0))
    node = await hitTest(root, col, row)
    handler = node and node.get("props", {}).get("onClick")
    if callable(handler):
        handler({"col": col, "row": row, "target": node})
        return True
    return False


async def dispatchHover(*args: Any, **kwargs: Any) -> Any:
    root = args[0] if args else kwargs.get("root")
    col = int(args[1] if len(args) > 1 else kwargs.get("col", 0))
    row = int(args[2] if len(args) > 2 else kwargs.get("row", 0))
    node = await hitTest(root, col, row)
    handler = node and node.get("props", {}).get("onHover")
    if callable(handler):
        handler({"col": col, "row": row, "target": node})
    return node
