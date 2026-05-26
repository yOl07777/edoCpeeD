"""Eligibility wrapper for remote managed settings cache."""

from __future__ import annotations

import os
from typing import Any

from .syncCacheState import resetSyncCache as resetLeafCache
from .syncCacheState import setEligibility

_cached: bool | None = None


async def isRemoteManagedSettingsEligible(*args: Any, **kwargs: Any) -> bool:
    global _cached
    if _cached is not None:
        return _cached
    value = os.getenv("DEEPCODE_REMOTE_MANAGED_SETTINGS_ELIGIBLE") or os.getenv("DEEPSEEK_REMOTE_MANAGED_SETTINGS_ELIGIBLE")
    _cached = True if value is None else value.lower() in {"1", "true", "yes", "on"}
    await setEligibility(_cached)
    return _cached


async def resetSyncCache(*args: Any, **kwargs: Any) -> None:
    global _cached
    _cached = None
    await resetLeafCache()


__all__ = ["isRemoteManagedSettingsEligible", "resetSyncCache"]
