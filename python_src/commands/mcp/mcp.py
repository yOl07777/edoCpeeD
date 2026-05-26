"""Local MCP command implementation for the Python migration."""

from __future__ import annotations

from typing import Any, Callable

from python_src.cli.handlers.mcp import mcpGetHandler, mcpListHandler


def _format_servers(servers: list[dict[str, Any]]) -> str:
    if not servers:
        return "No MCP servers configured."
    lines = ["Configured MCP servers:"]
    for server in servers:
        name = server.get("name", "unknown")
        status = server.get("status", "unknown")
        target = server.get("url") or server.get("command") or "(missing target)"
        lines.append(f"- {name}: {status} ({target})")
    return "\n".join(lines)


async def _toggle_server(name: str, disabled: bool) -> dict[str, Any]:
    from python_src.cli.handlers import mcp as mcp_handlers

    config = mcp_handlers._read_config()
    servers = config.setdefault("servers", {})
    changed: list[str] = []
    targets = list(servers) if name == "all" else [name]
    for target in targets:
        server = servers.get(target)
        if isinstance(server, dict):
            server["disabled"] = disabled
            changed.append(target)
    mcp_handlers._write_config(config)
    return {"changed": changed, "disabled": disabled}


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    parts = args.strip().split() if args else []
    command = parts[0].lower() if parts else "list"
    if command in {"list", "status", "no-redirect"}:
        listed = await mcpListHandler()
        value = _format_servers(listed["servers"])
        result = {"type": "mcp", "value": value, "action": "list", **listed}
    elif command in {"enable", "disable"}:
        target = " ".join(parts[1:]).strip() or "all"
        toggle = await _toggle_server(target, command == "disable")
        listed = await mcpListHandler()
        value = f"{command.title()}d {len(toggle['changed'])} MCP server(s)."
        result = {"type": "mcp", "value": value, "action": command, "target": target, "toggle": toggle, **listed}
    elif command == "reconnect" and len(parts) > 1:
        target = " ".join(parts[1:]).strip()
        server = await mcpGetHandler(target)
        value = (
            f"Reconnect requested for MCP server {target}. Restart the DeepSeek Code session to reconnect."
            if server
            else f'MCP server "{target}" not found.'
        )
        result = {"type": "mcp", "value": value, "action": "reconnect", "server": server}
    else:
        value = "Usage: /mcp [list|status|enable [server]|disable [server]|reconnect <server>]"
        result = {"type": "mcp", "value": value, "action": "help"}
    if onDone:
        onDone(result["value"])
    return result
