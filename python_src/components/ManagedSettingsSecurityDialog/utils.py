from __future__ import annotations

from typing import Any


DANGEROUS_KEYS = {
    "apiKey",
    "api_key",
    "token",
    "secret",
    "password",
    "allowedTools",
    "dangerouslySkipPermissions",
    "disableSandbox",
    "autoApprove",
}


def _flatten(settings: Any, prefix: str = "") -> list[tuple[str, Any]]:
    if isinstance(settings, dict):
        rows: list[tuple[str, Any]] = []
        for key, value in settings.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_flatten(value, path))
        return rows
    return [(prefix, settings)]


async def extractDangerousSettings(*args: Any, **kwargs: Any) -> Any:
    settings = kwargs.get("settings") if "settings" in kwargs else (args[0] if args else {})
    rows = []
    for path, value in _flatten(settings):
        key = path.split(".")[-1]
        lowered = key.lower()
        sensitive = any(marker.lower() in lowered for marker in DANGEROUS_KEYS)
        permission_risk = key in {"allowedTools", "dangerouslySkipPermissions", "disableSandbox", "autoApprove"}
        if sensitive or permission_risk:
            rows.append({"path": path, "value": "***" if sensitive else value, "risk": "secret" if sensitive else "permission"})
    return rows


async def formatDangerousSettingsList(*args: Any, **kwargs: Any) -> Any:
    settings = kwargs.get("settings") if "settings" in kwargs else (args[0] if args else [])
    rows = settings if isinstance(settings, list) else await extractDangerousSettings(settings)
    return "\n".join(f"- {row['path']} ({row['risk']})" for row in rows)


async def hasDangerousSettings(*args: Any, **kwargs: Any) -> Any:
    return len(await extractDangerousSettings(*args, **kwargs)) > 0


async def hasDangerousSettingsChanged(*args: Any, **kwargs: Any) -> Any:
    before = await extractDangerousSettings(kwargs.get("before") if "before" in kwargs else (args[0] if args else {}))
    after = await extractDangerousSettings(kwargs.get("after") if "after" in kwargs else (args[1] if len(args) > 1 else {}))
    before_paths = {row["path"] for row in before}
    after_paths = {row["path"] for row in after}
    return before_paths != after_paths


__all__ = [
    "extractDangerousSettings",
    "formatDangerousSettingsList",
    "hasDangerousSettings",
    "hasDangerousSettingsChanged",
]
