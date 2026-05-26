"""Local ultrareview quota helper."""

from __future__ import annotations

import time
from typing import Any

_QUOTA: dict[str, Any] = {"limit": 0, "used": 0, "remaining": 0, "reset_at": None, "updated_at": None}


async def fetchUltrareviewQuota(data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return or update local ultrareview quota data."""

    global _QUOTA
    if data is not None:
        limit = int(data.get("limit", _QUOTA.get("limit", 0)) or 0)
        used = int(data.get("used", _QUOTA.get("used", 0)) or 0)
        remaining = int(data.get("remaining", max(0, limit - used)) or 0)
        _QUOTA = {
            "limit": limit,
            "used": used,
            "remaining": remaining,
            "reset_at": data.get("reset_at", data.get("resetAt", _QUOTA.get("reset_at"))),
            "updated_at": time.time(),
            **data,
        }
    return dict(_QUOTA)

