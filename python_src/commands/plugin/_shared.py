"""Shared local plugin command helpers."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from python_src.cli.handlers import plugins as plugin_handlers


PLUGIN_HELP = """Plugin commands:
  /plugin                     Show installed plugins and marketplaces
  /plugin install <name>      Record a local plugin installation
  /plugin uninstall <name>    Remove a local plugin
  /plugin enable <name>       Enable a local plugin
  /plugin disable <name>      Disable a local plugin
  /plugin validate <path>     Validate a plugin manifest
  /plugin marketplace list
  /plugin marketplace add <source>
  /plugin marketplace remove <name>
  /plugin marketplace update [name]
"""


def read_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Plugin manifest must be a JSON object")
    return data


def plugin_summary(name: str, info: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "source": info.get("source", name),
        "scope": info.get("scope", "user"),
        "version": info.get("version", "local"),
        "enabled": bool(info.get("enabled", True)),
        "updated": bool(info.get("updated", False)),
    }


async def list_plugins() -> dict[str, Any]:
    result = await plugin_handlers.pluginListHandler({})
    plugins = result.get("plugins", {})
    return {
        **result,
        "items": [plugin_summary(name, info) for name, info in sorted(plugins.items())],
    }


async def list_marketplaces() -> dict[str, Any]:
    result = await plugin_handlers.marketplaceListHandler({})
    marketplaces = result.get("marketplaces", {})
    return {
        **result,
        "items": [
            {"name": name, **(info if isinstance(info, dict) else {"source": info})}
            for name, info in sorted(marketplaces.items())
        ],
    }


def extract_github_repo(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"github\.com[:/]([^/\s]+/[^/\s#?]+)", value)
    if not match:
        return None
    return match.group(1).removesuffix(".git")


def paginate(items: list[Any], *, page: int = 1, per_page: int = 10) -> dict[str, Any]:
    page = max(1, page)
    per_page = max(1, per_page)
    total_pages = max(1, math.ceil(len(items) / per_page))
    start = (page - 1) * per_page
    return {
        "items": items[start : start + per_page],
        "page": page,
        "perPage": per_page,
        "total": len(items),
        "totalPages": total_pages,
        "hasNext": page < total_pages,
        "hasPrevious": page > 1,
    }


def command_result(value: str, **extra: Any) -> dict[str, Any]:
    return {"type": "plugin", "provider": "deepseek", "value": value, **extra}


__all__ = [
    "PLUGIN_HELP",
    "command_result",
    "extract_github_repo",
    "list_marketplaces",
    "list_plugins",
    "paginate",
    "plugin_summary",
    "read_manifest",
]
