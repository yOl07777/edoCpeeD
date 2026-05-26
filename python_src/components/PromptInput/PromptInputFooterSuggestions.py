from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


OVERLAY_MAX_ITEMS = 8


async def PromptInputFooterSuggestions(*args: Any, **kwargs: Any) -> Any:
    suggestions = kwargs.get("suggestions") or (args[0] if args else []) or []
    query = str(kwargs.get("query") or "")
    rows = [str(item) for item in suggestions if not query or query.lower() in str(item).lower()]
    return prompt_payload("prompt_input_footer_suggestions", suggestions=rows[:OVERLAY_MAX_ITEMS], count=len(rows), maxItems=OVERLAY_MAX_ITEMS)


__all__ = ["OVERLAY_MAX_ITEMS", "PromptInputFooterSuggestions"]
