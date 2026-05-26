from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import logo_payload, notice_text, option, scalar_arg


async def ChannelsNotice(*args: Any, **kwargs: Any) -> Any:
    channel = str(option(args, kwargs, "channel", option(args, kwargs, "currentChannel", scalar_arg(args, "stable"))))
    text = notice_text(args, kwargs, f"Using DeepSeek Code {channel} channel.")
    return logo_payload("channels_notice", channel=channel, text=text, visible=bool(option(args, kwargs, "visible", True)))


__all__ = ["ChannelsNotice"]
