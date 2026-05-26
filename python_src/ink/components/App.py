from __future__ import annotations

import time
from typing import Any


MULTI_CLICK_TIMEOUT_MS = 500
MULTI_CLICK_DISTANCE = 1


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _set(obj: Any, key: str, value: Any) -> None:
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)


def _call(fn: Any, *args: Any) -> Any:
    if callable(fn):
        return fn(*args)
    return None


def _props(app: Any) -> Any:
    return _get(app, "props", {})


def _selection(app: Any) -> Any:
    return _get(_props(app), "selection", {})


def _finish_selection(selection: Any) -> None:
    _set(selection, "isDragging", False)


def _has_selection(selection: Any) -> bool:
    return _get(selection, "anchor") is not None and _get(selection, "focus") is not None


def _start_selection(selection: Any, col: int, row: int) -> None:
    point = {"col": col, "row": row}
    _set(selection, "anchor", point)
    _set(selection, "focus", None)
    _set(selection, "isDragging", True)


async def handleMouseEvent(*args: Any, **kwargs: Any) -> Any:
    app = args[0] if args else kwargs.get("app")
    mouse = args[1] if len(args) > 1 else kwargs.get("mouse", kwargs.get("event", {}))
    if app is None:
        return {"handled": False, "reason": "missing_app"}

    props = _props(app)
    selection = _selection(app)
    col = int(_get(mouse, "col", 1)) - 1
    row = int(_get(mouse, "row", 1)) - 1
    button = int(_get(mouse, "button", 0))
    action = _get(mouse, "action", "press")
    base_button = button & 0x03
    is_motion = (button & 0x20) != 0

    if action == "press":
        if is_motion and base_button == 3:
            if _get(selection, "isDragging", False):
                _finish_selection(selection)
                _call(_get(props, "onSelectionChange"))
            if col == _get(app, "lastHoverCol", -1) and row == _get(app, "lastHoverRow", -1):
                return {"handled": True, "type": "hover_duplicate", "col": col, "row": row}
            _set(app, "lastHoverCol", col)
            _set(app, "lastHoverRow", row)
            _call(_get(props, "onHoverAt"), col, row)
            return {"handled": True, "type": "hover", "col": col, "row": row}

        if base_button != 0:
            _set(app, "clickCount", 0)
            return {"handled": True, "type": "non_left_press", "col": col, "row": row}

        if is_motion:
            _call(_get(props, "onSelectionDrag"), col, row)
            return {"handled": True, "type": "drag", "col": col, "row": row}

        if _get(selection, "isDragging", False):
            _finish_selection(selection)
            _call(_get(props, "onSelectionChange"))

        now = int(time.time() * 1000)
        near_last = (
            now - int(_get(app, "lastClickTime", 0)) < MULTI_CLICK_TIMEOUT_MS
            and abs(col - int(_get(app, "lastClickCol", -999))) <= MULTI_CLICK_DISTANCE
            and abs(row - int(_get(app, "lastClickRow", -999))) <= MULTI_CLICK_DISTANCE
        )
        click_count = int(_get(app, "clickCount", 0)) + 1 if near_last else 1
        _set(app, "clickCount", click_count)
        _set(app, "lastClickTime", now)
        _set(app, "lastClickCol", col)
        _set(app, "lastClickRow", row)

        if click_count >= 2:
            _set(app, "pendingHyperlinkTimer", None)
            count = 2 if click_count == 2 else 3
            _call(_get(props, "onMultiClick"), col, row, count)
            return {"handled": True, "type": "multi_click", "count": count, "col": col, "row": row}

        _start_selection(selection, col, row)
        _set(selection, "lastPressHadAlt", (button & 0x08) != 0)
        _call(_get(props, "onSelectionChange"))
        return {"handled": True, "type": "selection_start", "col": col, "row": row}

    if base_button != 0:
        if not _get(selection, "isDragging", False):
            return {"handled": False, "type": "non_left_release", "col": col, "row": row}
        _finish_selection(selection)
        _call(_get(props, "onSelectionChange"))
        return {"handled": True, "type": "selection_finish", "col": col, "row": row}

    _finish_selection(selection)
    opened_url = None
    if not _has_selection(selection) and _get(selection, "anchor") is not None:
        consumed = bool(_call(_get(props, "onClickAt"), col, row))
        if not consumed:
            opened_url = _call(_get(props, "getHyperlinkAt"), col, row)
            if opened_url:
                _call(_get(props, "onOpenHyperlink"), opened_url)

    _call(_get(props, "onSelectionChange"))
    return {"handled": True, "type": "release", "col": col, "row": row, "openedUrl": opened_url}


default = handleMouseEvent
