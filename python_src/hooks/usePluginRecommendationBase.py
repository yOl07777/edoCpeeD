from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick


async def installPluginAndNotify(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    plugin = str(pick(options, "plugin", "name", default=args[0] if args and not isinstance(args[0], dict) else ""))
    return {
        "provider": "deepseek",
        "installed": bool(plugin),
        "plugin": plugin,
        "notification": f"Plugin {plugin} is ready for DeepSeek Code." if plugin else "No plugin selected.",
    }

async def usePluginRecommendationBase(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    installed = {str(item) for item in listify(pick(options, "installed", default=[]))}
    candidates = listify(pick(options, "candidates", "plugins", default=[]))
    recommendations = []
    for candidate in candidates:
        name = candidate.get("name") if isinstance(candidate, dict) else str(candidate)
        if name and name not in installed:
            recommendations.append(candidate if isinstance(candidate, dict) else {"name": name})
    return {
        "provider": "deepseek",
        "recommendations": recommendations,
        "count": len(recommendations),
        "dismissed": bool(pick(options, "dismissed", default=False)),
    }
