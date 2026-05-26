from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def UserImageMessage(*args: Any, **kwargs: Any) -> Any:
    image = kwargs.get("image") or (args[0] if args else {})
    url = image.get("url") if isinstance(image, dict) else str(image)
    return message_payload("user_image_message", imageUrl=url, detail=kwargs.get("detail", "auto"))


__all__ = ["UserImageMessage"]
