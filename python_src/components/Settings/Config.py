from __future__ import annotations

from typing import Any

from python_src.components.Settings._shared import safe_config, settings_payload


async def Config(*args: Any, **kwargs: Any) -> Any:
    config = kwargs.get("config") or (args[0] if args else {}) or {}
    return settings_payload("settings_config", config=safe_config(config), keys=sorted(safe_config(config).keys()))


__all__ = ["Config"]
