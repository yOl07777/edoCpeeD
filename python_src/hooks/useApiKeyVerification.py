from __future__ import annotations

import os
from typing import Any


async def useApiKeyVerification(api_key: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    key = str(kwargs.get("api_key") or api_key or os.getenv("DEEPSEEK_API_KEY") or "").strip()
    keys = [item.strip() for item in os.getenv("DEEPSEEK_API_KEYS", "").split(",") if item.strip()]
    valid = bool(key) or bool(keys)
    source = "argument" if api_key or kwargs.get("api_key") else ("env" if key or keys else "missing")
    return {
        "provider": "deepseek",
        "valid": valid,
        "source": source,
        "count": len(keys) if keys else (1 if key else 0),
        "message": "DeepSeek API key configured" if valid else "Set DEEPSEEK_API_KEY or DEEPSEEK_API_KEYS",
    }


__all__ = ["useApiKeyVerification"]
