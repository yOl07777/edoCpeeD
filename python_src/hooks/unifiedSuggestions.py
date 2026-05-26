from __future__ import annotations

from typing import Any

from python_src.hooks.fileSuggestions import generateFileSuggestions


async def generateUnifiedSuggestions(query: Any = "", *_args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    text = str(kwargs.get("query", query) or "")
    commands = kwargs.get("commands", ["help", "status", "review", "commit"])
    suggestions: list[dict[str, Any]] = []
    if text.startswith("/"):
        needle = text[1:].lower()
        suggestions.extend(
            {"type": "command", "value": f"/{command}", "label": f"/{command}"}
            for command in commands
            if not needle or needle in str(command).lower()
        )
    elif text.startswith("@"):
        suggestions.extend(await generateFileSuggestions(text[1:], cwd=kwargs.get("cwd"), paths=kwargs.get("paths")))
    else:
        suggestions.extend({"type": "text", "value": item, "label": item} for item in kwargs.get("static", []) or [])
    return suggestions[: int(kwargs.get("limit", 20) or 20)]


__all__ = ["generateUnifiedSuggestions"]
