from __future__ import annotations

import os
from typing import Any

from ._shared import update_user_settings, user_settings


async def migrateFennecToOpus(*_args: Any, **_kwargs: Any) -> bool:
    """Migrate removed first-party Fennec aliases to DeepSeek defaults."""

    if os.getenv("USER_TYPE") != "ant":
        return False
    model = (await user_settings()).get("model")
    if not isinstance(model, str):
        return False
    updates: dict[str, Any] | None = None
    if model.startswith(("fennec-fast-latest", "opus-4-5-fast")):
        updates = {"model": "deepseek-v4-flash", "fastMode": True}
    elif model.startswith(("fennec-latest[1m]", "fennec-latest")):
        updates = {"model": "deepseek-v4-pro"}
    if not updates:
        return False
    await update_user_settings(updates)
    return True
