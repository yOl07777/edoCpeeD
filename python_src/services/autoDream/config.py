"""Auto-dream configuration."""

from __future__ import annotations

import os
from typing import Any

from python_src.utils.settings.settings import getInitialSettings


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


async def isAutoDreamEnabled(*_: Any, **__: Any) -> bool:
    settings = await getInitialSettings()
    if "autoDreamEnabled" in settings:
        return bool(settings["autoDreamEnabled"])
    if os.getenv("DEEPSEEK_AUTO_DREAM_ENABLED") is not None:
        return _truthy(os.getenv("DEEPSEEK_AUTO_DREAM_ENABLED"))
    return _truthy(os.getenv("TENGU_ONYX_PLOVER"))


__all__ = ["isAutoDreamEnabled"]
