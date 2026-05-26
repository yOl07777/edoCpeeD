from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option


async def DevBar(*args: Any, **kwargs: Any) -> Any:
    flags = normalize_items(option(args, kwargs, "flags", []), text_key="name")
    return component_payload(
        "dev_bar",
        enabled=bool(option(args, kwargs, "enabled", True)),
        model=str(option(args, kwargs, "model", "deepseek-chat")),
        flags=flags,
        text=f"DeepSeek Code dev mode: {len(flags)} flags",
    )


__all__ = ["DevBar"]
