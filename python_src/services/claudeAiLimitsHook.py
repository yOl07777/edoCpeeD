"""Hook-style compatibility wrapper for quota status."""

from __future__ import annotations

from typing import Any

from .claudeAiLimits import checkQuotaStatus, getRawUtilization


async def useClaudeAiLimits(headers: dict[str, Any] | None = None, error: Any = None) -> dict[str, Any]:
    if headers is not None or error is not None:
        return await checkQuotaStatus(headers, error)
    return await getRawUtilization()
