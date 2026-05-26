from __future__ import annotations

from typing import Any

from importlib import import_module


async def FuzzyPicker(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    items = kwargs.get("items") or (args[0] if args else []) or []
    query = str(kwargs.get("query") or "")
    matches = []
    for item in items:
        label = str(item.get("label", item.get("value", "")) if isinstance(item, dict) else item)
        if not query or query.lower() in label.lower():
            matches.append(item if isinstance(item, dict) else {"label": label, "value": item})
    return shared.ui_payload("fuzzy_picker", query=query, matches=matches, count=len(matches))


__all__ = ["FuzzyPicker"]
