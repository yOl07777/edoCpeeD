from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def useVimInput(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    mode = str(pick(options, "mode", default="insert"))
    key = pick(options, "key", default=None)
    if key == "esc":
        mode = "normal"
    elif key in {"i", "a"} and mode == "normal":
        mode = "insert"
    return {"provider": "deepseek", "mode": mode, "value": str(pick(options, "value", default="")), "handled": key is not None}
