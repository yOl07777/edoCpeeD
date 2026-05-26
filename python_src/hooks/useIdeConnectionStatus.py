from __future__ import annotations

from typing import Any


async def useIdeConnectionStatus(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    connected = bool(kwargs.get("connected", False))
    return {"provider": "deepseek", "connected": connected, "ide": str(kwargs.get("ide", "VS Code")), "status": "connected" if connected else "disconnected"}


__all__ = ["useIdeConnectionStatus"]
