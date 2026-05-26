from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def getTeleportErrors(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    errors = option(args, kwargs, "errors", scalar_arg(args, []))
    return normalize_items(errors, text_key="message")


async def TeleportError(*args: Any, **kwargs: Any) -> dict[str, Any]:
    errors = await getTeleportErrors(option(args, kwargs, "errors", scalar_arg(args, [])))
    first = errors[0] if errors else {}
    return component_payload(
        "teleport_error",
        errors=errors,
        count=len(errors),
        message=str(option(args, kwargs, "message", first.get("message", "")) or ""),
        retryable=bool(option(args, kwargs, "retryable", False)),
    )


__all__ = ["TeleportError", "getTeleportErrors"]
