"""Command metadata for `/plugin`."""

from __future__ import annotations

from typing import Any

from python_src.commands.plugin.plugin import local_call


plugin: dict[str, Any] = {
    "type": "local-jsx",
    "name": "plugin",
    "description": "Manage local DeepSeek plugins and marketplaces",
    "availability": ["deepseek", "console"],
    "source": "builtin",
    "supportsNonInteractive": False,
    "call": local_call,
}

call = local_call
default = plugin

__all__ = ["call", "default", "plugin"]
