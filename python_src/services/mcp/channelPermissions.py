"""Permission relay helpers for MCP channel requests."""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from typing import Any, Awaitable, Callable

PERMISSION_REPLY_RE = re.compile(r"permission[_-]?reply[:#]?(?P<id>[A-Za-z0-9_.:-]+)?", re.I)


async def createChannelPermissionCallbacks(
    allow: Callable[[dict[str, Any]], Any] | None = None,
    deny: Callable[[dict[str, Any]], Any] | None = None,
) -> dict[str, Callable[[dict[str, Any]], Any]]:
    """Create simple allow/deny callbacks for channel permission flows."""

    async def default_allow(request: dict[str, Any]) -> dict[str, Any]:
        return {"allowed": True, "request": request}

    async def default_deny(request: dict[str, Any]) -> dict[str, Any]:
        return {"allowed": False, "request": request}

    return {"allow": allow or default_allow, "deny": deny or default_deny}


async def filterPermissionRelayClients(clients: Iterable[Any]) -> list[Any]:
    """Keep clients that advertise permission relay support."""

    result: list[Any] = []
    for client in clients:
        if isinstance(client, dict):
            enabled = client.get("permissionRelay") or client.get("supportsPermissionRelay")
            if enabled:
                result.append(client)
        elif getattr(client, "permissionRelay", False) or getattr(client, "supportsPermissionRelay", False):
            result.append(client)
    return result


async def isChannelPermissionRelayEnabled(config: dict[str, Any] | None = None) -> bool:
    """Return whether channel permission relay is enabled."""

    config = config or {}
    if "permissionRelay" in config:
        return bool(config["permissionRelay"])
    value = os.getenv("MCP_CHANNEL_PERMISSION_RELAY") or os.getenv("DEEPSEEK_MCP_CHANNEL_PERMISSION_RELAY")
    return str(value).lower() in {"1", "true", "yes", "on"} if value is not None else False


async def shortRequestId(request_id: Any, length: int = 8) -> str:
    """Shorten a request id while keeping it deterministic."""

    value = str(request_id or "")
    return value if len(value) <= length else value[:length]


async def truncateForPreview(value: Any, limit: int = 160) -> str:
    """Truncate long values for readable permission prompts."""

    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)] + "..."
