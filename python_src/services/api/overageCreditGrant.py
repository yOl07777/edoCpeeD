"""Local overage credit grant cache."""

from __future__ import annotations

import time
from typing import Any

_GRANT: dict[str, Any] | None = None


async def formatGrantAmount(amount: int | float | None, currency: str = "USD") -> str:
    value = float(amount or 0)
    symbol = "$" if currency.upper() == "USD" else f"{currency.upper()} "
    return f"{symbol}{value:,.2f}"


async def refreshOverageCreditGrantCache(grant: dict[str, Any] | None = None) -> dict[str, Any]:
    global _GRANT
    _GRANT = {
        "amount": 0,
        "currency": "USD",
        "available": False,
        "updated_at": time.time(),
        **(grant or {}),
    }
    _GRANT["formatted"] = await formatGrantAmount(_GRANT.get("amount"), _GRANT.get("currency", "USD"))
    return dict(_GRANT)


async def getCachedOverageCreditGrant() -> dict[str, Any] | None:
    return dict(_GRANT) if _GRANT is not None else None


async def invalidateOverageCreditGrantCache() -> None:
    global _GRANT
    _GRANT = None

