from __future__ import annotations

from typing import Any

from ._shared import get_global_config, has_skip_dangerous_prompt, mutate_global_config, update_user_settings


async def migrateBypassPermissionsAcceptedToSettings(*_args: Any, **_kwargs: Any) -> bool:
    """Move accepted dangerous-mode prompt flag into user settings."""

    config = await get_global_config()
    if not config.get("bypassPermissionsModeAccepted"):
        return False
    if not await has_skip_dangerous_prompt():
        await update_user_settings({"skipDangerousModePermissionPrompt": True})

    def remove_key(current: dict[str, Any]) -> dict[str, Any]:
        next_config = dict(current)
        next_config.pop("bypassPermissionsModeAccepted", None)
        return next_config

    await mutate_global_config(remove_key)
    return True
