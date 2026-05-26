"""Guest passes command shim."""

from __future__ import annotations

from typing import Any, Callable

from python_src.services.api.referral import getCachedRemainingPasses
from python_src.utils.config import getGlobalConfig, saveGlobalConfig


async def call(onDone: Callable[..., Any] | None = None, *_: Any, **__: Any) -> dict[str, Any]:
    config = await getGlobalConfig()
    is_first_visit = not bool(config.get("hasVisitedPasses"))
    remaining = await getCachedRemainingPasses()
    if is_first_visit:
        config["hasVisitedPasses"] = True
        config["passesLastSeenRemaining"] = remaining if remaining is not None else config.get("passesLastSeenRemaining")
        await saveGlobalConfig(config)
    result = {
        "type": "passes",
        "isFirstVisit": is_first_visit,
        "remaining": remaining,
        "onDone": onDone,
        "message": f"{remaining} guest pass{'es' if remaining != 1 else ''} remaining",
    }
    return result
