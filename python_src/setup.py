"""Setup shim for the migrated DeepSeek runtime."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from deepseek_code.config import DeepSeekConfig


async def setup(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    cwd = Path(kwargs.get("cwd") or os.getcwd()).resolve()
    config = DeepSeekConfig.from_env()
    settings_dir = cwd / ".deepseek"
    if kwargs.get("createSettingsDir", True):
        settings_dir.mkdir(exist_ok=True)
    return {
        "type": "setup",
        "provider": "deepseek",
        "cwd": str(cwd),
        "settingsDir": str(settings_dir),
        "hasApiKey": bool(config.api_keys),
        "defaultModel": config.default_model,
        "endpointCount": len(config.endpoints),
        "createdSettingsDir": settings_dir.exists(),
    }


__all__ = ["setup"]
