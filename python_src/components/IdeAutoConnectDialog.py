from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def IdeAutoConnectDialog(*args: Any, **kwargs: Any) -> Any:
    ide = str(option(args, kwargs, "ide", "VS Code"))
    return component_payload("ide_auto_connect_dialog", ide=ide, visible=await shouldShowAutoConnectDialog(*args, **kwargs), action="enable_auto_connect")


async def IdeDisableAutoConnectDialog(*args: Any, **kwargs: Any) -> Any:
    ide = str(option(args, kwargs, "ide", "VS Code"))
    return component_payload("ide_disable_auto_connect_dialog", ide=ide, visible=await shouldShowDisableAutoConnectDialog(*args, **kwargs), action="disable_auto_connect")


async def shouldShowAutoConnectDialog(*args: Any, **kwargs: Any) -> Any:
    return bool(option(args, kwargs, "detected", True)) and not bool(option(args, kwargs, "autoConnect", option(args, kwargs, "auto_connect", False))) and not bool(option(args, kwargs, "dismissed", False))


async def shouldShowDisableAutoConnectDialog(*args: Any, **kwargs: Any) -> Any:
    return bool(option(args, kwargs, "autoConnect", option(args, kwargs, "auto_connect", False))) and bool(option(args, kwargs, "requestedDisable", option(args, kwargs, "requested_disable", False)))


__all__ = [
    "IdeAutoConnectDialog",
    "IdeDisableAutoConnectDialog",
    "shouldShowAutoConnectDialog",
    "shouldShowDisableAutoConnectDialog",
]
