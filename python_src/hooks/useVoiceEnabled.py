from __future__ import annotations

import os
from typing import Any

from ._basic import first_mapping, normalize_bool, pick


async def useVoiceEnabled(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    configured = pick(options, "enabled", default=os.getenv("DEEPCODE_VOICE_ENABLED"))
    enabled = normalize_bool(configured, default=False)
    return {"provider": "deepseek", "enabled": enabled, "source": "argument" if "enabled" in options else "environment"}
