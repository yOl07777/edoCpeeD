from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def UserBashInputMessage(*args: Any, **kwargs: Any) -> Any:
    command = text_from(args[0] if args else None, **kwargs)
    return message_payload("user_bash_input_message", command=command, shell=kwargs.get("shell", "powershell"))


__all__ = ["UserBashInputMessage"]
