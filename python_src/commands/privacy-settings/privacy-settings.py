"""Local privacy settings command shim."""

from __future__ import annotations

from typing import Any, Callable

from python_src.services.api.grove import getGroveNoticeConfig, getGroveSettings, isQualifiedForGrove, updateGroveSettings

FALLBACK_MESSAGE = "Review and manage your privacy settings in DeepSeek Code local privacy settings."


def _done(onDone: Callable[..., Any] | None, message: str, options: dict[str, Any] | None = None) -> None:
    if callable(onDone):
        if options is None:
            onDone(message)
        else:
            onDone(message, options)


async def call(onDone: Callable[..., Any] | None = None, _context: Any | None = None, args: str | None = None) -> dict[str, Any] | None:
    trimmed = (args or "").strip().lower()
    if trimmed in {"on", "enable", "true"}:
        settings = await updateGroveSettings({"enabled": True, "grove_enabled": True})
        _done(onDone, '"Help improve DeepSeek Code" set to true.')
        return {"type": "privacy_settings", "enabled": True, "settings": settings}
    if trimmed in {"off", "disable", "false"}:
        settings = await updateGroveSettings({"enabled": False, "grove_enabled": False})
        _done(onDone, '"Help improve DeepSeek Code" set to false.')
        return {"type": "privacy_settings", "enabled": False, "settings": settings}

    qualified = await isQualifiedForGrove()
    settings = await getGroveSettings()
    config = await getGroveNoticeConfig()
    if not qualified and not trimmed:
        _done(onDone, FALLBACK_MESSAGE)
        return None
    return {
        "type": "privacy_settings",
        "qualified": qualified,
        "settings": settings,
        "config": config,
        "message": FALLBACK_MESSAGE if not qualified else "Privacy settings are available.",
    }
