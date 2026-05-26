from __future__ import annotations

import re
from typing import Any

URL_RE = re.compile(r"https?://[^\s)>\]]+")
WORD_RE = re.compile(r"[\w-]+", re.UNICODE)


def _point(col: int = 0, row: int = 0) -> dict[str, int]:
    return {"col": int(col), "row": int(row)}


def _rows(screen_or_rows: Any) -> list[str]:
    if isinstance(screen_or_rows, dict):
        if "rows" in screen_or_rows and all(isinstance(row, str) for row in screen_or_rows["rows"]):
            return list(screen_or_rows["rows"])
        if "cells" in screen_or_rows:
            return ["".join(cell.get("char", " ") for cell in row).rstrip() for row in screen_or_rows["cells"]]
    if isinstance(screen_or_rows, str):
        return screen_or_rows.splitlines()
    if isinstance(screen_or_rows, (list, tuple)):
        if all(isinstance(row, str) for row in screen_or_rows):
            return list(screen_or_rows)
        return ["".join(str(cell.get("char", cell)) for cell in row).rstrip() for row in screen_or_rows]
    return []


def _get(selection: dict[str, Any], name: str) -> dict[str, int] | None:
    value = selection.get(name)
    return value if isinstance(value, dict) else None


async def createSelectionState(*args: Any, **kwargs: Any) -> Any:
    return {
        "anchor": kwargs.get("anchor"),
        "focus": kwargs.get("focus"),
        "isDragging": bool(kwargs.get("isDragging", False)),
        "mode": kwargs.get("mode", "char"),
        "lastPressHadAlt": bool(kwargs.get("lastPressHadAlt", False)),
        "scrollbackRows": list(kwargs.get("scrollbackRows", [])),
    }


async def hasSelection(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    return bool(isinstance(selection, dict) and selection.get("anchor") and selection.get("focus"))


async def startSelection(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    col = args[1] if len(args) > 1 else kwargs.get("col", 0)
    row = args[2] if len(args) > 2 else kwargs.get("row", 0)
    selection.update({"anchor": _point(col, row), "focus": None, "isDragging": True, "mode": kwargs.get("mode", "char")})
    return selection


async def updateSelection(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    col = args[1] if len(args) > 1 else kwargs.get("col", 0)
    row = args[2] if len(args) > 2 else kwargs.get("row", 0)
    selection["focus"] = _point(col, row)
    return selection


async def moveFocus(*args: Any, **kwargs: Any) -> Any:
    return await updateSelection(*args, **kwargs)


async def finishSelection(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    selection["isDragging"] = False
    return selection


async def clearSelection(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    selection.update({"anchor": None, "focus": None, "isDragging": False})
    return selection


async def selectionBounds(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    anchor = _get(selection, "anchor")
    focus = _get(selection, "focus")
    if not anchor or not focus:
        return None
    a = (anchor["row"], anchor["col"])
    b = (focus["row"], focus["col"])
    start, end = (anchor, focus) if a <= b else (focus, anchor)
    return {"start": dict(start), "end": dict(end)}


async def isCellSelected(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    col = args[1] if len(args) > 1 else kwargs.get("col", 0)
    row = args[2] if len(args) > 2 else kwargs.get("row", 0)
    bounds = await selectionBounds(selection)
    if not bounds:
        return False
    start, end = bounds["start"], bounds["end"]
    if row < start["row"] or row > end["row"]:
        return False
    if start["row"] == end["row"]:
        return start["col"] <= col <= end["col"]
    if row == start["row"]:
        return col >= start["col"]
    if row == end["row"]:
        return col <= end["col"]
    return True


async def getSelectedText(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    rows = _rows(args[1] if len(args) > 1 else kwargs.get("screen", kwargs.get("rows", [])))
    bounds = await selectionBounds(selection)
    if not bounds:
        return ""
    start, end = bounds["start"], bounds["end"]
    selected: list[str] = []
    for row_index in range(start["row"], min(end["row"], len(rows) - 1) + 1):
        line = rows[row_index]
        left = start["col"] if row_index == start["row"] else 0
        right = end["col"] + 1 if row_index == end["row"] else len(line)
        selected.append(line[left:right])
    return "\n".join(selected)


async def applySelectionOverlay(*args: Any, **kwargs: Any) -> Any:
    screen = args[0] if args else kwargs.get("screen", {})
    selection = args[1] if len(args) > 1 else kwargs.get("selection", {})
    rows = _rows(screen)
    overlay = []
    for row, line in enumerate(rows):
        overlay.append("".join("^" if await isCellSelected(selection, col, row) else " " for col, _ in enumerate(line)))
    return {"provider": "deepseek", "rows": rows, "overlay": overlay}


async def captureScrolledRows(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    rows = _rows(args[1] if len(args) > 1 else kwargs.get("rows", []))
    selection.setdefault("scrollbackRows", []).extend(rows)
    return selection["scrollbackRows"]


async def extendSelection(*args: Any, **kwargs: Any) -> Any:
    return await updateSelection(*args, **kwargs)


async def shiftAnchor(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    delta = int(args[1] if len(args) > 1 else kwargs.get("delta", kwargs.get("rows", 0)))
    if isinstance(selection.get("anchor"), dict):
        selection["anchor"]["row"] += delta
    return selection


async def shiftSelection(*args: Any, **kwargs: Any) -> Any:
    selection = await shiftAnchor(*args, **kwargs)
    delta = int(args[1] if len(args) > 1 else kwargs.get("delta", kwargs.get("rows", 0)))
    if isinstance(selection.get("focus"), dict):
        selection["focus"]["row"] += delta
    return selection


async def shiftSelectionForFollow(*args: Any, **kwargs: Any) -> Any:
    return await shiftSelection(*args, **kwargs)


async def selectLineAt(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    rows = _rows(args[1] if len(args) > 1 else kwargs.get("screen", kwargs.get("rows", [])))
    row = int(args[2] if len(args) > 2 else kwargs.get("row", 0))
    line = rows[row] if 0 <= row < len(rows) else ""
    selection.update({"anchor": _point(0, row), "focus": _point(max(0, len(line) - 1), row), "isDragging": True, "mode": "line"})
    return selection


async def selectWordAt(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    rows = _rows(args[1] if len(args) > 1 else kwargs.get("screen", kwargs.get("rows", [])))
    col = int(args[2] if len(args) > 2 else kwargs.get("col", 0))
    row = int(args[3] if len(args) > 3 else kwargs.get("row", 0))
    line = rows[row] if 0 <= row < len(rows) else ""
    for match in WORD_RE.finditer(line):
        if match.start() <= col <= match.end():
            selection.update({"anchor": _point(match.start(), row), "focus": _point(match.end() - 1, row), "isDragging": True, "mode": "word"})
            return selection
    return await startSelection(selection, col, row)


async def findPlainTextUrlAt(*args: Any, **kwargs: Any) -> Any:
    rows = _rows(args[0] if args else kwargs.get("screen", kwargs.get("rows", [])))
    col = int(args[1] if len(args) > 1 else kwargs.get("col", 0))
    row = int(args[2] if len(args) > 2 else kwargs.get("row", 0))
    line = rows[row] if 0 <= row < len(rows) else ""
    for match in URL_RE.finditer(line):
        if match.start() <= col < match.end():
            return match.group(0)
    return None
