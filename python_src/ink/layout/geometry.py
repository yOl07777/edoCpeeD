from __future__ import annotations

from typing import Any

ZERO_EDGES: dict[str, int] = {"top": 0, "right": 0, "bottom": 0, "left": 0}


def _rect(value: Any = None, **kwargs: Any) -> dict[str, int]:
    data = dict(value) if isinstance(value, dict) else {}
    data.update(kwargs)
    return {
        "x": int(data.get("x", data.get("left", 0)) or 0),
        "y": int(data.get("y", data.get("top", 0)) or 0),
        "width": max(0, int(data.get("width", 0) or 0)),
        "height": max(0, int(data.get("height", 0) or 0)),
    }


def _edge_value(value: Any) -> int:
    return int(value or 0)

async def addEdges(*args: Any, **kwargs: Any) -> Any:
    a = await edges(args[0] if args else kwargs.get("a", {}))
    b = await edges(args[1] if len(args) > 1 else kwargs.get("b", {}))
    return {key: a[key] + b[key] for key in ZERO_EDGES}

async def clamp(*args: Any, **kwargs: Any) -> Any:
    value = int(args[0] if args else kwargs.get("value", 0))
    minimum = int(args[1] if len(args) > 1 else kwargs.get("min", kwargs.get("minimum", 0)))
    maximum = int(args[2] if len(args) > 2 else kwargs.get("max", kwargs.get("maximum", value)))
    return max(minimum, min(maximum, value))

async def clampRect(*args: Any, **kwargs: Any) -> Any:
    rect = _rect(args[0] if args else kwargs.get("rect", {}))
    bounds = _rect(args[1] if len(args) > 1 else kwargs.get("bounds", {}))
    x = await clamp(rect["x"], bounds["x"], bounds["x"] + bounds["width"])
    y = await clamp(rect["y"], bounds["y"], bounds["y"] + bounds["height"])
    width = min(rect["width"], max(0, bounds["x"] + bounds["width"] - x))
    height = min(rect["height"], max(0, bounds["y"] + bounds["height"] - y))
    return {"x": x, "y": y, "width": width, "height": height}

async def edges(*args: Any, **kwargs: Any) -> Any:
    value = args[0] if args else kwargs
    if isinstance(value, (int, float)):
        amount = _edge_value(value)
        return {"top": amount, "right": amount, "bottom": amount, "left": amount}
    data = dict(value) if isinstance(value, dict) else {}
    vertical = data.get("vertical", data.get("y", 0))
    horizontal = data.get("horizontal", data.get("x", 0))
    return {
        "top": _edge_value(data.get("top", vertical)),
        "right": _edge_value(data.get("right", horizontal)),
        "bottom": _edge_value(data.get("bottom", vertical)),
        "left": _edge_value(data.get("left", horizontal)),
    }

async def resolveEdges(*args: Any, **kwargs: Any) -> Any:
    return await edges(args[0] if args else kwargs)

async def unionRect(*args: Any, **kwargs: Any) -> Any:
    rects = list(args) or list(kwargs.get("rects", []))
    if len(rects) == 1 and isinstance(rects[0], list):
        rects = rects[0]
    if not rects:
        return _rect()
    normalized = [_rect(rect) for rect in rects]
    left = min(rect["x"] for rect in normalized)
    top = min(rect["y"] for rect in normalized)
    right = max(rect["x"] + rect["width"] for rect in normalized)
    bottom = max(rect["y"] + rect["height"] for rect in normalized)
    return {"x": left, "y": top, "width": right - left, "height": bottom - top}

async def withinBounds(*args: Any, **kwargs: Any) -> Any:
    point = dict(args[0] if args else kwargs.get("point", {}))
    bounds = _rect(args[1] if len(args) > 1 else kwargs.get("bounds", {}))
    x = int(point.get("x", 0) or 0)
    y = int(point.get("y", 0) or 0)
    return bounds["x"] <= x < bounds["x"] + bounds["width"] and bounds["y"] <= y < bounds["y"] + bounds["height"]
