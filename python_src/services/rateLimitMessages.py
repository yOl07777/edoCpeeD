"""Rate limit message helpers for DeepSeek/OpenAI-compatible responses."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

RATE_LIMIT_ERROR_PREFIXES = [
    "rate limit",
    "too many requests",
    "quota exceeded",
    "429",
    "insufficient quota",
]


def _reset_text(reset_at: Any = None) -> str:
    if reset_at is None:
        return "later"
    try:
        value = float(reset_at)
        if value > 10_000_000_000:
            value /= 1000
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OSError):
        return str(reset_at)


async def isRateLimitErrorMessage(message: str) -> bool:
    lowered = str(message or "").lower()
    return any(prefix in lowered for prefix in RATE_LIMIT_ERROR_PREFIXES)


async def getUsingOverageText(overage_enabled: bool = False, amount: str | None = None) -> str:
    if not overage_enabled:
        return ""
    return f" Using overage credits ({amount})." if amount else " Using overage credits."


async def getRateLimitMessage(
    limit_name: str = "requests",
    reset_at: Any = None,
    remaining: int | None = None,
    overage_enabled: bool = False,
) -> str:
    remaining_text = f" Remaining: {remaining}." if remaining is not None else ""
    overage = await getUsingOverageText(overage_enabled)
    return f"DeepSeek API rate limit reached for {limit_name}. Try again at {_reset_text(reset_at)}.{remaining_text}{overage}"


async def getRateLimitWarning(remaining: int | None = None, limit: int | None = None, reset_at: Any = None) -> str:
    if remaining is None:
        return "DeepSeek API rate limit is approaching."
    limit_text = f"/{limit}" if limit is not None else ""
    return f"DeepSeek API quota is low: {remaining}{limit_text} remaining until {_reset_text(reset_at)}."


async def getRateLimitErrorMessage(error: Any = None, headers: dict[str, Any] | None = None) -> str:
    headers = headers or {}
    message = str(error if not isinstance(error, dict) else error.get("message", ""))
    reset = headers.get("x-ratelimit-reset-requests") or headers.get("retry-after") or headers.get("x-ratelimit-reset")
    if await isRateLimitErrorMessage(message):
        return f"{message} " + await getRateLimitMessage(reset_at=reset)
    return await getRateLimitMessage(reset_at=reset)
