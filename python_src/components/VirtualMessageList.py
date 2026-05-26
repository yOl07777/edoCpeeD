from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, safe_int, scalar_arg


async def VirtualMessageList(*args: Any, **kwargs: Any) -> dict[str, Any]:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    offset = max(0, safe_int(option(args, kwargs, "offset", 0)))
    limit = max(0, safe_int(option(args, kwargs, "limit", len(messages)), len(messages)))
    window = messages[offset : offset + limit] if limit else []
    return component_payload("virtual_message_list", messages=window, count=len(messages), offset=offset, limit=limit)


__all__ = ["VirtualMessageList"]
