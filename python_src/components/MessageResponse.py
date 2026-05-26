from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, option, scalar_arg
from python_src.components.Message import Message


async def MessageResponse(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    rendered = await Message(message)
    return component_payload("message_response", message=rendered, streaming=bool(option(args, kwargs, "streaming", False)))


__all__ = ["MessageResponse"]
