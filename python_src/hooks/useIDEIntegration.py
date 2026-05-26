from __future__ import annotations

from typing import Any


async def useIDEIntegration(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    return {
        "provider": "deepseek",
        "enabled": bool(kwargs.get("enabled", True)),
        "connected": bool(kwargs.get("connected", False)),
        "ide": str(kwargs.get("ide", "VS Code")),
        "dryRun": True,
    }


__all__ = ["useIDEIntegration"]
