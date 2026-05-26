from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import logo_payload, normalize_feed_items, option, scalar_arg, visible_by_seen_count


async def OverageCreditUpsell(*args: Any, **kwargs: Any) -> Any:
    visibility = await useShowOverageCreditUpsell(*args, **kwargs)
    credits = option(args, kwargs, "credits", option(args, kwargs, "amount", scalar_arg(args, 0)))
    return logo_payload("overage_credit_upsell", visible=visibility["visible"], credits=credits, text=f"{credits} usage credits available.")


async def createOverageCreditFeed(*args: Any, **kwargs: Any) -> Any:
    credits = option(args, kwargs, "credits", option(args, kwargs, "amount", scalar_arg(args, 0)))
    rows = normalize_feed_items(
        [
            {"text": f"Usage credits available: {credits}", "tone": "success"},
            "Use /cost to inspect local session estimates",
        ]
    )
    return logo_payload("overage_credit_feed", items=rows, count=len(rows))


async def incrementOverageCreditUpsellSeenCount(*args: Any, **kwargs: Any) -> Any:
    current = int(option(args, kwargs, "seenCount", option(args, kwargs, "seen_count", scalar_arg(args, 0))) or 0)
    return logo_payload("overage_credit_seen_count", seenCount=current + 1)


async def isEligibleForOverageCreditGrant(*args: Any, **kwargs: Any) -> Any:
    if option(args, kwargs, "eligible", None) is not None:
        return bool(option(args, kwargs, "eligible"))
    credits = float(option(args, kwargs, "credits", option(args, kwargs, "amount", scalar_arg(args, 0))) or 0)
    plan = str(option(args, kwargs, "plan", "")).lower()
    return credits > 0 or plan in {"team", "pro", "enterprise"}


async def maybeRefreshOverageCreditCache(*args: Any, **kwargs: Any) -> Any:
    force = bool(option(args, kwargs, "force", False))
    ttl_expired = bool(option(args, kwargs, "ttlExpired", option(args, kwargs, "ttl_expired", False)))
    return logo_payload("overage_credit_cache", refreshed=force or ttl_expired, force=force, ttlExpired=ttl_expired)


async def shouldShowOverageCreditUpsell(*args: Any, **kwargs: Any) -> Any:
    return visible_by_seen_count(args, kwargs, default=True, max_seen=3) and await isEligibleForOverageCreditGrant(*args, **kwargs)


async def useShowOverageCreditUpsell(*args: Any, **kwargs: Any) -> Any:
    visible = await shouldShowOverageCreditUpsell(*args, **kwargs)
    credits = option(args, kwargs, "credits", option(args, kwargs, "amount", scalar_arg(args, 0)))
    return logo_payload("overage_credit_visibility", visible=visible, credits=credits)


__all__ = [
    "OverageCreditUpsell",
    "createOverageCreditFeed",
    "incrementOverageCreditUpsellSeenCount",
    "isEligibleForOverageCreditGrant",
    "maybeRefreshOverageCreditCache",
    "shouldShowOverageCreditUpsell",
    "useShowOverageCreditUpsell",
]
