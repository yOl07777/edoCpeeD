from __future__ import annotations

from typing import Any


async def PluginTrustWarning(*args: Any, **kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("source") or (args[0] if args else "unknown")
    return {
        "type": "plugin_trust_warning",
        "provider": "deepseek",
        "source": source,
        "message": "Review plugin source and manifest before enabling local code or tools.",
    }


__all__ = ["PluginTrustWarning"]
