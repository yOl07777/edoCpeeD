from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def formatTeammateMessageContent(*args: Any, **kwargs: Any) -> Any:
    return text_from(args[0] if args else None, **kwargs)


async def PlanApprovalRequestDisplay(*args: Any, **kwargs: Any) -> Any:
    plan = await formatTeammateMessageContent(args[0] if args else kwargs.get("plan", ""))
    return message_payload("plan_approval_request_display", plan=plan, actions=["approve", "reject", "edit"])


async def PlanApprovalResponseDisplay(*args: Any, **kwargs: Any) -> Any:
    approved = bool(kwargs.get("approved", args[0] if args else False))
    reason = str(kwargs.get("reason") or "")
    return message_payload("plan_approval_response_display", approved=approved, reason=reason)


async def tryRenderPlanApprovalMessage(*args: Any, **kwargs: Any) -> Any:
    if kwargs.get("response") is not None:
        return await PlanApprovalResponseDisplay(kwargs.get("response"), reason=kwargs.get("reason", ""))
    return await PlanApprovalRequestDisplay(kwargs.get("plan") or (args[0] if args else ""))


__all__ = [
    "PlanApprovalRequestDisplay",
    "PlanApprovalResponseDisplay",
    "formatTeammateMessageContent",
    "tryRenderPlanApprovalMessage",
]
