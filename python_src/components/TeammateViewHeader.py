from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, option, scalar_arg


async def TeammateViewHeader(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = dict(first_options(args))
    name = str(option(args, kwargs, "name", data.get("displayName") or scalar_arg(args, "DeepSeek Code")) or "DeepSeek Code")
    status = str(option(args, kwargs, "status", data.get("state", "idle")) or "idle")
    return component_payload("teammate_view_header", name=name, status=status, subtitle=option(args, kwargs, "subtitle", data.get("subtitle", "")))


__all__ = ["TeammateViewHeader"]
