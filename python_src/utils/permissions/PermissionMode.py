from __future__ import annotations


PERMISSION_MODES = {"default", "acceptEdits", "plan", "bypassPermissions", "readonly"}
EXTERNAL_PERMISSION_MODES = {"default", "acceptEdits", "plan", "bypassPermissions", "readonly"}

permissionModeSchema = {"enum": sorted(PERMISSION_MODES)}
externalPermissionModeSchema = {"enum": sorted(EXTERNAL_PERMISSION_MODES)}


def _normalize(mode: str | None) -> str:
    raw = (mode or "default").strip()
    aliases = {
        "accept-edits": "acceptEdits",
        "accept_edits": "acceptEdits",
        "auto": "acceptEdits",
        "read-only": "readonly",
        "read_only": "readonly",
        "bypass": "bypassPermissions",
        "dangerously_skip_permissions": "bypassPermissions",
    }
    return aliases.get(raw, raw)


async def permissionModeFromString(mode: str | None) -> str:
    normalized = _normalize(mode)
    if normalized not in PERMISSION_MODES:
        raise ValueError(f"Unknown permission mode: {mode}")
    return normalized


async def isDefaultMode(mode: str | None) -> bool:
    return _normalize(mode) == "default"


async def isExternalPermissionMode(mode: str | None) -> bool:
    return _normalize(mode) in EXTERNAL_PERMISSION_MODES


async def toExternalPermissionMode(mode: str | None) -> str:
    normalized = await permissionModeFromString(mode)
    return normalized


async def permissionModeTitle(mode: str | None) -> str:
    return {
        "default": "Default",
        "acceptEdits": "Accept Edits",
        "plan": "Plan",
        "bypassPermissions": "Bypass Permissions",
        "readonly": "Read Only",
    }[await permissionModeFromString(mode)]


async def permissionModeShortTitle(mode: str | None) -> str:
    return {
        "default": "Default",
        "acceptEdits": "Auto",
        "plan": "Plan",
        "bypassPermissions": "Bypass",
        "readonly": "Read",
    }[await permissionModeFromString(mode)]


async def permissionModeSymbol(mode: str | None) -> str:
    return {
        "default": "?",
        "acceptEdits": "A",
        "plan": "P",
        "bypassPermissions": "!",
        "readonly": "R",
    }[await permissionModeFromString(mode)]


async def getModeColor(mode: str | None) -> str:
    return {
        "default": "yellow",
        "acceptEdits": "green",
        "plan": "cyan",
        "bypassPermissions": "red",
        "readonly": "blue",
    }[await permissionModeFromString(mode)]
