from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def NativeAutoUpdater(*args: Any, **kwargs: Any) -> Any:
    current = str(option(args, kwargs, "currentVersion", option(args, kwargs, "current", "unknown")))
    latest = str(option(args, kwargs, "latestVersion", option(args, kwargs, "latest", current)))
    return component_payload("native_auto_updater", currentVersion=current, latestVersion=latest, updateAvailable=current != latest, native=True, dryRun=True)


__all__ = ["NativeAutoUpdater"]
