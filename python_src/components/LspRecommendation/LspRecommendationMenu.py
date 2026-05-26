from __future__ import annotations

from typing import Any


async def LspRecommendationMenu(*args: Any, **kwargs: Any) -> Any:
    recommendations = kwargs.get("recommendations") or (args[0] if args else []) or []
    language = str(kwargs.get("language") or "")
    rows = []
    for item in recommendations:
        if isinstance(item, dict):
            name = str(item.get("name") or item.get("server") or item.get("id") or "")
            command = str(item.get("command") or "")
            languages = item.get("languages") or ([item.get("language")] if item.get("language") else [])
        else:
            name = str(item)
            command = ""
            languages = []
        if not language or not languages or language in languages:
            rows.append({"name": name, "command": command, "languages": languages, "selected": bool(item.get("selected", False)) if isinstance(item, dict) else False})
    return {
        "type": "lsp_recommendation_menu",
        "provider": "deepseek",
        "language": language,
        "recommendations": rows,
        "count": len(rows),
        "actions": ["install", "ignore", "details"],
    }


__all__ = ["LspRecommendationMenu"]
