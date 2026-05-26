from __future__ import annotations

import os
from typing import Any


SAFE_ENV_KEYS = [
    "DEEPSEEK_API_KEYS",
    "DEEPSEEK_MODELS",
    "DEEPSEEK_ENDPOINTS",
    "DEEPSEEK_BALANCE_STRATEGY",
    "DEFAULT_MODEL",
    "PYTHONPATH",
]


def _redact(key: str, value: str | None) -> str | None:
    if value is None:
        return None
    if "KEY" in key or "TOKEN" in key or "SECRET" in key:
        return "<set>" if value else ""
    return value


async def env_command(keys: list[str] | None = None) -> dict[str, Any]:
    selected = keys or SAFE_ENV_KEYS
    return {"env": {key: _redact(key, os.getenv(key)) for key in selected}}


call = env_command
