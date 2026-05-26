"""Internal local logging helpers."""

from __future__ import annotations

import os
import socket
import time
from typing import Any

_PERMISSION_CONTEXT_LOG: list[dict[str, Any]] = []


async def getContainerId() -> str:
    return os.getenv("HOSTNAME") or socket.gethostname()


async def logPermissionContextForAnts(context: dict[str, Any] | None = None, **metadata: Any) -> dict[str, Any]:
    entry = {
        "container_id": await getContainerId(),
        "context": context or {},
        "metadata": metadata,
        "timestamp": time.time(),
    }
    _PERMISSION_CONTEXT_LOG.append(entry)
    return entry


async def getPermissionContextLog() -> list[dict[str, Any]]:
    return list(_PERMISSION_CONTEXT_LOG)
