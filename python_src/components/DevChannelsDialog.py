from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option


async def DevChannelsDialog(*args: Any, **kwargs: Any) -> Any:
    current = str(option(args, kwargs, "current", option(args, kwargs, "channel", "stable")))
    channels = normalize_items(option(args, kwargs, "channels", ["stable", "beta", "nightly"]), text_key="name")
    for channel in channels:
        channel["selected"] = channel["name"] == current
    return component_payload("dev_channels_dialog", current=current, channels=channels, count=len(channels))


__all__ = ["DevChannelsDialog"]
