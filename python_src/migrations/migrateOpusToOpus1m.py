from __future__ import annotations

from typing import Any

from ._shared import opus_1m_merge_enabled, update_user_settings, user_settings


async def migrateOpusToOpus1m(*_args: Any, **_kwargs: Any) -> bool:
    """Map the old Opus alias to DeepSeek Pro when merge behavior is enabled."""

    if not opus_1m_merge_enabled():
        return False
    if (await user_settings()).get("model") != "opus":
        return False
    await update_user_settings({"model": "deepseek-v4-pro"})
    return True
