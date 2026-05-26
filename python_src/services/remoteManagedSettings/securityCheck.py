"""Security checks for remote managed settings."""

from __future__ import annotations

from typing import Any

SecurityCheckResult = str

_DANGEROUS_KEYS = {
    "apiKey",
    "api_key",
    "anthropicApiKey",
    "deepseekApiKey",
    "oauthToken",
    "accessToken",
    "permissions",
    "allowedTools",
    "disabledTools",
    "mcpServers",
    "hooks",
}


def _dangerous(settings: Any, prefix: str = "") -> dict[str, Any]:
    found: dict[str, Any] = {}
    if not isinstance(settings, dict):
        return found
    for key, value in settings.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if str(key) in _DANGEROUS_KEYS or any(part in str(key).lower() for part in ("token", "secret", "password")):
            found[path] = value
        if isinstance(value, dict):
            found.update(_dangerous(value, path))
    return found


async def checkManagedSettingsSecurity(*args: Any, **kwargs: Any) -> SecurityCheckResult:
    cachedSettings = kwargs.get("cachedSettings") if "cachedSettings" in kwargs else (args[0] if args else None)
    newSettings = kwargs.get("newSettings") if "newSettings" in kwargs else (args[1] if len(args) > 1 else None)
    dangerous = _dangerous(newSettings)
    if not dangerous:
        return "no_check_needed"
    if _dangerous(cachedSettings) == dangerous:
        return "no_check_needed"
    return str(kwargs.get("defaultResult") or "approved")


async def handleSecurityCheckResult(*args: Any, **kwargs: Any) -> bool:
    result = str(kwargs.get("result") or (args[0] if args else "no_check_needed"))
    return result != "rejected"


__all__ = ["SecurityCheckResult", "checkManagedSettingsSecurity", "handleSecurityCheckResult"]
