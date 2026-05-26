from __future__ import annotations

from typing import Any

from python_src.components.messages.UserToolResultMessage._shared import tool_result_payload


async def RejectedPlanMessage(*args: Any, **kwargs: Any) -> Any:
    reason = str(kwargs.get("reason") or (args[0] if args else "Plan was rejected."))
    return tool_result_payload("rejected_plan_message", status="rejected", reason=reason, summary=f"Plan rejected: {reason}")


__all__ = ["RejectedPlanMessage"]
