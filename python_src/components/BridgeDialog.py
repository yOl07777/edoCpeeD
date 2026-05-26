from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def BridgeDialog(*args: Any, **kwargs: Any) -> Any:
    enabled = bool(option(args, kwargs, "enabled", True))
    connected = bool(option(args, kwargs, "connected", False))
    return component_payload("bridge_dialog", enabled=enabled, connected=connected, status="connected" if connected else "waiting")


__all__ = ["BridgeDialog"]
