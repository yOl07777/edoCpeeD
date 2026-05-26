from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def IdeStatusIndicator(*args: Any, **kwargs: Any) -> Any:
    connected = bool(option(args, kwargs, "connected", False))
    ide = str(option(args, kwargs, "ide", "IDE"))
    return component_payload("ide_status_indicator", ide=ide, connected=connected, text=f"{ide}: {'connected' if connected else 'disconnected'}")


__all__ = ["IdeStatusIndicator"]
