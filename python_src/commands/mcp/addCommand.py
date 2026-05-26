"""MCP add subcommand registration shim."""

from __future__ import annotations

from typing import Any

from python_src.cli.handlers.mcp import mcpAddJsonHandler


async def addMcpServer(
    name: str,
    commandOrUrl: str,
    args: list[str] | None = None,
    *,
    transport: str | None = None,
    scope: str = "local",
    env: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    transport = transport or ("http" if commandOrUrl.startswith(("http://", "https://")) else "stdio")
    if transport in {"http", "sse"}:
        config: dict[str, Any] = {"type": transport, "url": commandOrUrl}
        if headers:
            config["headers"] = headers
    else:
        config = {"type": "stdio", "command": commandOrUrl, "args": list(args or [])}
        if env:
            config["env"] = dict(env)
    return await mcpAddJsonHandler(name, config, {"scope": scope})


def registerMcpAddCommand(mcp: Any) -> dict[str, Any]:
    """Register metadata on a lightweight command object when possible.

    The Python migration does not depend on Commander.js, so this returns a
    structured descriptor and appends it to simple list-like registries.
    """

    descriptor = {
        "name": "add",
        "description": "Add a local MCP server to DeepSeek Code configuration",
        "handler": addMcpServer,
    }
    if isinstance(mcp, list):
        mcp.append(descriptor)
    elif isinstance(mcp, dict):
        mcp.setdefault("subcommands", []).append(descriptor)
    return descriptor
