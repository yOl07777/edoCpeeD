from __future__ import annotations

from typing import Any


_LANGUAGE_PLUGINS = {"python": "pyright", "typescript": "typescript-language-server", "javascript": "typescript-language-server"}


async def useLspPluginRecommendation(language: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    lang = str(kwargs.get("language", language) or "").lower()
    plugin = kwargs.get("plugin") or _LANGUAGE_PLUGINS.get(lang, "")
    return {"provider": "deepseek", "language": lang, "plugin": plugin, "recommended": bool(plugin)}


__all__ = ["useLspPluginRecommendation"]
