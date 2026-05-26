"""Bootstrap data for the local DeepSeek Python runtime."""

from __future__ import annotations

import os
from typing import Any


async def fetchBootstrapData(config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or {}
    model = config.get("model") or os.getenv("DEFAULT_MODEL", "deepseek-chat")
    endpoint = config.get("endpoint") or os.getenv("DEEPSEEK_ENDPOINTS", "https://api.deepseek.com").split(",", 1)[0]
    return {
        "provider": "deepseek",
        "model": model,
        "endpoint": endpoint,
        "features": {
            "tools": True,
            "streaming": True,
            "mcp": True,
            "analytics": True,
        },
        "config": config,
    }

