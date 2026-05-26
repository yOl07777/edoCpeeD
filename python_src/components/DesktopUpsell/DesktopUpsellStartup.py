from __future__ import annotations

import os
from typing import Any


async def getDesktopUpsellConfig(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    enabled = str(os.environ.get("DEEPCODE_DESKTOP_UPSELL", kwargs.get("enabled", "0"))).lower() in {"1", "true", "yes"}
    return {
        "provider": "deepseek",
        "enabled": enabled,
        "source": "env" if "DEEPCODE_DESKTOP_UPSELL" in os.environ else "default",
        "message": "DeepSeek Code desktop integration is optional.",
    }


async def shouldShowDesktopUpsellStartup(*args: Any, **kwargs: Any) -> bool:
    config = await getDesktopUpsellConfig(*args, **kwargs)
    return bool(config["enabled"]) and not bool(kwargs.get("alreadyShown", False))


async def DesktopUpsellStartup(*args: Any, **kwargs: Any) -> dict[str, Any]:
    config = await getDesktopUpsellConfig(*args, **kwargs)
    return {
        "type": "desktop_upsell_startup",
        "provider": "deepseek",
        "config": config,
        "shouldShow": await shouldShowDesktopUpsellStartup(*args, **kwargs),
        "actions": ["dismiss", "open-settings"],
    }


__all__ = ["DesktopUpsellStartup", "getDesktopUpsellConfig", "shouldShowDesktopUpsellStartup"]
