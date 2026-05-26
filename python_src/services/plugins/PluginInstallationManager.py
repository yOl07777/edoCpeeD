"""Background plugin installation status shim."""

from __future__ import annotations

from typing import Any, Callable


def _apply_state(setAppState: Callable[[Any], Any] | None, update: dict[str, Any]) -> None:
    if not callable(setAppState):
        return

    def reducer(prev: dict[str, Any] | None) -> dict[str, Any]:
        prev = dict(prev or {})
        plugins = dict(prev.get("plugins") or {})
        plugins.update(update)
        prev["plugins"] = plugins
        return prev

    setAppState(reducer)


async def performBackgroundPluginInstallations(*args: Any, **kwargs: Any) -> dict[str, Any]:
    setAppState = kwargs.get("setAppState") or (args[0] if args else None)
    declared = kwargs.get("declaredMarketplaces") or []
    marketplaces = [
        {"name": str(item.get("name") if isinstance(item, dict) else item), "status": "installed"}
        for item in declared
    ]
    status = {"installationStatus": {"marketplaces": marketplaces, "plugins": []}, "needsRefresh": False}
    _apply_state(setAppState, status)
    return {
        "performed": True,
        "installed": [item["name"] for item in marketplaces],
        "updated": [],
        "failed": [],
        "upToDate": [],
        "dryRun": True,
    }


__all__ = ["performBackgroundPluginInstallations"]
