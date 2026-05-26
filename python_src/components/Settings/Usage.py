from __future__ import annotations

from typing import Any

from python_src.components.Settings._shared import settings_payload


async def Usage(*args: Any, **kwargs: Any) -> Any:
    usage = kwargs.get("usage") or (args[0] if args else {}) or {}
    if not isinstance(usage, dict):
        usage = {"value": usage}
    return settings_payload("settings_usage", usage=usage, totalTokens=usage.get("totalTokens", usage.get("tokens", 0)))


__all__ = ["Usage"]
