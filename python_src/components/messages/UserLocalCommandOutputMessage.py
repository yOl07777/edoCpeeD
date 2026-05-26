from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def UserLocalCommandOutputMessage(*args: Any, **kwargs: Any) -> Any:
    output = text_from(args[0] if args else None, **kwargs)
    return message_payload("user_local_command_output_message", output=output, exitCode=kwargs.get("exitCode", 0))


__all__ = ["UserLocalCommandOutputMessage"]
