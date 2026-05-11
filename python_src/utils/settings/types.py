from __future__ import annotations

from typing import Any


CUSTOMIZATION_SURFACES = ["cli", "tools", "model", "permissions", "plugins"]
EnvironmentVariablesSchema = {"type": "object", "additionalProperties": {"type": "string"}}
PermissionsSchema = {"type": "object"}
ExtraKnownMarketplaceSchema = {"type": "object"}
AllowedMcpServerEntrySchema = {"type": "object"}
DeniedMcpServerEntrySchema = {"type": "object"}
SettingsSchema = {
    "type": "object",
    "properties": {
        "model": {"type": "string"},
        "defaultModel": {"type": "string"},
        "provider": {"type": "string"},
        "permissions": PermissionsSchema,
        "env": EnvironmentVariablesSchema,
        "mcpServers": {"type": "object"},
    },
}


async def isMcpServerCommandEntry(entry: Any) -> bool:
    return isinstance(entry, dict) and isinstance(entry.get("command"), str)


async def isMcpServerUrlEntry(entry: Any) -> bool:
    return isinstance(entry, dict) and isinstance(entry.get("url"), str)


async def isMcpServerNameEntry(entry: Any) -> bool:
    return isinstance(entry, str) or (isinstance(entry, dict) and isinstance(entry.get("name"), str))
