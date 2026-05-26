from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def AdvisorMessage(*args: Any, **kwargs: Any) -> Any:
    text = text_from(args[0] if args else None, **kwargs)
    return message_payload("advisor_message", role="advisor", text=text, model=kwargs.get("model", "deepseek-chat"))


__all__ = ["AdvisorMessage"]
