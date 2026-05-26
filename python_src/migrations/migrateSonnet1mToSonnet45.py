from __future__ import annotations

from typing import Any

from ._shared import get_global_config, mutate_global_config, update_user_settings, user_settings


async def migrateSonnet1mToSonnet45(*_args: Any, **_kwargs: Any) -> bool:
    """Mark legacy Sonnet 1M migration complete and map old alias to DeepSeek Pro."""

    if (await get_global_config()).get("sonnet1m45MigrationComplete"):
        return False
    if (await user_settings()).get("model") == "sonnet[1m]":
        await update_user_settings({"model": "deepseek-v4-pro"})
    await mutate_global_config(lambda current: {**current, "sonnet1m45MigrationComplete": True})
    return True
