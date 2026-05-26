from __future__ import annotations

from typing import Any

from python_src.components.ManagedSettingsSecurityDialog.utils import extractDangerousSettings, formatDangerousSettingsList


async def ManagedSettingsSecurityDialog(*args: Any, **kwargs: Any) -> Any:
    settings = kwargs.get("settings") if "settings" in kwargs else (args[0] if args else {})
    dangerous = await extractDangerousSettings(settings)
    return {
        "type": "managed_settings_security_dialog",
        "provider": "deepseek",
        "dangerousSettings": dangerous,
        "hasDangerousSettings": bool(dangerous),
        "formatted": await formatDangerousSettingsList(dangerous),
        "actions": ["review", "accept", "cancel"],
    }


__all__ = ["ManagedSettingsSecurityDialog"]
