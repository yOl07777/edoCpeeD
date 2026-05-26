from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, option, scalar_arg


async def MessageModel(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    model = message.get("model") if isinstance(message, dict) else scalar_arg(args, "deepseek-chat")
    return component_payload("message_model", model=str(option(args, kwargs, "model", model or "deepseek-chat")))


__all__ = ["MessageModel"]
