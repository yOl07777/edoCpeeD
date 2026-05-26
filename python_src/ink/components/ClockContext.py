from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ._nodes import normalize_children, render_node


ClockContext: dict[str, Any] = {"provider": "deepseek", "now": None, "timezone": "UTC"}


async def ClockProvider(*args: Any, **kwargs: Any) -> Any:
    prop_children = kwargs.pop("children", None)
    clock = await createClock(**kwargs)
    return render_node("clock_provider", context=clock, children=normalize_children(prop_children, *args))


async def createClock(*args: Any, **kwargs: Any) -> Any:
    now = kwargs.pop("now", None)
    if now is None:
        now = datetime.now(timezone.utc).isoformat()
    elif hasattr(now, "isoformat"):
        now = now.isoformat()
    return {"provider": "deepseek", "now": str(now), "timezone": kwargs.pop("timezone", "UTC"), **kwargs}


default = ClockProvider
