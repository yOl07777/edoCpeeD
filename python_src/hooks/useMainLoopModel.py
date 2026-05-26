from __future__ import annotations

import os
from typing import Any


async def useMainLoopModel(model: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    selected = str(kwargs.get("model", model or os.getenv("DEFAULT_MODEL") or "deepseek-chat"))
    return {"provider": "deepseek", "model": selected, "reasoning": selected in {"deepseek-reasoner"}}


__all__ = ["useMainLoopModel"]
