from __future__ import annotations

from typing import Any

from ._shared import get_global_config, is_first_party, is_paid_subscriber, mutate_global_config, now_ms, update_user_settings, user_settings

LEGACY_SONNET_45_MODELS = {
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-5-20250929[1m]",
    "sonnet-4-5-20250929",
    "sonnet-4-5-20250929[1m]",
}


async def migrateSonnet45ToSonnet46(*_args: Any, **_kwargs: Any) -> bool:
    """Migrate explicit Sonnet 4.5 pins to DeepSeek chat/pro aliases."""

    if not is_first_party() or not is_paid_subscriber():
        return False
    model = (await user_settings()).get("model")
    if model not in LEGACY_SONNET_45_MODELS:
        return False
    has_1m = str(model).endswith("[1m]")
    await update_user_settings({"model": "deepseek-v4-pro" if has_1m else "deepseek-v4-flash"})
    if (await get_global_config()).get("numStartups", 0) > 1:
        await mutate_global_config(lambda current: {**current, "sonnet45To46MigrationTimestamp": now_ms()})
    return True
