from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick, truthy


async def useCanSwitchToExistingSubscription(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    can_switch = truthy(pick(options, "canSwitch", "eligible", default=False))
    plan = str(pick(options, "plan", "subscription", default="existing DeepSeek plan"))
    return notification(
        visible=can_switch,
        title="Existing subscription available",
        message=f"You can switch this session to {plan}.",
        plan=plan,
    )
