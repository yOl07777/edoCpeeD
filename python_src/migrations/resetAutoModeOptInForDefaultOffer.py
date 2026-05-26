from __future__ import annotations

from typing import Any

from ._shared import get_global_config, mutate_global_config, update_user_settings, user_settings


async def resetAutoModeOptInForDefaultOffer(*_args: Any, **_kwargs: Any) -> bool:
    """One-shot reset for old auto-mode opt-in state."""

    config = await get_global_config()
    if config.get("hasResetAutoModeOptInForDefaultOffer"):
        return False
    user = await user_settings()
    permissions = user.get("permissions") if isinstance(user.get("permissions"), dict) else {}
    if user.get("skipAutoPermissionPrompt") and permissions.get("defaultMode") != "auto":
        await update_user_settings({"skipAutoPermissionPrompt": None})
    await mutate_global_config(lambda current: {**current, "hasResetAutoModeOptInForDefaultOffer": True})
    return True
