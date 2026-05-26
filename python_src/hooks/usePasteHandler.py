from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def usePasteHandler(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    value = str(pick(options, "value", "text", default=""))
    pasted = str(pick(options, "paste", "clipboard", default=args[0] if args and not isinstance(args[0], dict) else ""))
    separator = str(pick(options, "separator", default=""))
    max_length = pick(options, "maxLength", default=None)
    combined = f"{value}{separator}{pasted}"
    truncated = False
    if max_length is not None and len(combined) > int(max_length):
        combined = combined[: int(max_length)]
        truncated = True
    return {
        "provider": "deepseek",
        "value": combined,
        "pasted": pasted,
        "truncated": truncated,
        "length": len(combined),
    }
