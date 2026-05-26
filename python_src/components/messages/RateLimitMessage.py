from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def getUpsellMessage(*args: Any, **kwargs: Any) -> Any:
    model = str(kwargs.get("model") or (args[0] if args else "deepseek-chat"))
    return f"DeepSeek rate limit reached for {model}. Wait for reset or switch keys/models."


async def RateLimitMessage(*args: Any, **kwargs: Any) -> Any:
    reset = kwargs.get("resetAt") or kwargs.get("reset_at")
    model = str(kwargs.get("model") or (args[0] if args else "deepseek-chat"))
    return message_payload(
        "rate_limit_message",
        model=model,
        resetAt=reset,
        retryAfter=kwargs.get("retryAfter") or kwargs.get("retry_after"),
        message=await getUpsellMessage(model=model),
    )


__all__ = ["RateLimitMessage", "getUpsellMessage"]
