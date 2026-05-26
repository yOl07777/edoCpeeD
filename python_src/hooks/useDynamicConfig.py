from __future__ import annotations

import os
from typing import Any


async def useDynamicConfig(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    defaults = dict(kwargs.get("defaults", {}) or {})
    overrides = dict(kwargs.get("overrides", {}) or {})
    env_prefix = str(kwargs.get("envPrefix", "DEEPSEEK_"))
    env_values = {key[len(env_prefix) :].lower(): value for key, value in os.environ.items() if key.startswith(env_prefix)}
    config = {**defaults, **env_values, **overrides}
    return {"provider": "deepseek", "config": config, "keys": sorted(config)}


__all__ = ["useDynamicConfig"]
