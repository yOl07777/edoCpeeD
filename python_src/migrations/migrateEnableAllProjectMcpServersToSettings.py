from __future__ import annotations

from typing import Any

from ._shared import get_project_config, local_settings, mutate_project_config, update_local_settings


def _missing_items(existing: list[str], incoming: list[str]) -> list[str]:
    seen = set(existing)
    return [value for value in incoming if value not in seen]


async def migrateEnableAllProjectMcpServersToSettings(*_args: Any, **_kwargs: Any) -> bool:
    """Move MCP approval fields from project config into local settings."""

    project = await get_project_config()
    fields = ["enableAllProjectMcpServers", "enabledMcpjsonServers", "disabledMcpjsonServers"]
    if not any(key in project and project.get(key) not in (None, []) for key in fields):
        return False

    existing = await local_settings()
    updates: dict[str, Any] = {}
    if "enableAllProjectMcpServers" in project and "enableAllProjectMcpServers" not in existing:
        updates["enableAllProjectMcpServers"] = bool(project.get("enableAllProjectMcpServers"))
    if project.get("enabledMcpjsonServers"):
        missing = _missing_items(
            list(existing.get("enabledMcpjsonServers") or []),
            list(project.get("enabledMcpjsonServers") or []),
        )
        if missing:
            updates["enabledMcpjsonServers"] = missing
    if project.get("disabledMcpjsonServers"):
        missing = _missing_items(
            list(existing.get("disabledMcpjsonServers") or []),
            list(project.get("disabledMcpjsonServers") or []),
        )
        if missing:
            updates["disabledMcpjsonServers"] = missing
    if updates:
        await update_local_settings(updates)

    def remove_fields(current: dict[str, Any]) -> dict[str, Any]:
        next_config = dict(current)
        for key in fields:
            next_config.pop(key, None)
        return next_config

    await mutate_project_config(remove_fields)
    return True
