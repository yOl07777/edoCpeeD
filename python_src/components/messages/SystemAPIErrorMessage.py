from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def SystemAPIErrorMessage(*args: Any, **kwargs: Any) -> Any:
    error = kwargs.get("error") or (args[0] if args else "API error")
    status = kwargs.get("status") or kwargs.get("statusCode")
    return message_payload("system_api_error_message", role="system", error=str(error), status=status, retryable=bool(kwargs.get("retryable", False)))


__all__ = ["SystemAPIErrorMessage"]
