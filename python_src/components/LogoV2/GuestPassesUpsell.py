from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import logo_payload, option, scalar_arg, visible_by_seen_count


async def GuestPassesUpsell(*args: Any, **kwargs: Any) -> Any:
    remaining = option(args, kwargs, "remaining", option(args, kwargs, "passes", scalar_arg(args, 0)))
    visible = await useShowGuestPassesUpsell(*args, **kwargs)
    return logo_payload(
        "guest_passes_upsell",
        visible=bool(visible["visible"]),
        remaining=remaining,
        text=f"{remaining} guest passes available for teammates.",
    )


async def incrementGuestPassesSeenCount(*args: Any, **kwargs: Any) -> Any:
    current = int(option(args, kwargs, "seenCount", option(args, kwargs, "seen_count", scalar_arg(args, 0))) or 0)
    return logo_payload("guest_passes_seen_count", seenCount=current + 1)


async def useShowGuestPassesUpsell(*args: Any, **kwargs: Any) -> Any:
    visible = visible_by_seen_count(args, kwargs, default=True, max_seen=3)
    remaining = option(args, kwargs, "remaining", option(args, kwargs, "passes", scalar_arg(args, 0)))
    return logo_payload("guest_passes_visibility", visible=visible and bool(remaining), remaining=remaining)


__all__ = ["GuestPassesUpsell", "incrementGuestPassesSeenCount", "useShowGuestPassesUpsell"]
