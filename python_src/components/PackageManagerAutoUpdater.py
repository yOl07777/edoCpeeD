from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def PackageManagerAutoUpdater(*args: Any, **kwargs: Any) -> Any:
    manager = str(option(args, kwargs, "manager", option(args, kwargs, "packageManager", "pip")))
    current = str(option(args, kwargs, "currentVersion", option(args, kwargs, "current", "unknown")))
    latest = str(option(args, kwargs, "latestVersion", option(args, kwargs, "latest", current)))
    return component_payload("package_manager_auto_updater", manager=manager, currentVersion=current, latestVersion=latest, updateAvailable=current != latest, dryRun=True)


__all__ = ["PackageManagerAutoUpdater"]
