from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def MCPServerMultiselectDialog(*args: Any, **kwargs: Any) -> Any:
    selected = set(option(args, kwargs, "selected", []))
    servers = normalize_items(option(args, kwargs, "servers", scalar_arg(args, [])), text_key="name")
    for server in servers:
        server["selected"] = server["name"] in selected
    return component_payload("mcp_server_multiselect_dialog", servers=servers, selected=sorted(selected), count=len(servers))


__all__ = ["MCPServerMultiselectDialog"]
