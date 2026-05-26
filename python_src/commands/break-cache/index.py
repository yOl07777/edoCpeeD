"""Local DeepSeek cache-break shim.

DeepSeek's OpenAI-compatible API does not expose Claude-style prompt cache
control, so this command returns an explicit no-op marker that can be inserted
into a prompt when a caller wants to avoid reuse by an upstream compatible
gateway.
"""

from __future__ import annotations

import secrets
from typing import Any, Callable


def createCacheBreaker(label: str = "") -> str:
    suffix = f":{label.strip()}" if label and label.strip() else ""
    return f"DEEPSEEK_CACHE_BREAKER{suffix}:{secrets.token_hex(8)}"


async def call(onDone: Callable[[str], Any] | None = None, context: Any | None = None, args: str = "") -> dict[str, str]:
    marker = createCacheBreaker(args)
    value = (
        "DeepSeek does not use Claude prompt cache controls. "
        f"Use this local marker only if an OpenAI-compatible gateway needs a prompt variation:\n{marker}"
    )
    if onDone:
        onDone(value)
    return {"type": "text", "value": value, "marker": marker}


break_cache = {
    "type": "local",
    "name": "break-cache",
    "description": "Generate a DeepSeek-compatible no-op cache breaker marker",
    "source": "builtin",
    "isHidden": True,
    "call": call,
}

default = break_cache
