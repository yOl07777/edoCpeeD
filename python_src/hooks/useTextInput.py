from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def useTextInput(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    value = str(pick(options, "value", default=""))
    cursor = max(0, min(int(pick(options, "cursor", default=len(value))), len(value)))
    insert = pick(options, "insert", default=None)
    key = pick(options, "key", default=None)
    if insert is not None:
        text = str(insert)
        value = value[:cursor] + text + value[cursor:]
        cursor += len(text)
    elif key == "backspace" and cursor > 0:
        value = value[: cursor - 1] + value[cursor:]
        cursor -= 1
    elif key == "left":
        cursor = max(0, cursor - 1)
    elif key == "right":
        cursor = min(len(value), cursor + 1)
    return {"provider": "deepseek", "value": value, "cursor": cursor}
