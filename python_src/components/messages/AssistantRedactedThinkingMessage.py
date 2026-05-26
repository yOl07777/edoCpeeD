from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def AssistantRedactedThinkingMessage(*_args: Any, **kwargs: Any) -> Any:
    return message_payload("assistant_redacted_thinking_message", role="assistant", redacted=True, reason=str(kwargs.get("reason") or "thinking redacted"))


__all__ = ["AssistantRedactedThinkingMessage"]
