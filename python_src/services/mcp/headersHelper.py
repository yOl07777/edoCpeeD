"""Header helpers for MCP server configuration."""

from __future__ import annotations

import os
from typing import Any

from .envExpansion import expandEnvVarsInString
from .utils import parseHeaders


async def getMcpHeadersFromHelper(helper: Any, env: dict[str, str] | None = None) -> dict[str, str]:
    """Resolve headers from a dict, list of pairs, or raw header string."""

    if helper is None:
        return {}
    if callable(helper):
        helper = helper()
    if isinstance(helper, dict):
        return {str(k): await expandEnvVarsInString(str(v), env) for k, v in helper.items() if v is not None}
    if isinstance(helper, (list, tuple)):
        headers: dict[str, str] = {}
        for item in helper:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                headers[str(item[0])] = await expandEnvVarsInString(str(item[1]), env)
            elif isinstance(item, str):
                headers.update(await parseHeaders(item))
        return headers
    return await parseHeaders(await expandEnvVarsInString(str(helper), env or os.environ))


async def getMcpServerHeaders(server: dict[str, Any], env: dict[str, str] | None = None) -> dict[str, str]:
    """Return merged headers from MCP server config fields."""

    headers: dict[str, str] = {}
    headers.update(await getMcpHeadersFromHelper(server.get("headers"), env))
    headers.update(await getMcpHeadersFromHelper(server.get("headersHelper"), env))
    return headers
