from __future__ import annotations

from typing import Any


def mcp_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def normalize_server(server: Any, index: int = 0) -> dict[str, Any]:
    if isinstance(server, dict):
        name = server.get("name") or server.get("id") or f"server-{index}"
        status = server.get("status") or ("enabled" if server.get("enabled", True) else "disabled")
        transport = server.get("transport") or ("stdio" if server.get("command") else "remote")
        tools = server.get("tools") or []
    else:
        name = str(server)
        status = "enabled"
        transport = "stdio"
        tools = []
    return {
        "index": index,
        "name": str(name),
        "status": str(status),
        "transport": str(transport),
        "tools": [normalize_tool(tool, tool_index) for tool_index, tool in enumerate(tools)],
    }


def normalize_tool(tool: Any, index: int = 0) -> dict[str, Any]:
    if isinstance(tool, dict):
        name = tool.get("name") or tool.get("id") or f"tool-{index}"
        description = tool.get("description") or ""
        schema = tool.get("inputSchema") or tool.get("schema") or tool.get("parameters") or {}
    else:
        name = str(tool)
        description = ""
        schema = {}
    return {"index": index, "name": str(name), "description": str(description), "schema": schema}

