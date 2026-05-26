from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def AutoUpdater(*args: Any, **kwargs: Any) -> Any:
    current = str(option(args, kwargs, "currentVersion", option(args, kwargs, "current", "unknown")))
    latest = str(option(args, kwargs, "latestVersion", option(args, kwargs, "latest", current)))
    return component_payload("auto_updater", currentVersion=current, latestVersion=latest, updateAvailable=current != latest, dryRun=True)


__all__ = ["AutoUpdater"]
