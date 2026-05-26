from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def UserAgentNotificationMessage(*args: Any, **kwargs: Any) -> Any:
    text = text_from(args[0] if args else None, **kwargs)
    agent = str(kwargs.get("agent") or kwargs.get("agentName") or "agent")
    return message_payload("user_agent_notification_message", agent=agent, text=text)


__all__ = ["UserAgentNotificationMessage"]
