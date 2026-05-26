from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def useTeammateViewAutoExit(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    active = bool(pick(options, "active", default=False))
    teammate_count = int(pick(options, "teammateCount", "count", default=0))
    should_exit = active and teammate_count == 0
    return {"provider": "deepseek", "shouldExit": should_exit, "active": active, "teammateCount": teammate_count}
