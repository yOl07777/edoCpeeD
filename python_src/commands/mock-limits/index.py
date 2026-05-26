"""Local command shim for DeepSeek mock rate-limit state."""

from __future__ import annotations

from typing import Any, Callable

from python_src.services.mockRateLimits import (
    clearMockHeaders,
    getMockStatus,
    setMockBillingAccess,
    setMockEarlyWarning,
    setMockHeader,
    setMockRateLimitScenario,
    setMockSubscriptionType,
)


async def applyMockLimitArgs(args: str = "") -> dict[str, Any]:
    parts = args.strip().split()
    if not parts:
        return await getMockStatus()
    command = parts[0].lower()
    value = " ".join(parts[1:]).strip() or None
    if command in {"clear", "off", "reset"}:
        await setMockRateLimitScenario(None)
        await setMockEarlyWarning(None)
        await setMockSubscriptionType(None)
        await setMockBillingAccess(False)
        await clearMockHeaders()
    elif command in {"scenario", "set"}:
        await setMockRateLimitScenario(value)
    elif command == "warning":
        await setMockEarlyWarning(value)
    elif command == "subscription":
        await setMockSubscriptionType(value)
    elif command == "billing":
        await setMockBillingAccess(str(value).lower() in {"1", "true", "yes", "on"})
    elif command == "header" and value and "=" in value:
        name, header_value = value.split("=", 1)
        await setMockHeader(name.strip(), header_value.strip())
    return await getMockStatus()


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    status = await applyMockLimitArgs(args)
    value = f"DeepSeek mock limit status: scenario={status.get('scenario') or 'none'}"
    if onDone:
        onDone(value)
    return {"type": "mock_limits", "value": value, "status": status}


mock_limits = {
    "type": "local",
    "name": "mock-limits",
    "description": "Inspect or update local DeepSeek mock rate-limit state",
    "source": "builtin",
    "isHidden": True,
    "supportsNonInteractive": True,
    "call": call,
}

default = mock_limits
