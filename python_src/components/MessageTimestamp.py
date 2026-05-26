from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def MessageTimestamp(*args: Any, **kwargs: Any) -> Any:
    value = option(args, kwargs, "timestamp", scalar_arg(args, None))
    if isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(value, tz=timezone.utc)
    elif isinstance(value, datetime):
        dt = value
    elif value:
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            dt = datetime.now(timezone.utc)
    else:
        dt = datetime.now(timezone.utc)
    return component_payload("message_timestamp", iso=dt.isoformat(), text=dt.strftime("%Y-%m-%d %H:%M:%S"))


__all__ = ["MessageTimestamp"]
