from __future__ import annotations

from typing import Any

OSC8_PREFIX = "\x1b]8;"


class StylePool:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.items: list[Any] = [None]

    def intern(self, style: Any) -> int:
        if style in self.items:
            return self.items.index(style)
        self.items.append(style)
        return len(self.items) - 1

    def get(self, index: int) -> Any:
        return self.items[index] if 0 <= index < len(self.items) else None


class HyperlinkPool(StylePool):
    pass


class CharPool(StylePool):
    pass


def _cell(char: str = " ", styleId: int = 0, hyperlinkId: int = 0, noSelect: bool = False) -> dict[str, Any]:
    return {"char": char[:1] or " ", "styleId": styleId, "hyperlinkId": hyperlinkId, "noSelect": noSelect}


def _blank_row(columns: int) -> list[dict[str, Any]]:
    return [_cell() for _ in range(columns)]


def _dims(screen: dict[str, Any]) -> tuple[int, int]:
    return int(screen.get("columns", 0)), int(screen.get("rowsCount", len(screen.get("cells", []))))


async def createScreen(*args: Any, **kwargs: Any) -> Any:
    columns = int(args[0] if args else kwargs.get("columns", 80))
    rows = int(args[1] if len(args) > 1 else kwargs.get("rows", kwargs.get("height", 24)))
    cells = [_blank_row(columns) for _ in range(rows)]
    return {
        "provider": "deepseek",
        "columns": columns,
        "rowsCount": rows,
        "cells": cells,
        "stylePool": StylePool(),
        "hyperlinkPool": HyperlinkPool(),
        "charPool": CharPool(),
        "noSelectRegions": [],
    }


async def resetScreen(*args: Any, **kwargs: Any) -> Any:
    screen = args[0] if args else kwargs.get("screen", {})
    columns, rows = _dims(screen)
    screen["cells"] = [_blank_row(columns) for _ in range(rows)]
    return screen


async def cellAt(*args: Any, **kwargs: Any) -> Any:
    screen = args[0] if args else kwargs.get("screen", {})
    col = int(args[1] if len(args) > 1 else kwargs.get("col", 0))
    row = int(args[2] if len(args) > 2 else kwargs.get("row", 0))
    cells = screen.get("cells", [])
    if 0 <= row < len(cells) and 0 <= col < len(cells[row]):
        return cells[row][col]
    return None


async def cellAtIndex(*args: Any, **kwargs: Any) -> Any:
    screen = args[0] if args else kwargs.get("screen", {})
    index = int(args[1] if len(args) > 1 else kwargs.get("index", 0))
    columns, _ = _dims(screen)
    return await cellAt(screen, index % max(columns, 1), index // max(columns, 1))


async def visibleCellAtIndex(*args: Any, **kwargs: Any) -> Any:
    return await cellAtIndex(*args, **kwargs)


async def setCellAt(*args: Any, **kwargs: Any) -> Any:
    screen = args[0] if args else kwargs.get("screen", {})
    col = int(args[1] if len(args) > 1 else kwargs.get("col", 0))
    row = int(args[2] if len(args) > 2 else kwargs.get("row", 0))
    value = args[3] if len(args) > 3 else kwargs.get("value", kwargs.get("char", " "))
    cell = await cellAt(screen, col, row)
    if cell is None:
        return None
    if isinstance(value, dict):
        cell.update(value)
    else:
        cell["char"] = str(value)[:1] or " "
    return cell


async def setCellStyleId(*args: Any, **kwargs: Any) -> Any:
    cell = await setCellAt(*args[:3], **kwargs) if False else None
    screen = args[0] if args else kwargs.get("screen", {})
    col = int(args[1] if len(args) > 1 else kwargs.get("col", 0))
    row = int(args[2] if len(args) > 2 else kwargs.get("row", 0))
    style_id = int(args[3] if len(args) > 3 else kwargs.get("styleId", 0))
    cell = await cellAt(screen, col, row)
    if cell is not None:
        cell["styleId"] = style_id
    return cell


async def charInCellAt(*args: Any, **kwargs: Any) -> Any:
    cell = await cellAt(*args, **kwargs)
    return None if cell is None else cell.get("char", " ")


async def isCellEmpty(*args: Any, **kwargs: Any) -> Any:
    cell = args[0] if args else kwargs.get("cell")
    return not cell or cell.get("char", " ") == " "


async def isEmptyCellAt(*args: Any, **kwargs: Any) -> Any:
    return await isCellEmpty(await cellAt(*args, **kwargs))


async def clearRegion(*args: Any, **kwargs: Any) -> Any:
    screen = args[0] if args else kwargs.get("screen", {})
    x = int(kwargs.get("x", args[1] if len(args) > 1 else 0))
    y = int(kwargs.get("y", args[2] if len(args) > 2 else 0))
    width = int(kwargs.get("width", args[3] if len(args) > 3 else screen.get("columns", 0)))
    height = int(kwargs.get("height", args[4] if len(args) > 4 else screen.get("rowsCount", 0)))
    for row in range(y, y + height):
        for col in range(x, x + width):
            await setCellAt(screen, col, row, _cell())
    return screen


async def blitRegion(*args: Any, **kwargs: Any) -> Any:
    source = args[0] if args else kwargs.get("source")
    target = args[1] if len(args) > 1 else kwargs.get("target")
    x = int(kwargs.get("x", 0))
    y = int(kwargs.get("y", 0))
    for row_index, row in enumerate(source.get("cells", [])):
        for col_index, cell in enumerate(row):
            await setCellAt(target, x + col_index, y + row_index, dict(cell))
    return target


async def diff(*args: Any, **kwargs: Any) -> Any:
    before = args[0] if args else kwargs.get("before", {})
    after = args[1] if len(args) > 1 else kwargs.get("after", {})
    changes: list[dict[str, Any]] = []
    rows = max(len(before.get("cells", [])), len(after.get("cells", [])))
    for row in range(rows):
        b_row = before.get("cells", [])[row] if row < len(before.get("cells", [])) else []
        a_row = after.get("cells", [])[row] if row < len(after.get("cells", [])) else []
        for col in range(max(len(b_row), len(a_row))):
            old = b_row[col] if col < len(b_row) else None
            new = a_row[col] if col < len(a_row) else None
            if old != new:
                changes.append({"row": row, "col": col, "before": old, "after": new})
    return changes


async def diffEach(*args: Any, **kwargs: Any) -> Any:
    changes = await diff(*args, **kwargs)
    callback = kwargs.get("callback")
    if callable(callback):
        for change in changes:
            callback(change)
    return changes


async def extractHyperlinkFromStyles(*args: Any, **kwargs: Any) -> Any:
    styles = args[0] if args else kwargs.get("styles", "")
    if isinstance(styles, dict):
        return styles.get("hyperlink") or styles.get("url")
    text = str(styles)
    if OSC8_PREFIX in text:
        return text.split(";", 2)[-1].split("\x1b", 1)[0]
    return None


async def filterOutHyperlinkStyles(*args: Any, **kwargs: Any) -> Any:
    styles = args[0] if args else kwargs.get("styles", {})
    if isinstance(styles, dict):
        return {key: value for key, value in styles.items() if key not in {"hyperlink", "url"}}
    return str(styles).replace(OSC8_PREFIX, "")


async def markNoSelectRegion(*args: Any, **kwargs: Any) -> Any:
    screen = args[0] if args else kwargs.get("screen", {})
    region = {
        "x": int(kwargs.get("x", args[1] if len(args) > 1 else 0)),
        "y": int(kwargs.get("y", args[2] if len(args) > 2 else 0)),
        "width": int(kwargs.get("width", args[3] if len(args) > 3 else 0)),
        "height": int(kwargs.get("height", args[4] if len(args) > 4 else 0)),
    }
    screen.setdefault("noSelectRegions", []).append(region)
    for row in range(region["y"], region["y"] + region["height"]):
        for col in range(region["x"], region["x"] + region["width"]):
            cell = await cellAt(screen, col, row)
            if cell is not None:
                cell["noSelect"] = True
    return region


async def migrateScreenPools(*args: Any, **kwargs: Any) -> Any:
    screen = args[0] if args else kwargs.get("screen", {})
    return screen


async def shiftRows(*args: Any, **kwargs: Any) -> Any:
    screen = args[0] if args else kwargs.get("screen", {})
    delta = int(args[1] if len(args) > 1 else kwargs.get("delta", 0))
    cells = screen.get("cells", [])
    columns, rows = _dims(screen)
    if delta > 0:
        screen["cells"] = [_blank_row(columns) for _ in range(delta)] + cells[: max(0, rows - delta)]
    elif delta < 0:
        screen["cells"] = cells[-delta:] + [_blank_row(columns) for _ in range(-delta)]
    return screen
