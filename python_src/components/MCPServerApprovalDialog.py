from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, normalize_items, option, scalar_arg


async def MCPServerApprovalDialog(*args: Any, **kwargs: Any) -> Any:
    server = option(args, kwargs, "server", scalar_arg(args, first_options(args)))
    tools = normalize_items(option(args, kwargs, "tools", server.get("tools", []) if isinstance(server, dict) else []), text_key="name")
    name = str(server.get("name", "mcp-server")) if isinstance(server, dict) else str(server or "mcp-server")
    return component_payload("mcp_server_approval_dialog", server=name, tools=tools, approved=bool(option(args, kwargs, "approved", False)))


__all__ = ["MCPServerApprovalDialog"]
