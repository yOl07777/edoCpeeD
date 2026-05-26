from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def UserBashOutputMessage(*args: Any, **kwargs: Any) -> Any:
    output = text_from(args[0] if args else None, **kwargs)
    exit_code = kwargs.get("exitCode", kwargs.get("exit_code", 0))
    return message_payload("user_bash_output_message", output=output, exitCode=exit_code, success=exit_code in {0, "0", None})


__all__ = ["UserBashOutputMessage"]
