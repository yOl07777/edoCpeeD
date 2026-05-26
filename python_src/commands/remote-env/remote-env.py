"""Remote environment command shim."""

from __future__ import annotations

import os
from typing import Any, Callable

_SAFE_ENV_KEYS = (
    "DEEPSEEK_ENDPOINTS",
    "DEEPSEEK_MODELS",
    "DEFAULT_MODEL",
    "DEEPCODE_PROJECT_ROOT",
    "DEEPCODE_CONFIG_HOME",
    "DEEPSEEK_BALANCE_STRATEGY",
)


def _emit(onDone: Callable[..., Any] | None, message: str, options: dict[str, Any] | None = None) -> None:
    if not callable(onDone):
        return
    try:
        onDone(message, options) if options is not None else onDone(message)
    except TypeError:
        onDone(message)


async def call(onDone: Callable[..., Any] | None = None, _context: Any | None = None, args: str | None = None) -> dict[str, Any]:
    action = (args or "summary").strip().lower() or "summary"
    values = {key: os.getenv(key) for key in _SAFE_ENV_KEYS if os.getenv(key) is not None}
    result = {
        "type": "remote_env",
        "action": action,
        "available": bool(values),
        "env": values,
        "redacted": ["DEEPSEEK_API_KEY", "DEEPSEEK_API_KEYS"],
    }
    _emit(onDone, "Remote environment summary prepared.", {"display": "system"})
    return result
