"""MCP channel notification helpers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .channelAllowlist import getChannelAllowlist, isChannelAllowlisted

CHANNEL_PERMISSION_METHOD = "mcp/channel_permission"
CHANNEL_PERMISSION_REQUEST_METHOD = "mcp/channel_permission_request"
ChannelMessageNotificationSchema: dict[str, Any] = {"type": "object"}
ChannelPermissionNotificationSchema: dict[str, Any] = {"type": "object"}


def _entry_name(entry: Any) -> str:
    if isinstance(entry, dict):
        return str(entry.get("channel") or entry.get("name") or entry.get("id") or "")
    return str(entry or "")


async def findChannelEntry(channel: str, entries: Iterable[Any] | None = None) -> Any | None:
    """Find a channel entry by name, accepting wildcard entries."""

    for entry in entries or []:
        name = _entry_name(entry)
        if name == "*" or name.lower() == str(channel or "").lower():
            return entry
    return None


async def gateChannelServer(server: dict[str, Any], allowlist: Iterable[str] | None = None) -> dict[str, Any]:
    """Annotate a server with its channel gating state."""

    channel = str(server.get("channel") or server.get("name") or "")
    permitted = await isChannelAllowlisted(channel, allowlist)
    result = dict(server)
    result["channelAllowed"] = permitted
    return result


async def getEffectiveChannelAllowlist(
    config: dict[str, Any] | None = None,
    enterprise_allowlist: Iterable[str] | None = None,
) -> list[str]:
    """Merge local and enterprise channel allowlists."""

    values = list(enterprise_allowlist or []) + await getChannelAllowlist(config)
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        lowered = str(value).lower()
        if lowered not in seen:
            seen.add(lowered)
            result.append(str(value))
    return result


async def wrapChannelMessage(channel: str, message: Any, method: str | None = None) -> dict[str, Any]:
    """Wrap a notification payload in a stable MCP channel envelope."""

    return {
        "method": method or CHANNEL_PERMISSION_METHOD,
        "params": {
            "channel": channel,
            "message": message,
        },
    }
