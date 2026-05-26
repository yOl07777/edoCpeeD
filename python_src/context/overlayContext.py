from __future__ import annotations

from typing import Any


_OVERLAYS: dict[str, dict[str, Any]] = {}


async def useRegisterOverlay(name: Any = "overlay", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    overlay_id = str(kwargs.get("id") or name or "overlay")
    active = bool(kwargs.get("active", True))
    modal = bool(kwargs.get("modal", False))
    if kwargs.get("unregister"):
        _OVERLAYS.pop(overlay_id, None)
    else:
        _OVERLAYS[overlay_id] = {"id": overlay_id, "active": active, "modal": modal}
    return {"provider": "deepseek", "overlay": _OVERLAYS.get(overlay_id), "overlays": list(_OVERLAYS.values())}


async def useIsOverlayActive(*_args: Any, **_kwargs: Any) -> bool:
    return any(item.get("active") for item in _OVERLAYS.values())


async def useIsModalOverlayActive(*_args: Any, **_kwargs: Any) -> bool:
    return any(item.get("active") and item.get("modal") for item in _OVERLAYS.values())


__all__ = ["useIsModalOverlayActive", "useIsOverlayActive", "useRegisterOverlay"]
