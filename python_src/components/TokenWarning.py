from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, percent, safe_int, scalar_arg


async def TokenWarning(*args: Any, **kwargs: Any) -> dict[str, Any]:
    used = safe_int(option(args, kwargs, "used", option(args, kwargs, "tokens", scalar_arg(args, 0))))
    limit = safe_int(option(args, kwargs, "limit", option(args, kwargs, "maxTokens", 0)))
    usage = percent(used, limit)
    return component_payload("token_warning", used=used, limit=limit, percent=usage, high=usage >= 80)


__all__ = ["TokenWarning"]
