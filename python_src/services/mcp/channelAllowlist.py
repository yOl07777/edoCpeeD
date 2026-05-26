"""MCP channel allowlist helpers."""

from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Any


def _split(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.replace(";", ",").split(",") if item.strip()]


async def getChannelAllowlist(config: dict[str, Any] | None = None) -> list[str]:
    """Return channel names allowed for MCP notifications."""

    config = config or {}
    value = config.get("channelAllowlist") or config.get("allowedChannels")
    if isinstance(value, str):
        return _split(value)
    if isinstance(value, Iterable):
        return [str(item) for item in value if str(item).strip()]
    return _split(os.getenv("MCP_CHANNEL_ALLOWLIST") or os.getenv("DEEPSEEK_MCP_CHANNEL_ALLOWLIST"))


async def isChannelAllowlisted(channel: str, allowlist: Iterable[str] | None = None) -> bool:
    """Return true when a channel is accepted by the allowlist."""

    allowed = list(allowlist) if allowlist is not None else await getChannelAllowlist()
    if not allowed:
        return True
    lowered = {item.lower() for item in allowed}
    return "*" in lowered or str(channel or "").lower() in lowered


async def isChannelsEnabled(config: dict[str, Any] | None = None) -> bool:
    """Return whether MCP channel notifications should be considered enabled."""

    config = config or {}
    if "channelsEnabled" in config:
        return bool(config["channelsEnabled"])
    value = os.getenv("MCP_CHANNELS_ENABLED") or os.getenv("DEEPSEEK_MCP_CHANNELS_ENABLED")
    return str(value).lower() in {"1", "true", "yes", "on"} if value is not None else False
