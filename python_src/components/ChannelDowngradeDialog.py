from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def ChannelDowngradeDialog(*args: Any, **kwargs: Any) -> Any:
    current = str(option(args, kwargs, "current", option(args, kwargs, "currentChannel", "beta")))
    target = str(option(args, kwargs, "target", option(args, kwargs, "targetChannel", "stable")))
    return component_payload("channel_downgrade_dialog", currentChannel=current, targetChannel=target, requiresRestart=current != target)


__all__ = ["ChannelDowngradeDialog"]
