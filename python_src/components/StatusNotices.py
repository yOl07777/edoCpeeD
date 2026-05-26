from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def StatusNotices(*args: Any, **kwargs: Any) -> Any:
    notices = normalize_items(option(args, kwargs, "notices", scalar_arg(args, [])))
    return component_payload("status_notices", notices=notices, count=len(notices), hasErrors=any(str(n.get("severity", "")).lower() == "error" for n in notices))


__all__ = ["StatusNotices"]
