"""Local Grove notice/settings compatibility layer."""

from __future__ import annotations

from typing import Any

_SETTINGS: dict[str, Any] = {"enabled": False, "noticeViewed": False}


async def getGroveSettings() -> dict[str, Any]:
    return dict(_SETTINGS)


async def getGroveNoticeConfig() -> dict[str, Any]:
    return {"enabled": bool(_SETTINGS.get("enabled")), "message": _SETTINGS.get("message", "")}


async def updateGroveSettings(settings: dict[str, Any]) -> dict[str, Any]:
    _SETTINGS.update(settings)
    return await getGroveSettings()


async def markGroveNoticeViewed() -> dict[str, Any]:
    _SETTINGS["noticeViewed"] = True
    return await getGroveSettings()


async def isQualifiedForGrove(user: dict[str, Any] | None = None, settings: dict[str, Any] | None = None) -> bool:
    merged = {**_SETTINGS, **(settings or {})}
    if not merged.get("enabled"):
        return False
    if user and user.get("disabled"):
        return False
    return True


async def calculateShouldShowGrove(user: dict[str, Any] | None = None, settings: dict[str, Any] | None = None) -> bool:
    merged = {**_SETTINGS, **(settings or {})}
    return await isQualifiedForGrove(user, merged) and not bool(merged.get("noticeViewed"))


async def checkGroveForNonInteractive(user: dict[str, Any] | None = None) -> dict[str, Any]:
    should_show = await calculateShouldShowGrove(user)
    return {"shouldShow": should_show, "settings": await getGroveSettings()}

