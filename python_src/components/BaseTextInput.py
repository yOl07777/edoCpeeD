from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, safe_int, scalar_arg


async def BaseTextInput(*args: Any, **kwargs: Any) -> Any:
    value = str(option(args, kwargs, "value", scalar_arg(args, "")))
    cursor = safe_int(option(args, kwargs, "cursor", len(value)), len(value))
    placeholder = str(option(args, kwargs, "placeholder", ""))
    return component_payload("base_text_input", value=value, cursor=max(0, min(cursor, len(value))), placeholder=placeholder, empty=not value)


__all__ = ["BaseTextInput"]
