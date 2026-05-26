from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, safe_int, scalar_arg


async def ScrollKeybindingHandler(*args: Any, **kwargs: Any) -> Any:
    key = str(option(args, kwargs, "key", scalar_arg(args, "")))
    action = await modalPagerAction(key)
    return component_payload("scroll_keybinding_handler", key=key, action=action, clearSelection=await shouldClearSelectionOnKey(key))


async def applyModalPagerAction(*args: Any, **kwargs: Any) -> Any:
    current = safe_int(option(args, kwargs, "current", args[0] if args else 0), 0)
    action = str(option(args, kwargs, "action", args[1] if len(args) > 1 else "none"))
    page = safe_int(option(args, kwargs, "page", 10), 10)
    maximum = safe_int(option(args, kwargs, "max", option(args, kwargs, "maximum", current)), current)
    delta = {"page_up": -page, "page_down": page, "up": -1, "down": 1, "top": -maximum, "bottom": maximum}.get(action, 0)
    return max(0, min(maximum, current + delta))


async def computeWheelStep(*args: Any, **kwargs: Any) -> Any:
    delta = safe_int(option(args, kwargs, "delta", scalar_arg(args, 0)), 0)
    base = await readScrollSpeedBase(**kwargs)
    return max(-base, min(base, delta))


async def dragScrollDirection(*args: Any, **kwargs: Any) -> Any:
    delta = safe_int(option(args, kwargs, "delta", scalar_arg(args, 0)), 0)
    return "down" if delta > 0 else "up" if delta < 0 else "none"


async def initWheelAccel(*args: Any, **kwargs: Any) -> Any:
    return {"type": "wheel_accel", "provider": "deepseek", "base": await readScrollSpeedBase(*args, **kwargs), "multiplier": 1}


async def jumpBy(*args: Any, **kwargs: Any) -> Any:
    current = safe_int(option(args, kwargs, "current", args[0] if args else 0), 0)
    delta = safe_int(option(args, kwargs, "delta", args[1] if len(args) > 1 else 0), 0)
    minimum = safe_int(option(args, kwargs, "min", 0), 0)
    maximum = safe_int(option(args, kwargs, "max", current + delta), current + delta)
    return max(minimum, min(maximum, current + delta))


async def modalPagerAction(*args: Any, **kwargs: Any) -> Any:
    key = str(option(args, kwargs, "key", scalar_arg(args, ""))).lower()
    return {
        "pagedown": "page_down",
        "pageup": "page_up",
        "j": "down",
        "down": "down",
        "k": "up",
        "up": "up",
        "home": "top",
        "end": "bottom",
    }.get(key, "none")


async def readScrollSpeedBase(*args: Any, **kwargs: Any) -> Any:
    return max(1, safe_int(option(args, kwargs, "base", scalar_arg(args, 3)), 3))


async def scrollUp(*args: Any, **kwargs: Any) -> Any:
    current = safe_int(option(args, kwargs, "current", scalar_arg(args, 0)), 0)
    amount = safe_int(option(args, kwargs, "amount", 1), 1)
    return max(0, current - amount)


async def selectionFocusMoveForKey(*args: Any, **kwargs: Any) -> Any:
    key = str(option(args, kwargs, "key", scalar_arg(args, ""))).lower()
    return {"j": 1, "down": 1, "k": -1, "up": -1}.get(key, 0)


async def shouldClearSelectionOnKey(*args: Any, **kwargs: Any) -> Any:
    key = str(option(args, kwargs, "key", scalar_arg(args, ""))).lower()
    return key in {"escape", "esc", "ctrl+c"}


__all__ = [
    "ScrollKeybindingHandler",
    "applyModalPagerAction",
    "computeWheelStep",
    "dragScrollDirection",
    "initWheelAccel",
    "jumpBy",
    "modalPagerAction",
    "readScrollSpeedBase",
    "scrollUp",
    "selectionFocusMoveForKey",
    "shouldClearSelectionOnKey",
]
