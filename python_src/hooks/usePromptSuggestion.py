from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick, text_filter


async def usePromptSuggestion(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    query = str(pick(options, "query", "input", default=""))
    suggestions = listify(
        pick(
            options,
            "suggestions",
            default=[
                "Review the current git diff",
                "Write tests for this module",
                "Explain the selected file",
            ],
        )
    )
    filtered = text_filter(suggestions, query)
    return {"provider": "deepseek", "query": query, "suggestions": filtered, "active": filtered[0] if filtered else None}
