from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def InvalidSettingsDialog(*args: Any, **kwargs: Any) -> Any:
    errors = normalize_items(option(args, kwargs, "errors", scalar_arg(args, [])))
    return component_payload("invalid_settings_dialog", settingsPath=str(option(args, kwargs, "path", ".deepseek/settings.json")), errors=errors, count=len(errors))


__all__ = ["InvalidSettingsDialog"]
