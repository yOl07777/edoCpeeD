from __future__ import annotations

import importlib
from typing import Any

screen_mod = importlib.import_module("python_src.ink.screen")
squash_mod = importlib.import_module("python_src.ink.squash-text-nodes")


async def scanPositions(*args: Any, **kwargs: Any) -> Any:
    text = str(args[0] if args else kwargs.get("text", ""))
    positions: list[dict[str, int | str]] = []
    row = int(kwargs.get("row", 0))
    col = int(kwargs.get("col", 0))
    for char in text:
        if char == "\n":
            row += 1
            col = 0
            continue
        positions.append({"char": char, "row": row, "col": col})
        col += 1
    return positions


async def applyPositionedHighlight(*args: Any, **kwargs: Any) -> Any:
    target = args[0] if args else kwargs.get("screen")
    positions = args[1] if len(args) > 1 else kwargs.get("positions", [])
    style_id = int(kwargs.get("styleId", 1))
    for pos in positions:
        cell = await screen_mod.cellAt(target, pos["col"], pos["row"])
        if cell is not None:
            cell["styleId"] = style_id
    return target


async def renderToScreen(*args: Any, **kwargs: Any) -> Any:
    node = args[0] if args else kwargs.get("node", "")
    columns = int(kwargs.get("columns", kwargs.get("width", 80)))
    rows = int(kwargs.get("rows", kwargs.get("height", 24)))
    target = kwargs.get("screen") or await screen_mod.createScreen(columns, rows)
    segments = await squash_mod.squashTextNodesToSegments(node)
    row = 0
    col = 0
    style_pool = target.get("stylePool")
    for segment in segments:
        style_id = style_pool.intern(segment.get("style", {})) if style_pool else 0
        for char in segment.get("text", ""):
            if char == "\n":
                row += 1
                col = 0
                continue
            if row >= rows:
                break
            await screen_mod.setCellAt(target, col, row, {"char": char, "styleId": style_id})
            col += 1
            if col >= columns:
                row += 1
                col = 0
        if row >= rows:
            break
    target["cursor"] = {"row": row, "col": col}
    return target
