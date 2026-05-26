"""Local hooks configuration viewer."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from python_src.utils.settings.settings import getInitialSettings


async def getHooksStatus(cwd: str | None = None) -> dict[str, Any]:
    settings = await getInitialSettings(cwd)
    hooks = settings.get("hooks", {})
    if not isinstance(hooks, dict):
        hooks = {}
    deepseek_settings = Path(cwd or Path.cwd()) / ".deepseek" / "settings.json"
    legacy_settings = Path(cwd or Path.cwd()) / ".claude" / "settings.json"
    return {
        "provider": "deepseek",
        "hooks": hooks,
        "hookEvents": sorted(hooks.keys()),
        "settingsPaths": [str(deepseek_settings), str(legacy_settings)],
    }


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    cwd = context.get("cwd") if isinstance(context, dict) else None
    status = await getHooksStatus(cwd)
    count = len(status["hookEvents"])
    value = f"DeepSeek hook configuration: {count} event group(s) configured."
    if onDone:
        onDone(value)
    return {"type": "hooks", "value": value, "status": status}


hooks = {
    "type": "local",
    "name": "hooks",
    "description": "View DeepSeek hook configurations for tool events",
    "immediate": True,
    "source": "builtin",
    "supportsNonInteractive": True,
    "call": call,
}

default = hooks
