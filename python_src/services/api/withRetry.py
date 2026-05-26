"""Retry helpers for DeepSeek/OpenAI compatible API calls."""

from __future__ import annotations

import random
import re
from typing import Any

BASE_DELAY_MS = 500


class CannotRetryError(Exception):
    """Raised when an API error should not be retried."""


class FallbackTriggeredError(Exception):
    """Raised when a request should be retried through a fallback target."""


def _status_code(error: Any) -> int | None:
    for attr in ("status_code", "status", "code"):
        value = getattr(error, attr, None)
        if isinstance(value, int):
            return value
        if isinstance(error, dict) and isinstance(error.get(attr), int):
            return error[attr]
    response = getattr(error, "response", None)
    value = getattr(response, "status_code", None)
    return value if isinstance(value, int) else None


async def getDefaultMaxRetries(config: dict[str, Any] | None = None) -> int:
    if config and "max_retries" in config:
        return int(config["max_retries"])
    if config and "maxRetries" in config:
        return int(config["maxRetries"])
    return 3


async def getRetryDelay(
    attempt: int,
    retry_after: float | int | None = None,
    base_delay_ms: int = BASE_DELAY_MS,
    jitter: bool = True,
) -> float:
    """Return retry delay in seconds using exponential backoff."""

    if retry_after is not None:
        return max(0.0, float(retry_after))
    delay_ms = base_delay_ms * (2 ** max(0, int(attempt)))
    if jitter:
        delay_ms *= 0.75 + random.random() * 0.5
    return delay_ms / 1000.0


async def is529Error(error: Any) -> bool:
    code = _status_code(error)
    message = str(error if not isinstance(error, dict) else error.get("message", "")).lower()
    return code == 529 or "overloaded" in message or "temporarily unavailable" in message


async def parseMaxTokensContextOverflowError(error: Any) -> dict[str, int] | None:
    """Parse context length/max token overflow details from provider messages."""

    message = str(error if not isinstance(error, dict) else error.get("message", ""))
    patterns = [
        r"context(?:\s+length)?\D+(?P<context>\d+)\D+maximum\D+(?P<maximum>\d+)",
        r"requested\s+(?P<context>\d+)\s+tokens\D+maximum\D+(?P<maximum>\d+)",
        r"(?P<context>\d+)\s+tokens.*?(?P<maximum>\d+)\s+tokens",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.I)
        if match:
            return {key: int(value) for key, value in match.groupdict().items()}
    return None

