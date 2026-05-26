from __future__ import annotations

from typing import Any


async def useInputBuffer(value: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    text = str(kwargs.get("value", value) or "")
    insert = str(kwargs.get("insert", "") or "")
    cursor = max(0, min(int(kwargs.get("cursor", len(text)) or 0), len(text)))
    if insert:
        text = text[:cursor] + insert + text[cursor:]
        cursor += len(insert)
    if kwargs.get("backspace") and cursor > 0:
        text = text[: cursor - 1] + text[cursor:]
        cursor -= 1
    return {"provider": "deepseek", "value": text, "cursor": cursor}


__all__ = ["useInputBuffer"]
