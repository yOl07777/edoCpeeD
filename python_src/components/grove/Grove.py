from __future__ import annotations

from typing import Any


async def GroveDialog(*args: Any, **kwargs: Any) -> Any:
    return {
        "type": "grove_dialog",
        "provider": "deepseek",
        "title": str(kwargs.get("title") or "DeepSeek Code settings"),
        "body": str(kwargs.get("body") or (args[0] if args else "")),
        "open": bool(kwargs.get("open", True)),
    }


async def PrivacySettingsDialog(*_args: Any, **kwargs: Any) -> Any:
    return {
        "type": "privacy_settings_dialog",
        "provider": "deepseek",
        "telemetry": bool(kwargs.get("telemetry", False)),
        "transcriptShare": bool(kwargs.get("transcriptShare", False)),
        "actions": ["save", "cancel"],
    }


__all__ = ["GroveDialog", "PrivacySettingsDialog"]
