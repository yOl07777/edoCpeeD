"""Reload local plugin metadata for the current Python session."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


def _plugin_roots(cwd: str | None = None) -> list[Path]:
    root = Path(cwd or Path.cwd())
    return [root / ".deepseek" / "plugins", root / ".agents" / "plugins", root / ".codex" / "plugins"]


def discoverLocalPlugins(cwd: str | None = None) -> list[dict[str, Any]]:
    plugins: list[dict[str, Any]] = []
    for root in _plugin_roots(cwd):
        if not root.exists():
            continue
        for manifest in sorted(root.rglob("plugin.json")):
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
            except Exception as exc:
                data = {"name": manifest.parent.name, "error": str(exc)}
            plugins.append({"name": data.get("name", manifest.parent.name), "path": str(manifest), "manifest": data})
    return plugins


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    cwd = context.get("cwd") if isinstance(context, dict) else None
    plugins = discoverLocalPlugins(cwd)
    value = f"Reloaded local plugin metadata: {len(plugins)} plugin(s) discovered."
    if onDone:
        onDone(value)
    return {
        "type": "reload_plugins",
        "value": value,
        "commands": [],
        "agents": [],
        "plugins": plugins,
        "mcpServers": [],
    }


reload_plugins = {
    "type": "local",
    "name": "reload-plugins",
    "description": "Activate pending local plugin metadata changes in the current session",
    "source": "builtin",
    "supportsNonInteractive": False,
    "call": call,
}

default = reload_plugins
