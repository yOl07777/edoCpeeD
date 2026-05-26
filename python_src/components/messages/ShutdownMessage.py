from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def getShutdownMessageSummary(*args: Any, **kwargs: Any) -> Any:
    reason = str(kwargs.get("reason") or (args[0] if args else "Session ended."))
    accepted = bool(kwargs.get("accepted", True))
    return f"Shutdown {'accepted' if accepted else 'rejected'}: {reason}"


async def ShutdownRequestDisplay(*args: Any, **kwargs: Any) -> Any:
    reason = str(kwargs.get("reason") or (args[0] if args else "Ready to exit."))
    return message_payload("shutdown_request_display", reason=reason, actions=["accept", "reject"])


async def ShutdownRejectedDisplay(*args: Any, **kwargs: Any) -> Any:
    reason = str(kwargs.get("reason") or (args[0] if args else "Shutdown rejected."))
    return message_payload("shutdown_rejected_display", reason=reason, accepted=False)


async def tryRenderShutdownMessage(*args: Any, **kwargs: Any) -> Any:
    accepted = bool(kwargs.get("accepted", True))
    reason = str(kwargs.get("reason") or (args[0] if args else "Session ended."))
    return message_payload("shutdown_message", accepted=accepted, reason=reason, summary=await getShutdownMessageSummary(reason, accepted=accepted))


__all__ = ["ShutdownRejectedDisplay", "ShutdownRequestDisplay", "getShutdownMessageSummary", "tryRenderShutdownMessage"]
