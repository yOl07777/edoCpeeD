from __future__ import annotations

from typing import Any


async def useClipboardImageHint(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    has_image = bool(kwargs.get("hasImage", kwargs.get("has_image", False)))
    supported = bool(kwargs.get("supported", True))
    return {
        "provider": "deepseek",
        "visible": has_image and supported,
        "hasImage": has_image,
        "message": "Clipboard image ready to attach." if has_image and supported else "",
    }


__all__ = ["useClipboardImageHint"]
