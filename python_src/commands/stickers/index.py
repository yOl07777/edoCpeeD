"""DeepSeek stickers command shim."""

from __future__ import annotations

from typing import Any, Callable

STICKER_URL = "https://www.deepseek.com"


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, str]:
    value = f"DeepSeek sticker ordering is not bundled with this Python migration. Visit: {STICKER_URL}"
    if onDone:
        onDone(value)
    return {"type": "text", "value": value, "url": STICKER_URL}


stickers = {
    "type": "local",
    "name": "stickers",
    "description": "Show DeepSeek sticker/community link",
    "source": "builtin",
    "supportsNonInteractive": True,
    "call": call,
}

default = stickers
