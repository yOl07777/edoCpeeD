from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def UserPlanMessage(*args: Any, **kwargs: Any) -> Any:
    plan = text_from(args[0] if args else None, **kwargs)
    return message_payload("user_plan_message", plan=plan, steps=[line for line in plan.splitlines() if line.strip()])


__all__ = ["UserPlanMessage"]
