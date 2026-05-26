from __future__ import annotations

from typing import Any

from python_src.commands.plugin._shared import extract_github_repo


async def PluginSelectionKeyHint(*args: Any, **kwargs: Any) -> dict[str, str]:
    return {"install": "i", "enable": "e", "disable": "d", "details": "enter"}


async def buildPluginDetailsMenuOptions(plugin: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    plugin = plugin or {}
    enabled = bool(plugin.get("enabled", True))
    return [
        {"label": "Enable", "value": "enable", "disabled": enabled},
        {"label": "Disable", "value": "disable", "disabled": not enabled},
        {"label": "Uninstall", "value": "uninstall"},
        {"label": "Validate", "value": "validate"},
    ]


async def extractGitHubRepo(value: str | None = None, *args: Any, **kwargs: Any) -> str | None:
    return extract_github_repo(value or kwargs.get("url") or kwargs.get("source"))


__all__ = ["PluginSelectionKeyHint", "buildPluginDetailsMenuOptions", "extractGitHubRepo"]
