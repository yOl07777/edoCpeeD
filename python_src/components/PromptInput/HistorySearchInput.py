from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def HistorySearchInput(*args: Any, **kwargs: Any) -> Any:
    history = kwargs.get("history") or (args[0] if args else []) or []
    query = str(kwargs.get("query") or "")
    matches = [item for item in history if not query or query.lower() in str(item).lower()]
    return prompt_payload("history_search_input", query=query, matches=matches[:20], count=len(matches))


__all__ = ["HistorySearchInput"]
