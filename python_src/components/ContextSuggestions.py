from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def ContextSuggestions(*args: Any, **kwargs: Any) -> Any:
    suggestions = normalize_items(option(args, kwargs, "suggestions", scalar_arg(args, [])))
    query = str(option(args, kwargs, "query", ""))
    if query:
        suggestions = [item for item in suggestions if query.lower() in str(item.get("text", "")).lower()]
    return component_payload("context_suggestions", suggestions=suggestions, count=len(suggestions), query=query)


__all__ = ["ContextSuggestions"]
