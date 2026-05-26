from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def CompactSummary(*args: Any, **kwargs: Any) -> Any:
    summary = str(option(args, kwargs, "summary", scalar_arg(args, "")))
    messages = normalize_items(option(args, kwargs, "messages", []))
    return component_payload("compact_summary", summary=summary, messages=messages, messageCount=len(messages), compacted=bool(summary or messages))


__all__ = ["CompactSummary"]
