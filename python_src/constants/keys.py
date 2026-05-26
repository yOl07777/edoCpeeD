from __future__ import annotations

import os
from typing import Any


async def getGrowthBookClientKey(*_args: Any, **_kwargs: Any) -> str:
    return os.getenv("DEEPSEEK_GROWTHBOOK_CLIENT_KEY") or os.getenv("GROWTHBOOK_CLIENT_KEY") or ""


__all__ = ["getGrowthBookClientKey"]
