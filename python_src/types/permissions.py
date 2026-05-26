from __future__ import annotations

EXTERNAL_PERMISSION_MODES = ("acceptEdits", "bypassPermissions", "default", "dontAsk", "plan")
INTERNAL_PERMISSION_MODES = EXTERNAL_PERMISSION_MODES + ("auto",)
PERMISSION_MODES = INTERNAL_PERMISSION_MODES

PERMISSION_BEHAVIORS = ("allow", "deny", "ask")
PERMISSION_UPDATE_DESTINATIONS = ("userSettings", "projectSettings", "localSettings", "session", "cliArg")
PERMISSION_RULE_SOURCES = (
    "userSettings",
    "projectSettings",
    "localSettings",
    "flagSettings",
    "policySettings",
    "cliArg",
    "command",
    "session",
)


def isPermissionMode(value: str) -> bool:
    return value in PERMISSION_MODES


def isExternalPermissionMode(value: str) -> bool:
    return value in EXTERNAL_PERMISSION_MODES


__all__ = [
    "EXTERNAL_PERMISSION_MODES",
    "INTERNAL_PERMISSION_MODES",
    "PERMISSION_BEHAVIORS",
    "PERMISSION_MODES",
    "PERMISSION_RULE_SOURCES",
    "PERMISSION_UPDATE_DESTINATIONS",
    "isExternalPermissionMode",
    "isPermissionMode",
]
