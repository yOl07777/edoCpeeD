"""Local MCP command shim."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable


def _load_impl():
    path = Path(__file__).with_name("mcp.py")
    spec = importlib.util.spec_from_file_location("deepseek_mcp_impl", path)
    if not spec or not spec.loader:
        raise ImportError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    return await _load_impl().call(onDone, context, args)


mcp = {
    "type": "local",
    "name": "mcp",
    "description": "Manage local MCP server configuration",
    "immediate": True,
    "argumentHint": "[enable|disable|reconnect [server-name]]",
    "source": "builtin",
    "supportsNonInteractive": True,
    "call": call,
}

default = mcp
