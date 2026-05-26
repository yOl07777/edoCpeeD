from __future__ import annotations

from typing import Any

from ._shared import get_global_config, get_merged_settings, is_first_party, is_pro_subscriber, mutate_global_config, now_ms


async def resetProToOpusDefault(*_args: Any, **_kwargs: Any) -> bool:
    """Mark old Pro-to-Opus migration complete for DeepSeek defaults."""

    config = await get_global_config()
    if config.get("opusProMigrationComplete"):
        return False
    updates: dict[str, Any] = {"opusProMigrationComplete": True}
    if is_first_party() and is_pro_subscriber() and (await get_merged_settings()).get("model") is None:
        updates["opusProMigrationTimestamp"] = now_ms()
    await mutate_global_config(lambda current: {**current, **updates})
    return True
