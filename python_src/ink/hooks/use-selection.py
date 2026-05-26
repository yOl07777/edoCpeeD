from __future__ import annotations

from typing import Any


def _has_selection(selection: Any) -> bool:
    if not isinstance(selection, dict):
        return False
    return selection.get("anchor") is not None and selection.get("focus") is not None


async def useHasSelection(*args: Any, **kwargs: Any) -> Any:
    selection = args[0] if args else kwargs.get("selection", {})
    return _has_selection(selection)

async def useSelection(*args: Any, **kwargs: Any) -> Any:
    selection = dict(args[0] if args and isinstance(args[0], dict) else kwargs.get("selection", {}) or {})
    selection.setdefault("anchor", None)
    selection.setdefault("focus", None)
    selection.setdefault("isDragging", False)

    def clear() -> dict[str, Any]:
        selection.update({"anchor": None, "focus": None, "isDragging": False})
        return selection

    def start(col: int, row: int) -> dict[str, Any]:
        selection.update({"anchor": {"col": col, "row": row}, "focus": None, "isDragging": True})
        return selection

    def update(col: int, row: int) -> dict[str, Any]:
        selection.update({"focus": {"col": col, "row": row}})
        return selection

    return {
        "provider": "deepseek",
        "selection": selection,
        "hasSelection": _has_selection(selection),
        "clear": clear,
        "start": start,
        "update": update,
    }
