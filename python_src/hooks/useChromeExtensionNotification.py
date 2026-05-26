from __future__ import annotations

from typing import Any


async def useChromeExtensionNotification(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    installed = bool(kwargs.get("installed", False))
    dismissed = bool(kwargs.get("dismissed", False))
    visible = bool(kwargs.get("enabled", True)) and not installed and not dismissed
    return {
        "provider": "deepseek",
        "visible": visible,
        "installed": installed,
        "message": "Install the DeepSeek browser helper for page context." if visible else "",
    }


__all__ = ["useChromeExtensionNotification"]
