from __future__ import annotations

import os


async def isUltrareviewEnabled() -> bool:
    return os.getenv("DEEPSEEK_REVIEW_ENABLED", "1").lower() not in {"0", "false", "no"}
