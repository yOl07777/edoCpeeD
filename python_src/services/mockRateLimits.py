"""Mock rate limit state for local testing."""

from __future__ import annotations

import os
from typing import Any

_STATE: dict[str, Any] = {
    "scenario": None,
    "headers": {},
    "exceeded": [],
    "earlyWarning": None,
    "subscriptionType": None,
    "billingAccess": False,
}


async def setMockRateLimitScenario(scenario: str | None) -> dict[str, Any]:
    _STATE["scenario"] = scenario
    return await getMockStatus()


async def getCurrentMockScenario() -> str | None:
    return _STATE.get("scenario")


async def getScenarioDescription(scenario: str | None = None) -> str:
    scenario = scenario if scenario is not None else _STATE.get("scenario")
    descriptions = {
        "fast_mode": "Fast mode rate limit reached",
        "exceeded": "Configured mock rate limit exceeded",
        "warning": "Configured mock rate limit warning",
    }
    return descriptions.get(str(scenario), "No mock rate limit scenario")


async def isMockFastModeRateLimitScenario(scenario: str | None = None) -> bool:
    return (scenario if scenario is not None else _STATE.get("scenario")) in {"fast_mode", "fast-mode", "fast"}


async def checkMockFastModeRateLimit() -> dict[str, Any]:
    exceeded = await isMockFastModeRateLimitScenario()
    return {"limited": exceeded, "message": await getScenarioDescription("fast_mode") if exceeded else None}


async def addExceededLimit(limit_name: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"limit": limit_name, "details": details or {}}
    _STATE["exceeded"].append(entry)
    return entry


async def setMockHeader(name: str, value: Any) -> dict[str, str]:
    _STATE["headers"][str(name).lower()] = str(value)
    return await getMockHeaders()


async def getMockHeaders() -> dict[str, str]:
    return dict(_STATE["headers"])


async def applyMockHeaders(headers: dict[str, Any] | None = None) -> dict[str, str]:
    merged = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
    merged.update(await getMockHeaders())
    return merged


async def clearMockHeaders() -> None:
    _STATE["headers"].clear()


async def setMockEarlyWarning(warning: dict[str, Any] | str | None) -> Any:
    _STATE["earlyWarning"] = warning
    return warning


async def clearMockEarlyWarning() -> None:
    _STATE["earlyWarning"] = None


async def setMockSubscriptionType(subscription_type: str | None) -> str | None:
    _STATE["subscriptionType"] = subscription_type
    return subscription_type


async def getMockSubscriptionType() -> str | None:
    return _STATE.get("subscriptionType")


async def shouldUseMockSubscription() -> bool:
    return bool(_STATE.get("subscriptionType"))


async def setMockBillingAccess(enabled: bool) -> bool:
    _STATE["billingAccess"] = bool(enabled)
    return bool(_STATE["billingAccess"])


async def shouldProcessMockLimits() -> bool:
    env = os.getenv("DEEPSEEK_MOCK_RATE_LIMITS")
    return bool(_STATE.get("scenario") or _STATE["headers"] or _STATE["exceeded"] or str(env).lower() in {"1", "true", "yes"})


async def getMockHeaderless429Message() -> str:
    return "Mock DeepSeek rate limit reached without rate-limit headers."


async def getMockStatus() -> dict[str, Any]:
    return {
        "scenario": _STATE.get("scenario"),
        "headers": await getMockHeaders(),
        "exceeded": list(_STATE["exceeded"]),
        "earlyWarning": _STATE.get("earlyWarning"),
        "subscriptionType": _STATE.get("subscriptionType"),
        "billingAccess": bool(_STATE.get("billingAccess")),
    }
