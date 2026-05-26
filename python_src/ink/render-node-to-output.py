from __future__ import annotations

from typing import Any

_state: dict[str, Any] = {"layoutShifted": False, "scrollHint": None, "scrollDrainNode": None}


async def didLayoutShift(*args: Any, **kwargs: Any) -> Any:
    before = args[0] if args else kwargs.get("before")
    after = args[1] if len(args) > 1 else kwargs.get("after")
    shifted = before != after if before is not None or after is not None else bool(_state["layoutShifted"])
    _state["layoutShifted"] = shifted
    return shifted


async def resetLayoutShifted(*args: Any, **kwargs: Any) -> Any:
    _state["layoutShifted"] = False
    return False


async def getScrollHint(*args: Any, **kwargs: Any) -> Any:
    if args or "hint" in kwargs:
        _state["scrollHint"] = args[0] if args else kwargs.get("hint")
    return _state["scrollHint"]


async def resetScrollHint(*args: Any, **kwargs: Any) -> Any:
    _state["scrollHint"] = None
    return None


async def getScrollDrainNode(*args: Any, **kwargs: Any) -> Any:
    if args or "node" in kwargs:
        _state["scrollDrainNode"] = args[0] if args else kwargs.get("node")
    return _state["scrollDrainNode"]


async def resetScrollDrainNode(*args: Any, **kwargs: Any) -> Any:
    _state["scrollDrainNode"] = None
    return None


async def consumeFollowScroll(*args: Any, **kwargs: Any) -> Any:
    hint = _state.get("scrollHint")
    _state["scrollHint"] = None
    return {"provider": "deepseek", "consumed": hint is not None, "hint": hint}
