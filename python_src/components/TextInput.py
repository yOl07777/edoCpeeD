from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, safe_int, scalar_arg


async def TextInput(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = str(option(args, kwargs, "value", scalar_arg(args, "")) or "")
    cursor = safe_int(option(args, kwargs, "cursor", len(value)), len(value))
    cursor = max(0, min(cursor, len(value)))
    return component_payload(
        "text_input",
        value=value,
        cursor=cursor,
        placeholder=str(option(args, kwargs, "placeholder", "") or ""),
        multiline=bool(option(args, kwargs, "multiline", False)),
        submitted=bool(option(args, kwargs, "submitted", False)),
    )


_module_migration_placeholder = TextInput


__all__ = ["TextInput"]
