"""Rate limit options command shim for DeepSeek quota handling."""

from __future__ import annotations

from typing import Any, Callable

from python_src.services.claudeAiLimits import getRawUtilization
from python_src.utils.auth import getRateLimitTier, getSubscriptionType


def _emit(onDone: Callable[..., Any] | None, message: str, options: dict[str, Any] | None = None) -> None:
    if not callable(onDone):
        return
    try:
        onDone(message, options) if options is not None else onDone(message)
    except TypeError:
        onDone(message)


async def getRateLimitOptions() -> list[dict[str, str]]:
    subscription = await getSubscriptionType()
    tier = await getRateLimitTier()
    options = [{"label": "Stop and wait for limit to reset", "value": "cancel"}]
    if subscription not in {"team", "enterprise"}:
        options.append({"label": "Upgrade your DeepSeek plan", "value": "upgrade"})
    if tier not in {"free", "trial"}:
        options.append({"label": "Switch to extra usage", "value": "extra-usage"})
    return options


async def call(onDone: Callable[..., Any] | None = None, _context: Any | None = None, args: str | None = None) -> dict[str, Any]:
    selected = (args or "").strip().lower()
    options = await getRateLimitOptions()
    quota = await getRawUtilization()
    if selected:
        if selected not in {option["value"] for option in options}:
            message = f'Unknown rate limit option "{selected}".'
            _emit(onDone, message, {"display": "system"})
            return {"type": "rate_limit_options", "selected": None, "options": options, "quota": quota, "error": message}
        message = "Rate limit option selected: " + selected
        _emit(onDone, message, {"display": "system"})
        return {"type": "rate_limit_options", "selected": selected, "options": options, "quota": quota}
    return {"type": "rate_limit_options", "selected": None, "options": options, "quota": quota}
