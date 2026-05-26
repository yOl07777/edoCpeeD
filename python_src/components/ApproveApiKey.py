from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, redact, scalar_arg


async def ApproveApiKey(*args: Any, **kwargs: Any) -> Any:
    key = option(args, kwargs, "apiKey", option(args, kwargs, "api_key", scalar_arg(args, "")))
    approved = bool(option(args, kwargs, "approved", False))
    return component_payload("approve_api_key", approved=approved, apiKeyPreview=redact(key), hasKey=bool(key))


__all__ = ["ApproveApiKey"]
