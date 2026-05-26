"""MCP server approval helpers for local configuration."""

from __future__ import annotations

from typing import Any


def _server_name(server: Any) -> str:
    if isinstance(server, dict):
        return str(server.get("name") or server.get("id") or server.get("serverName") or "")
    return str(server or "")


async def handleMcpjsonServerApprovals(
    servers: list[dict[str, Any]] | dict[str, Any] | None,
    policy: str = "ask",
    approved: list[str] | None = None,
    denied: list[str] | None = None,
) -> dict[str, Any]:
    """Apply local MCP server approval policy.

    ``policy`` accepts ``allow``, ``deny``, or ``ask``. In ``ask`` mode, names
    present in ``approved`` are allowed and names in ``denied`` are rejected;
    everything else is returned as pending.
    """

    if servers is None:
        items: list[dict[str, Any]] = []
    elif isinstance(servers, dict):
        items = [
            {"name": name, **(value if isinstance(value, dict) else {"config": value})}
            for name, value in servers.items()
        ]
    else:
        items = list(servers)
    approved_set = {str(item) for item in approved or []}
    denied_set = {str(item) for item in denied or []}
    allowed_servers: list[dict[str, Any]] = []
    denied_servers: list[dict[str, Any]] = []
    pending_servers: list[dict[str, Any]] = []
    for server in items:
        name = _server_name(server)
        if policy == "allow" or name in approved_set:
            allowed_servers.append({**server, "approved": True})
        elif policy == "deny" or name in denied_set or server.get("disabled"):
            denied_servers.append({**server, "approved": False})
        else:
            pending_servers.append({**server, "approved": None})
    return {"allowed": allowed_servers, "denied": denied_servers, "pending": pending_servers}
