"""Diagnostic screen shim for DeepSeek Code."""

from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any


def _env_present(name: str) -> bool:
    value = os.getenv(name)
    return bool(value and value.strip())


async def Doctor(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Return diagnostics similar to the TS Doctor screen.

    The TS version renders an interactive Ink panel.  This Python migration
    returns structured diagnostics so CLI code and tests can render it however
    they like.
    """

    cwd = Path(kwargs.get("cwd") or os.getcwd())
    if args and isinstance(args[0], dict):
        cwd = Path(args[0].get("cwd") or cwd)

    diagnostics = {
        "type": "doctor",
        "product": "DeepSeek Code",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": str(cwd),
        "config": {
            "hasDeepSeekApiKeys": _env_present("DEEPSEEK_API_KEYS"),
            "hasDeepSeekApiKey": _env_present("DEEPSEEK_API_KEY"),
            "defaultModel": os.getenv("DEFAULT_MODEL") or os.getenv("DEEPSEEK_MODEL"),
            "endpoints": [
                item.strip()
                for item in (os.getenv("DEEPSEEK_ENDPOINTS") or "https://api.deepseek.com").split(",")
                if item.strip()
            ],
        },
        "tools": {
            "git": shutil.which("git") is not None,
            "gh": shutil.which("gh") is not None,
            "python": shutil.which("python") is not None or shutil.which("py") is not None,
            "ripgrep": shutil.which("rg") is not None,
        },
        "settingsPaths": {
            "project": str(cwd / ".deepseek" / "settings.json"),
            "legacyClaude": str(cwd / ".claude" / "settings.json"),
        },
    }
    diagnostics["ok"] = bool(
        diagnostics["config"]["hasDeepSeekApiKeys"] or diagnostics["config"]["hasDeepSeekApiKey"]
    )
    return diagnostics


__all__ = ["Doctor"]
