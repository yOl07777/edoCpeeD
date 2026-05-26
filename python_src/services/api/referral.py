"""Local referral and passes cache for migration compatibility."""

from __future__ import annotations

import time
from typing import Any

_PASSES_ELIGIBILITY: dict[str, Any] | None = None
_REFERRAL_ELIGIBILITY: dict[str, Any] | None = None
_REDEMPTIONS: list[dict[str, Any]] = []
_REFERRER_REWARD: dict[str, Any] | None = None


async def formatCreditAmount(amount: int | float | None, currency: str = "USD") -> str:
    value = float(amount or 0)
    symbol = "$" if currency.upper() == "USD" else f"{currency.upper()} "
    return f"{symbol}{value:,.2f}"


async def fetchAndStorePassesEligibility(data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Store locally supplied passes eligibility data."""

    global _PASSES_ELIGIBILITY, _REFERRER_REWARD
    data = data or {}
    remaining = int(data.get("remainingPasses", data.get("remaining_passes", 0)) or 0)
    reward_amount = float(data.get("rewardAmount", data.get("reward_amount", 0)) or 0)
    _PASSES_ELIGIBILITY = {
        "eligible": bool(data.get("eligible", remaining > 0)),
        "remainingPasses": remaining,
        "rewardAmount": reward_amount,
        "currency": data.get("currency", "USD"),
        "updated_at": time.time(),
        **data,
    }
    _REFERRER_REWARD = {
        "amount": reward_amount,
        "currency": _PASSES_ELIGIBILITY["currency"],
        "formatted": await formatCreditAmount(reward_amount, _PASSES_ELIGIBILITY["currency"]),
    }
    return dict(_PASSES_ELIGIBILITY)


async def checkCachedPassesEligibility(max_age_seconds: int | float | None = None) -> dict[str, Any] | None:
    if _PASSES_ELIGIBILITY is None:
        return None
    if max_age_seconds is not None and time.time() - float(_PASSES_ELIGIBILITY.get("updated_at", 0)) > max_age_seconds:
        return None
    return dict(_PASSES_ELIGIBILITY)


async def getCachedOrFetchPassesEligibility(data: dict[str, Any] | None = None) -> dict[str, Any]:
    cached = await checkCachedPassesEligibility()
    return cached if cached is not None else await fetchAndStorePassesEligibility(data)


async def prefetchPassesEligibility(data: dict[str, Any] | None = None) -> dict[str, Any]:
    return await fetchAndStorePassesEligibility(data)


async def getCachedRemainingPasses() -> int:
    cached = await checkCachedPassesEligibility()
    return int(cached.get("remainingPasses", 0)) if cached else 0


async def getCachedReferrerReward() -> dict[str, Any] | None:
    return dict(_REFERRER_REWARD) if _REFERRER_REWARD is not None else None


async def fetchReferralEligibility(data: dict[str, Any] | None = None) -> dict[str, Any]:
    global _REFERRAL_ELIGIBILITY
    data = data or {}
    _REFERRAL_ELIGIBILITY = {
        "eligible": bool(data.get("eligible", True)),
        "reason": data.get("reason"),
        "updated_at": time.time(),
        **data,
    }
    return dict(_REFERRAL_ELIGIBILITY)


async def fetchReferralRedemptions(redemptions: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    global _REDEMPTIONS
    if redemptions is not None:
        _REDEMPTIONS = [
            {
                "id": item.get("id", f"redemption-{index}"),
                "created_at": item.get("created_at", time.time()),
                **item,
            }
            for index, item in enumerate(redemptions)
        ]
    return list(_REDEMPTIONS)

