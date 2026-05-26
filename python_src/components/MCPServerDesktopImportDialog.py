from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def MCPServerDesktopImportDialog(*args: Any, **kwargs: Any) -> Any:
    servers = normalize_items(option(args, kwargs, "servers", scalar_arg(args, [])), text_key="name")
    return component_payload("mcp_server_desktop_import_dialog", servers=servers, count=len(servers), imported=bool(option(args, kwargs, "imported", False)))


__all__ = ["MCPServerDesktopImportDialog"]
