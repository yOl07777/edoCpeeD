from __future__ import annotations

from typing import Any

from ._shared import is_first_party, legacy_model_remap_enabled, mutate_global_config, now_ms, update_user_settings, user_settings

LEGACY_OPUS_MODELS = {
    "claude-opus-4-20250514",
    "claude-opus-4-1-20250805",
    "claude-opus-4-0",
    "claude-opus-4-1",
    "opus",
    "opus[1m]",
}


async def migrateLegacyOpusToCurrent(*_args: Any, **_kwargs: Any) -> bool:
    """Clean legacy Opus/Claude model pins into a DeepSeek model alias."""

    if not is_first_party() or not legacy_model_remap_enabled():
        return False
    model = (await user_settings()).get("model")
    if model not in LEGACY_OPUS_MODELS:
        return False
    await update_user_settings({"model": "deepseek-v4-pro"})
    await mutate_global_config(lambda current: {**current, "legacyOpusMigrationTimestamp": now_ms()})
    return True
